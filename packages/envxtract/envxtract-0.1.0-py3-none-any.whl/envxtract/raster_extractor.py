#!/usr/bin/env python3
"""
Advanced Raster Extraction Tool
===============================
Extract statistics from raster data using polygon or point geometries.
Supports batch processing, flexible statistics, and multiple file formats.

Usage:
    # CLI
    python raster_extractor.py --config config.yaml --output results/
    
    # Programmatic
    from raster_extractor import RasterExtractor
    processor = RasterExtractor(config_file="config.yaml")
    results = processor.run()
"""

import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.sample import sample_gen
import numpy as np
import pandas as pd
from shapely.geometry import mapping, Point
import os
import logging
import json
import yaml
import argparse
import glob
import re
from pathlib import Path
from typing import Dict, List, Union, Optional, Tuple, Any
from dataclasses import dataclass, field
import warnings
warnings.filterwarnings('ignore', category=UserWarning)


@dataclass
class ProcessingConfig:
    """Configuration for raster extraction processing"""
    # Input/Output paths
    raster_files: List[str] = field(default_factory=list)
    boundary_files: List[str] = field(default_factory=list)
    raster_dir: Optional[str] = None  # Directory to search for rasters
    boundary_dir: Optional[str] = None  # Directory to search for boundaries
    raster_pattern: Optional[str] = None  # Pattern like "*.tif" or "*NO2*.tif"
    boundary_pattern: Optional[str] = None  # Pattern like "*.shp" or "*nuts*.shp"
    output_dir: str = "extraction_results"
    output_prefix: str = "extraction"  # Prefix for output files
    
    # Geometry filtering
    process_polygons: bool = True
    process_points: bool = True
    geometry_types_allowed: List[str] = field(default_factory=lambda: ['Point', 'Polygon', 'MultiPolygon'])
    
    # Geometry field settings
    geometry_id_field: Optional[str] = None  # Auto-detect if None
    geometry_name_field: Optional[str] = None  # Auto-detect if None
    coordinate_fields: Dict[str, List[str]] = field(default_factory=lambda: {
        'x': ['x', 'lon', 'lng', 'longitude', 'long', 'x_coord'],
        'y': ['y', 'lat', 'latitude', 'y_coord']
    })
    
    # CRS settings
    target_crs: Optional[str] = None  # Auto-detect from raster if None
    geometry_crs: Optional[str] = None  # Auto-detect from file if None
    force_crs_match: bool = True  # Force geometries to match raster CRS
    
    # Statistics configuration
    statistics: Dict[str, Any] = field(default_factory=lambda: {
        'basic': ['mean', 'median', 'min', 'max', 'std', 'count'],
        'percentiles': [25, 75, 90, 95],
        'custom': ['coverage_percent']
    })
    single_statistic: Optional[str] = None  # If set, only compute this statistic
    
    # Processing options
    all_touched: bool = True
    nodata_value: Optional[float] = None
    buffer_distance: float = 0.0  # Buffer for point geometries (meters)
    max_points_per_chunk: int = 1000  # For large point datasets
    skip_existing: bool = False  # Skip if output file already exists
    
    # Filtering options
    min_valid_pixels: int = 1  # Minimum valid pixels required
    max_coverage_percent: float = 100.0  # Maximum coverage percentage filter
    min_coverage_percent: float = 0.0  # Minimum coverage percentage filter
    
    # Output options
    save_csv: bool = True
    save_geojson: bool = False
    save_shapefile: bool = False
    save_excel: bool = False
    include_geometry: bool = False  # Include geometry in outputs
    separate_files_per_raster: bool = False  # Create separate output per raster
    
    # Naming options
    use_raster_names_in_columns: bool = True
    column_name_separator: str = "_"
    remove_file_extensions: bool = True
    
    # Logging and progress
    log_level: str = "INFO"
    progress_interval: int = 100
    log_to_file: bool = False
    log_file: Optional[str] = None


class GeometryHandler:
    """Handles both point and polygon geometries with auto-detection"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def load_geometries(self, file_path: str) -> gpd.GeoDataFrame:
        """Load geometries from various file formats with auto-detection"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Geometry file not found: {file_path}")
        
        try:
            if file_path.suffix.lower() == '.csv':
                gdf = self._load_csv_points(file_path)
            elif file_path.suffix.lower() == '.json':
                gdf = self._load_json_points(file_path)
            elif file_path.suffix.lower() in ['.shp', '.geojson']:
                gdf = gpd.read_file(file_path)
            else:
                # Try as shapefile first, then as text
                try:
                    gdf = gpd.read_file(file_path)
                except:
                    gdf = self._load_csv_points(file_path)
            
            # Ensure there's always an index column available for ID field detection
            if 'index' not in gdf.columns:
                gdf['index'] = range(len(gdf))
            
            return gdf
        
        except Exception as e:
            self.logger.error(f"Error loading geometry file {file_path}: {e}")
            raise
    
    def _load_csv_points(self, file_path: Path) -> gpd.GeoDataFrame:
        """Load points from CSV with flexible column detection"""
        df = pd.read_csv(file_path)
        
        # Detect coordinate columns
        x_col, y_col = self._detect_coordinate_columns(df.columns)
        
        if not x_col or not y_col:
            raise ValueError(f"Could not detect coordinate columns in {file_path}")
        
        self.logger.info(f"Using coordinates: {x_col}, {y_col}")
        
        # Create geometry
        geometry = [Point(xy) for xy in zip(df[x_col], df[y_col])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry)
        
        # Set CRS (assume WGS84 if not specified)
        crs = self.config.geometry_crs or "EPSG:4326"
        gdf.set_crs(crs, inplace=True, allow_override=True)
        
        return gdf
    
    def _load_json_points(self, file_path: Path) -> gpd.GeoDataFrame:
        """Load points from JSON with flexible structure detection"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, dict):
            if 'features' in data:  # GeoJSON
                return gpd.read_file(file_path)
            else:  # Simple dict format
                df = pd.DataFrame([data])
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            raise ValueError(f"Unsupported JSON structure in {file_path}")
        
        return self._load_csv_points(df)  # Reuse CSV logic
    
    def _detect_coordinate_columns(self, columns) -> Tuple[Optional[str], Optional[str]]:
        """Auto-detect coordinate column names"""
        columns_lower = [col.lower() for col in columns]
        
        x_col = None
        y_col = None
        
        # Find X coordinate
        for x_name in self.config.coordinate_fields['x']:
            if x_name.lower() in columns_lower:
                x_col = columns[columns_lower.index(x_name.lower())]
                break
        
        # Find Y coordinate
        for y_name in self.config.coordinate_fields['y']:
            if y_name.lower() in columns_lower:
                y_col = columns[columns_lower.index(y_name.lower())]
                break        
        return x_col, y_col
    
    def detect_id_field(self, gdf: gpd.GeoDataFrame) -> str:
        """Auto-detect ID field"""
        if self.config.geometry_id_field and self.config.geometry_id_field in gdf.columns:
            return self.config.geometry_id_field
        
        # Common ID field patterns
        id_patterns = ['id', 'objectid', 'fid', 'gid', 'nuts_id', 'admin_id', 'region_id']
        
        for col in gdf.columns:
            if col.lower() in id_patterns:
                return col
        
        # Use index if no ID field found (should be available from load_geometries)
        if 'index' in gdf.columns:
            return 'index'
        else:
            # This shouldn't happen with the updated load_geometries method,
            # but just in case, create the index column
            self.logger.warning("No index column found, creating one...")
            return 'index'
    
    def detect_name_field(self, gdf: gpd.GeoDataFrame) -> Optional[str]:
        """Auto-detect name field"""
        if self.config.geometry_name_field and self.config.geometry_name_field in gdf.columns:
            return self.config.geometry_name_field
        
        # Common name field patterns
        name_patterns = ['name', 'name_latn', 'region_name', 'admin_name', 'label']
        
        for col in gdf.columns:
            if col.lower() in name_patterns:
                return col
        
        return None


class StatisticsEngine:
    """Flexible statistics calculation engine"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Define available statistics functions
        self.stat_functions = {
            'mean': np.mean,
            'median': np.median,
            'min': np.min,
            'max': np.max,
            'std': np.std,
            'count': len,
            'sum': np.sum,
            'var': np.var
        }
    
    def calculate_statistics(self, data: np.ndarray) -> Dict[str, float]:
        """Calculate all requested statistics for valid data"""
        if len(data) == 0:
            return {stat: np.nan for stat in self._get_all_stat_names()}
        
        results = {}
        
        # If single statistic is specified, only calculate that
        if self.config.single_statistic:
            stat_name = self.config.single_statistic
            if stat_name in self.stat_functions:
                try:
                    results[stat_name] = float(self.stat_functions[stat_name](data))
                except:
                    results[stat_name] = np.nan
            elif stat_name.startswith('p') and stat_name[1:].isdigit():
                # Handle percentile (e.g., 'p90')
                percentile = int(stat_name[1:])
                try:
                    results[stat_name] = float(np.percentile(data, percentile))
                except:
                    results[stat_name] = np.nan
            elif stat_name == 'coverage_percent':
                # This will be calculated at extraction level
                results[stat_name] = np.nan
            else:
                self.logger.warning(f"Unknown statistic: {stat_name}")
                results[stat_name] = np.nan
            
            return results
        
        # Calculate multiple statistics
        # Basic statistics
        for stat_name in self.config.statistics.get('basic', []):
            if stat_name in self.stat_functions:
                try:
                    results[stat_name] = float(self.stat_functions[stat_name](data))
                except:
                    results[stat_name] = np.nan
        
        # Percentiles
        for percentile in self.config.statistics.get('percentiles', []):
            try:
                results[f'p{percentile}'] = float(np.percentile(data, percentile))
            except:
                results[f'p{percentile}'] = np.nan
        
        # Custom statistics
        for custom_stat in self.config.statistics.get('custom', []):
            if custom_stat == 'coverage_percent':
                # This will be calculated at extraction level
                results[custom_stat] = np.nan
        
        return results
    
    def _get_all_stat_names(self) -> List[str]:
        """Get list of all statistic names that will be calculated"""
        if self.config.single_statistic:
            return [self.config.single_statistic]
        
        names = list(self.config.statistics.get('basic', []))
        names.extend([f'p{p}' for p in self.config.statistics.get('percentiles', [])])
        names.extend(self.config.statistics.get('custom', []))
        return names


class RasterExtractor:
    """Main class for raster data extraction"""
    
    def __init__(self, config_file: Optional[str] = None, config_dict: Optional[Dict] = None, **kwargs):
        """
        Initialize RasterExtractor
        
        Args:
            config_file: Path to YAML/JSON config file
            config_dict: Configuration dictionary
            **kwargs: Runtime parameter overrides
        """
        self.config = self._load_config(config_file, config_dict, kwargs)
        self._setup_logging()
        
        self.geometry_handler = GeometryHandler(self.config)
        self.stats_engine = StatisticsEngine(self.config)
        
        self.logger = logging.getLogger(__name__)
        self.results_cache = {}
    
    def _load_config(self, config_file: Optional[str], config_dict: Optional[Dict], overrides: Dict) -> ProcessingConfig:
        """Load and merge configuration from multiple sources"""
        # Start with defaults
        config_data = {}
        
        # Load from file
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
        
        # Merge with dictionary
        if config_dict:
            config_data.update(config_dict)
        
        # Apply runtime overrides
        config_data.update(overrides)
        
        return ProcessingConfig(**config_data)
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def run(self) -> Dict[str, Any]:
        """Main execution method - processes all combinations"""
        self.logger.info("Starting raster extraction process")
        
        # Validate inputs
        self._validate_inputs()
        
        # Create output directory
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        # Process all combinations
        all_results = []
        processing_metadata = []
        
        for raster_file in self.config.raster_files:
            for boundary_file in self.config.boundary_files:
                self.logger.info(f"Processing: {os.path.basename(raster_file)} x {os.path.basename(boundary_file)}")
                
                try:
                    result = self._process_single_combination(raster_file, boundary_file)
                    all_results.append(result['data'])
                    processing_metadata.append(result['metadata'])
                    
                except Exception as e:
                    self.logger.error(f"Error processing {raster_file} x {boundary_file}: {e}")
                    continue
        
        # Combine results
        if all_results:
            combined_results = self._combine_results(all_results, processing_metadata)
            
            # Export results
            export_paths = self._export_results(combined_results, processing_metadata)
            
            return {
                'results': combined_results,
                'metadata': processing_metadata,
                'export_paths': export_paths,
                'config': self.config
            }
        else:
            self.logger.warning("No results were successfully processed")
            return {'results': None, 'metadata': [], 'export_paths': [], 'config': self.config}
    
    def _validate_inputs(self):
        """Validate configuration and discover input files"""
        # Discover raster files
        if not self.config.raster_files:
            if self.config.raster_dir and self.config.raster_pattern:
                self.config.raster_files = glob.glob(
                    os.path.join(self.config.raster_dir, self.config.raster_pattern),
                    recursive=True
                )
                self.logger.info(f"Found {len(self.config.raster_files)} raster files using pattern")
            elif self.config.raster_dir:
                # Default pattern for common raster formats
                patterns = ["*.tif", "*.tiff", "*.img", "*.nc"]
                self.config.raster_files = []
                for pattern in patterns:
                    self.config.raster_files.extend(
                        glob.glob(os.path.join(self.config.raster_dir, "**", pattern), recursive=True)
                    )
                self.logger.info(f"Found {len(self.config.raster_files)} raster files in directory")
        
        # Discover boundary files
        if not self.config.boundary_files:
            if self.config.boundary_dir and self.config.boundary_pattern:
                self.config.boundary_files = glob.glob(
                    os.path.join(self.config.boundary_dir, self.config.boundary_pattern),
                    recursive=True
                )
                self.logger.info(f"Found {len(self.config.boundary_files)} boundary files using pattern")
            elif self.config.boundary_dir:
                # Default patterns for common vector formats
                patterns = ["*.shp", "*.geojson", "*.csv", "*.json"]
                self.config.boundary_files = []
                for pattern in patterns:
                    self.config.boundary_files.extend(
                        glob.glob(os.path.join(self.config.boundary_dir, "**", pattern), recursive=True)
                    )
                self.logger.info(f"Found {len(self.config.boundary_files)} boundary files in directory")
        
        if not self.config.raster_files:
            raise ValueError("No raster files specified or found")
        
        if not self.config.boundary_files:
            raise ValueError("No boundary files specified or found")
        
        # Check file existence
        for raster_file in self.config.raster_files:
            if not Path(raster_file).exists():
                raise FileNotFoundError(f"Raster file not found: {raster_file}")
        
        for boundary_file in self.config.boundary_files:
            if not Path(boundary_file).exists():
                raise FileNotFoundError(f"Boundary file not found: {boundary_file}")
    
    def _process_single_combination(self, raster_file: str, boundary_file: str) -> Dict[str, Any]:
        """Process a single raster-boundary combination"""
        # Load geometries
        gdf = self.geometry_handler.load_geometries(boundary_file)
        
        # Filter geometries by type
        original_count = len(gdf)
        geom_types = gdf.geometry.geom_type.unique()
        
        # Check if we should process this geometry type
        allowed_types = []
        for geom_type in geom_types:
            if geom_type in ['Point', 'MultiPoint'] and self.config.process_points:
                allowed_types.append(geom_type)
            elif geom_type in ['Polygon', 'MultiPolygon'] and self.config.process_polygons:
                allowed_types.append(geom_type)
            elif geom_type in self.config.geometry_types_allowed:
                allowed_types.append(geom_type)
        
        if not allowed_types:
            self.logger.warning(f"No allowed geometry types found in {boundary_file}. "
                              f"Found: {geom_types}, Allowed: {self.config.geometry_types_allowed}")
            return {'data': pd.DataFrame(), 'metadata': {}}
        
        # Filter to allowed geometry types
        gdf_filtered = gdf[gdf.geometry.geom_type.isin(allowed_types)]
        
        if len(gdf_filtered) != original_count:
            self.logger.info(f"Filtered {original_count} to {len(gdf_filtered)} geometries based on type restrictions")
        
        if len(gdf_filtered) == 0:
            self.logger.warning(f"No geometries remaining after filtering")
            return {'data': pd.DataFrame(), 'metadata': {}}
        
        # Detect fields
        id_field = self.geometry_handler.detect_id_field(gdf_filtered)
        name_field = self.geometry_handler.detect_name_field(gdf_filtered)
        
        self.logger.info(f"Using ID field: {id_field}, Name field: {name_field}")
        
        # Open raster and get info
        with rasterio.open(raster_file) as src:
            raster_crs = str(src.crs)
            target_crs = self.config.target_crs or raster_crs
            
            # Reproject geometries if needed
            if str(gdf_filtered.crs) != target_crs:
                self.logger.info(f"Reprojecting geometries from {gdf_filtered.crs} to {target_crs}")
                gdf_filtered = gdf_filtered.to_crs(target_crs)
            
            # Determine primary geometry type and extract
            primary_geom_type = gdf_filtered.geometry.geom_type.mode().iloc[0]
            
            if primary_geom_type in ['Point', 'MultiPoint']:
                stats_data = self._extract_point_statistics(src, gdf_filtered, id_field, name_field)
            else:
                stats_data = self._extract_polygon_statistics(src, gdf_filtered, id_field, name_field)
        
        # Create result dataframe
        result_df = pd.DataFrame(stats_data).T
        result_df.index.name = id_field
        result_df = result_df.reset_index()
        
        # Add metadata columns
        raster_name = self._get_clean_name(raster_file)
        boundary_name = self._get_clean_name(boundary_file)
        
        # Prefix statistics columns with raster name if enabled
        if self.config.use_raster_names_in_columns:
            stat_columns = self.stats_engine._get_all_stat_names()
            for col in stat_columns:
                if col in result_df.columns:
                    new_name = f"{raster_name}{self.config.column_name_separator}{col}"
                    result_df.rename(columns={col: new_name}, inplace=True)
        
        # Add name field if available
        if name_field and name_field in gdf_filtered.columns:
            name_mapping = dict(zip(gdf_filtered[id_field], gdf_filtered[name_field]))
            result_df[name_field] = result_df[id_field].map(name_mapping)
        
        metadata = {
            'raster_file': raster_file,
            'boundary_file': boundary_file,
            'raster_name': raster_name,
            'boundary_name': boundary_name,
            'raster_crs': raster_crs,
            'target_crs': target_crs,
            'geometry_types': list(geom_types),
            'primary_geometry_type': primary_geom_type,
            'allowed_geometry_types': allowed_types,
            'id_field': id_field,
            'name_field': name_field,
            'n_geometries_original': original_count,
            'n_geometries_filtered': len(gdf_filtered),
            'n_processed': len(result_df)
        }
        
        return {'data': result_df, 'metadata': metadata}
    
    def _extract_polygon_statistics(self, src, gdf: gpd.GeoDataFrame, id_field: str, name_field: str) -> Dict:
        """Extract statistics for polygon geometries"""
        results = {}
        total = len(gdf)
        
        for idx, row in gdf.iterrows():
            if (idx + 1) % self.config.progress_interval == 0:
                self.logger.info(f"Processing polygon {idx+1}/{total}")
            
            geometry_id = row[id_field]
            geom = mapping(row.geometry)
            
            try:
                # Mask the raster
                out_image, out_transform = mask(
                    src, [geom], 
                    crop=True, 
                    nodata=self.config.nodata_value or np.nan,
                    all_touched=self.config.all_touched
                )
                
                # Get valid data
                valid_data = out_image[0]
                if self.config.nodata_value is not None:
                    valid_data = valid_data[valid_data != self.config.nodata_value]
                else:
                    valid_data = valid_data[~np.isnan(valid_data)]
                
                # Calculate statistics
                stats = self.stats_engine.calculate_statistics(valid_data)
                
                # Add coverage percentage
                total_pixels = out_image[0].size
                valid_pixels = len(valid_data)
                stats['coverage_percent'] = (valid_pixels / total_pixels * 100) if total_pixels > 0 else 0
                
                results[geometry_id] = stats
                
            except ValueError as e:
                if "Input shapes do not overlap raster" in str(e):
                    # Geometry doesn't overlap raster
                    stats = {stat: np.nan for stat in self.stats_engine._get_all_stat_names()}
                    stats['coverage_percent'] = 0
                    results[geometry_id] = stats
                else:
                    self.logger.error(f"Error processing polygon {geometry_id}: {e}")
                    continue
            
            except Exception as e:
                self.logger.error(f"Unexpected error for polygon {geometry_id}: {e}")
                continue
        
        return results
    
    def _extract_point_statistics(self, src, gdf: gpd.GeoDataFrame, id_field: str, name_field: str) -> Dict:
        """Extract statistics for point geometries"""
        results = {}
        
        # Apply buffer if specified
        if self.config.buffer_distance > 0:
            gdf_buffered = gdf.copy()
            gdf_buffered.geometry = gdf_buffered.geometry.buffer(self.config.buffer_distance)
            return self._extract_polygon_statistics(src, gdf_buffered, id_field, name_field)
        
        # Extract point values
        coords = [(geom.x, geom.y) for geom in gdf.geometry]
        
        try:
            # Sample raster at point locations
            sampled_values = list(sample_gen(src, coords))
            
            for idx, (row, values) in enumerate(zip(gdf.itertuples(), sampled_values)):
                geometry_id = getattr(row, id_field)
                
                # Get first band value (assuming single band)
                value = values[0] if values else np.nan
                  # For points, all statistics are the same as the sampled value
                stats = {}
                if not np.isnan(value) and value != self.config.nodata_value:
                    if self.config.single_statistic:
                        # If single statistic is specified, only include that one
                        stats = {
                            self.config.single_statistic: value,
                            'coverage_percent': 100.0  # Always include coverage
                        }
                    else:
                        # Include all configured statistics
                        stats = {
                            'mean': value,
                            'median': value,
                            'min': value,
                            'max': value,
                            'std': 0.0,
                            'count': 1,
                            'coverage_percent': 100.0
                        }
                        
                        # Add percentiles (all same value for single point)
                        for percentile in self.config.statistics.get('percentiles', []):
                            stats[f'p{percentile}'] = value
                else:
                    stats = {stat: np.nan for stat in self.stats_engine._get_all_stat_names()}
                
                results[geometry_id] = stats
        
        except Exception as e:
            self.logger.error(f"Error sampling points: {e}")
            # Return NaN results for all points
            for _, row in gdf.iterrows():
                geometry_id = row[id_field]
                stats = {stat: np.nan for stat in self.stats_engine._get_all_stat_names()}
                results[geometry_id] = stats
        
        return results
        
    def _get_clean_name(self, file_path: str) -> str:
        """Generate clean name from file path"""
        base_name = Path(file_path).stem
        # Remove non-alphanumeric characters except underscores
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name)
        return clean_name
    
    def _combine_results(self, results_list: List[pd.DataFrame], metadata_list: List[Dict]) -> pd.DataFrame:
        """Combine results from multiple raster-boundary combinations"""
        if len(results_list) == 1:
            return results_list[0]
        
        # Find common ID field
        id_fields = [meta['id_field'] for meta in metadata_list]
        common_id_field = id_fields[0] if len(set(id_fields)) == 1 else 'geometry_id'
        
        # Identify columns to keep from metadata/identifiers (non-statistic columns)
        metadata_cols = ['Name']  # Add other metadata columns here if needed
        
        # Merge all results
        combined = results_list[0]
        for i, df in enumerate(results_list[1:], 1):
            # Make a copy to avoid modifying original
            df_to_merge = df.copy()
            
            # Rename ID field if needed
            if metadata_list[i]['id_field'] != common_id_field:
                df_to_merge = df_to_merge.rename(columns={metadata_list[i]['id_field']: common_id_field})
            
            # Drop duplicate metadata columns before merge
            for col in metadata_cols:
                if col in df_to_merge.columns and col in combined.columns:
                    df_to_merge = df_to_merge.drop(columns=[col])
            
            # Drop duplicate coverage_percent columns (keep only with raster-specific stats)
            if 'coverage_percent' in df_to_merge.columns and 'coverage_percent' in combined.columns:
                df_to_merge = df_to_merge.drop(columns=['coverage_percent'])
            
            # Merge without creating duplicate columns
            combined = combined.merge(df_to_merge, on=common_id_field, how='outer')
        
        return combined
    
    def _export_results(self, results_df: pd.DataFrame, metadata_list: List[Dict]) -> List[str]:
        """Export results to various formats"""
        export_paths = []
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        
        # CSV export
        if self.config.save_csv:
            csv_path = Path(self.config.output_dir) / f"extraction_results_{timestamp}.csv"
            results_df.to_csv(csv_path, index=False)
            export_paths.append(str(csv_path))
            self.logger.info(f"Results saved to {csv_path}")
        
        # Save metadata
        metadata_path = Path(self.config.output_dir) / f"extraction_metadata_{timestamp}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata_list, f, indent=2, default=str)
        export_paths.append(str(metadata_path))
        
        # TODO: Add GeoJSON and Shapefile export if geometry data is available
        
        return export_paths
    
    def extract_batch(self, raster_files: List[str], boundary_files: List[str], **kwargs) -> Dict[str, Any]:
        """Programmatic interface for batch extraction"""
        # Update config with new files
        self.config.raster_files = raster_files
        self.config.boundary_files = boundary_files
        
        # Apply any runtime overrides
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        return self.run()


def create_sample_config() -> Dict:
    """Create a sample configuration dictionary with all advanced options"""
    return {
        # ============================================================================
        # INPUT/OUTPUT CONFIGURATION
        # ============================================================================
        
        # Option 1: Specify exact files
        "raster_files": [
            "/path/to/data/environmental/NO2_2010.tif",
            "/path/to/data/environmental/PM25_2010.tif",
            "/path/to/data/environmental/BC_2010.tif"
        ],
        "boundary_files": [
            "/path/to/boundaries/nuts_regions_l3.shp",
            "/path/to/points/monitoring_stations.csv"
        ],
        
        # Option 2: Auto-discover files using directories and patterns
        # "raster_dir": "/path/to/environmental/data",
        # "raster_pattern": "*NO2*.tif",  # or "*.tif" for all
        # "boundary_dir": "/path/to/boundaries",
        # "boundary_pattern": "*.shp",
        
        # Output configuration
        "output_dir": "extraction_results_2024",
        "output_prefix": "environmental_extraction",
        
        # ============================================================================
        # GEOMETRY PROCESSING OPTIONS
        # ============================================================================
        
        # Control which geometry types to process
        "process_polygons": True,
        "process_points": False,  # Set to False if you don't want points
        "geometry_types_allowed": ["Point", "Polygon", "MultiPolygon"],
        
        # Field configuration (leave null for auto-detection)
        "geometry_id_field": None,  # Auto-detect: tries 'id', 'objectid', 'nuts_id', etc.
        "geometry_name_field": None,  # Auto-detect: tries 'name', 'name_latn', etc.
        
        # Coordinate field names for CSV/JSON points (flexible detection)
        "coordinate_fields": {
            "x": ["x", "lon", "lng", "longitude", "long", "x_coord", "easting"],
            "y": ["y", "lat", "latitude", "y_coord", "northing"]
        },
        
        # ============================================================================
        # SPATIAL REFERENCE SYSTEM
        # ============================================================================
        
        "target_crs": "EPSG:3035",  # European projection, null for auto-detect from raster
        "geometry_crs": None,  # Auto-detect from files, or specify like "EPSG:4326"
        "force_crs_match": True,
        
        # ============================================================================
        # STATISTICS CONFIGURATION
        # ============================================================================
        
        # Option 1: Multiple statistics
        "statistics": {
            "basic": ["mean", "median", "min", "max", "std", "count"],
            "percentiles": [25, 75, 90, 95],
            "custom": ["coverage_percent"]
        },
        
        # Option 2: Single statistic only (uncomment to use)
        # "single_statistic": "mean",  # Only compute mean values
        # "single_statistic": "p90",   # Only compute 90th percentile
        
        # ============================================================================
        # PROCESSING OPTIONS
        # ============================================================================
        
        "all_touched": True,  # Include pixels touched by geometry boundary
        "nodata_value": None,  # Auto-detect nodata, or specify like -9999
        "buffer_distance": 0.0,  # Buffer around points in meters (0 for exact points)
        "max_points_per_chunk": 1000,
        "skip_existing": False,
        
        # Filtering options
        "min_valid_pixels": 1,  # Minimum valid pixels required for result
        "min_coverage_percent": 0.0,  # Minimum coverage required
        "max_coverage_percent": 100.0,  # Maximum coverage allowed
        
        # ============================================================================
        # OUTPUT FORMAT OPTIONS
        # ============================================================================
        
        "save_csv": True,
        "save_geojson": False,  # Set True if you want spatial outputs
        "save_shapefile": False,
        "save_excel": False,
        "include_geometry": False,  # Include geometry data in outputs
        "separate_files_per_raster": False,  # One file per raster vs combined
        
        # Column naming options
        "use_raster_names_in_columns": True,  # Prefix columns with raster names
        "column_name_separator": "_",  # Separator for column names
        "remove_file_extensions": True,
        
        # ============================================================================
        # LOGGING AND PROGRESS
        # ============================================================================
        
        "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR
        "progress_interval": 50,  # Log progress every N geometries
        "log_to_file": False,
        "log_file": None  # "extraction.log"
    }


def create_scenario_configs() -> Dict[str, Dict]:
    """Create configuration examples for different use scenarios"""
    
    scenarios = {}
    
    # ============================================================================
    # SCENARIO 1: Simple mean extraction from multiple environmental variables
    # ============================================================================
    scenarios["simple_mean_only"] = {
        "raster_dir": "/data/environmental",
        "raster_pattern": "*.tif",
        "boundary_files": ["/boundaries/nuts_l3.shp"],
        "output_dir": "results_mean_only",
        "single_statistic": "mean",
        "process_points": False,
        "save_csv": True,
        "save_geojson": False,
        "log_level": "INFO"
    }
    
    # ============================================================================
    # SCENARIO 2: Comprehensive statistics for air quality research
    # ============================================================================
    scenarios["air_quality_comprehensive"] = {
        "raster_files": [
            "/data/NO2_2020.tif",
            "/data/PM25_2020.tif", 
            "/data/PM10_2020.tif",
            "/data/BC_2020.tif"
        ],
        "boundary_files": ["/boundaries/administrative_regions.shp"],
        "output_dir": "air_quality_analysis_2020",
        "target_crs": "EPSG:3035",
        "statistics": {
            "basic": ["mean", "median", "max"],
            "percentiles": [90, 95, 99],
            "custom": ["coverage_percent"]
        },
        "process_polygons": True,
        "process_points": False,
        "min_coverage_percent": 10.0,  # Require at least 10% coverage
        "save_csv": True,
        "save_excel": True
    }
    
    # ============================================================================
    # SCENARIO 3: Point-based monitoring station analysis
    # ============================================================================
    scenarios["monitoring_stations"] = {
        "raster_dir": "/data/meteorological",
        "raster_pattern": "*TEMP*.tif",
        "boundary_files": ["/stations/weather_stations.csv"],
        "output_dir": "station_temperatures",
        "process_polygons": False,
        "process_points": True,
        "buffer_distance": 1000.0,  # 1km buffer around stations
        "single_statistic": "mean",
        "coordinate_fields": {
            "x": ["longitude", "lon"],
            "y": ["latitude", "lat"]
        },
        "save_csv": True
    }
    
    # ============================================================================
    # SCENARIO 4: Climate data batch processing
    # ============================================================================
    scenarios["climate_batch"] = {
        "raster_dir": "/climate_data/2020",
        "boundary_dir": "/administrative_boundaries",
        "boundary_pattern": "*nuts*.shp",
        "output_dir": "climate_analysis_2020",
        "statistics": {
            "basic": ["mean", "min", "max"],
            "percentiles": [10, 90]
        },
        "separate_files_per_raster": True,
        "use_raster_names_in_columns": True,
        "save_csv": True,
        "save_geojson": True,
        "log_level": "DEBUG"
    }
    
    return scenarios


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description="Advanced Raster Extraction Tool")
    parser.add_argument("--config", "-c", help="Configuration file (YAML/JSON)")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--rasters", "-r", nargs="+", help="Raster files")
    parser.add_argument("--boundaries", "-b", nargs="+", help="Boundary files")
    parser.add_argument("--raster-dir", help="Directory containing raster files")
    parser.add_argument("--boundary-dir", help="Directory containing boundary files")
    parser.add_argument("--raster-pattern", help="Pattern for raster files (e.g., '*NO2*.tif')")
    parser.add_argument("--boundary-pattern", help="Pattern for boundary files (e.g., '*.shp')")
    parser.add_argument("--crs", help="Target CRS (e.g., EPSG:3035)")
    parser.add_argument("--single-stat", help="Calculate only one statistic (e.g., mean, p90)")
    parser.add_argument("--no-points", action="store_true", help="Skip point geometries")
    parser.add_argument("--no-polygons", action="store_true", help="Skip polygon geometries")
    parser.add_argument("--create-config", action="store_true", help="Create sample config file")
    parser.add_argument("--create-scenarios", action="store_true", help="Create scenario config files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument("--buffer", type=float, help="Buffer distance for points (meters)")
    
    args = parser.parse_args()
    
    if args.create_config:
        config = create_sample_config()
        config_file = "raster_extractor_config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        print(f"Advanced configuration saved to {config_file}")
        print("Edit this file with your specific paths and settings.")
        return
    
    if args.create_scenarios:
        scenarios = create_scenario_configs()
        for scenario_name, scenario_config in scenarios.items():
            filename = f"config_{scenario_name}.yaml"
            with open(filename, "w") as f:
                yaml.dump(scenario_config, f, default_flow_style=False, sort_keys=False)
            print(f"Scenario '{scenario_name}' saved to {filename}")
        print(f"\nCreated {len(scenarios)} scenario configuration files.")
        print("Choose the one that best matches your use case and modify as needed.")
        return
    
    # Build runtime config
    runtime_config = {}
    if args.output:
        runtime_config["output_dir"] = args.output
    if args.rasters:
        runtime_config["raster_files"] = args.rasters
    if args.boundaries:
        runtime_config["boundary_files"] = args.boundaries
    if args.raster_dir:
        runtime_config["raster_dir"] = args.raster_dir
    if args.boundary_dir:
        runtime_config["boundary_dir"] = args.boundary_dir
    if args.raster_pattern:
        runtime_config["raster_pattern"] = args.raster_pattern
    if args.boundary_pattern:
        runtime_config["boundary_pattern"] = args.boundary_pattern
    if args.crs:
        runtime_config["target_crs"] = args.crs
    if args.single_stat:
        runtime_config["single_statistic"] = args.single_stat
    if args.no_points:
        runtime_config["process_points"] = False
    if args.no_polygons:
        runtime_config["process_polygons"] = False
    if args.buffer:
        runtime_config["buffer_distance"] = args.buffer
    if args.verbose:
        runtime_config["log_level"] = "DEBUG"
    
    # Initialize processor
    processor = RasterExtractor(config_file=args.config, **runtime_config)
    
    # Run extraction
    results = processor.run()
    
    if results['results'] is not None:
        print(f"\n✅ Extraction completed successfully!")
        print(f"📊 Results shape: {results['results'].shape}")
        print(f"📁 Export files:")
        for path in results['export_paths']:
            print(f"   - {path}")
        print(f"🔄 Processed {len(results['metadata'])} raster-boundary combinations")
    else:
        print("❌ Extraction failed - check logs for details")


if __name__ == "__main__":
    main()