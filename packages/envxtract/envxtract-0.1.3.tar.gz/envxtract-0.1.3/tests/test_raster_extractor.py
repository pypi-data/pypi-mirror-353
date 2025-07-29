#!/usr/bin/env python3
"""
Simple Pytest Test for EnvXtract Raster Extractor
==================================================
Usage: python -m pytest tests/test_raster_extractor.py -v
"""

import os
import tempfile
import shutil
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.transform import from_bounds
from shapely.geometry import Polygon
import pytest

# Import the installed package
from envxtract.raster_extractor import RasterExtractor


def create_test_data():
    """Create minimal test raster and polygon"""
    test_dir = tempfile.mkdtemp(prefix="envxtract_test_")
    
    # Create simple 5x5 raster with value 42
    bounds = [0, 0, 1, 1]
    width, height = 5, 5
    transform = from_bounds(*bounds, width, height)
    data = np.full((height, width), 42.0, dtype=np.float32)
    
    raster_path = os.path.join(test_dir, "test.tif")
    with rasterio.open(
        raster_path, 'w', driver='GTiff', height=height, width=width,
        count=1, dtype=data.dtype, crs="EPSG:4326", transform=transform
    ) as dst:
        dst.write(data, 1)
    
    # Create simple polygon covering most of the raster
    polygon = Polygon([(0.1, 0.1), (0.9, 0.1), (0.9, 0.9), (0.1, 0.9)])
    gdf = gpd.GeoDataFrame([{'id': 1, 'name': 'test_region'}], 
                          geometry=[polygon], crs="EPSG:4326")
    
    polygon_path = os.path.join(test_dir, "test_polygon.shp")
    gdf.to_file(polygon_path)
    
    return test_dir, raster_path, polygon_path


def test_import():
    """Test that RasterExtractor can be imported"""
    from envxtract.raster_extractor import RasterExtractor
    assert RasterExtractor is not None


def test_basic_initialization():
    """Test basic RasterExtractor initialization"""
    config = {
        "raster_files": [],
        "boundary_files": [],
        "output_dir": "test_output"
    }
    
    processor = RasterExtractor(config_dict=config)
    assert processor is not None
    assert processor.config.output_dir == "test_output"


def test_simple_extraction():
    """Test basic raster extraction functionality"""
    # Create test data
    test_dir, raster_path, polygon_path = create_test_data()
    
    try:
        # Configure extraction
        config = {
            "raster_files": [raster_path],
            "boundary_files": [polygon_path],
            "output_dir": os.path.join(test_dir, "results"),
            "single_statistic": "mean",
            "save_csv": True,
            "log_level": "WARNING"  # Reduce log noise during tests
        }
        
        # Run extraction
        processor = RasterExtractor(config_dict=config)
        results = processor.run()
        
        # Verify results
        assert results is not None
        assert results['results'] is not None
        
        df = results['results']
        assert len(df) > 0  # Should have at least one result
        
        # Check that mean value is approximately 42 (our test data value)
        mean_cols = [col for col in df.columns if 'mean' in col]
        assert len(mean_cols) > 0, "Should have at least one mean column"
        
        mean_val = df[mean_cols[0]].iloc[0]
        assert 40 <= mean_val <= 44, f"Mean value {mean_val} should be around 42"
        
        # Check that output files were created
        export_paths = results.get('export_paths', [])
        assert len(export_paths) > 0, "Should create at least one output file"
        
        # Verify CSV file exists
        csv_files = [p for p in export_paths if p.endswith('.csv')]
        assert len(csv_files) > 0, "Should create a CSV file"
        assert os.path.exists(csv_files[0]), "CSV file should exist"
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)


def test_multiple_statistics():
    """Test extraction with multiple statistics"""
    test_dir, raster_path, polygon_path = create_test_data()
    
    try:
        config = {
            "raster_files": [raster_path],
            "boundary_files": [polygon_path],
            "output_dir": os.path.join(test_dir, "results"),
            "statistics": {
                "basic": ["mean", "min", "max"],
                "percentiles": [90]
            },
            "save_csv": True,
            "log_level": "WARNING"
        }
        
        processor = RasterExtractor(config_dict=config)
        results = processor.run()
        
        df = results['results']
        
        # Should have multiple statistic columns
        stat_cols = [col for col in df.columns if any(stat in col for stat in ['mean', 'min', 'max', 'p90'])]
        assert len(stat_cols) >= 4, f"Should have at least 4 statistic columns, got: {stat_cols}"
        
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    # Allow running directly for debugging
    print("🧪 Running tests directly...")
    test_import()
    print("✅ Import test passed")
    
    test_basic_initialization()
    print("✅ Initialization test passed")
    
    test_simple_extraction()
    print("✅ Simple extraction test passed")
    
    test_multiple_statistics()
    print("✅ Multiple statistics test passed")
    
    print("🎉 All tests passed!")