#!/usr/bin/env python3
"""
EnvXtract Simple Extraction Example
===================================
This script demonstrates how to use EnvXtract to extract mean values 
from environmental rasters for both administrative regions (NUTS) and point locations.

Directory Structure:
    data/
    ├── input/
    │   ├── rasters/          # Environmental raster files (.tif)
    │   ├── nuts_regions.shp  # Administrative boundaries
    │   └── monitoring_points.shp  # Point locations
    └── output/               # Results will be saved here

Usage:
    python examples/scripts/simple_extraction.py
"""

import os
import glob
from pathlib import Path
from datetime import datetime
from envxtract.raster_extractor import RasterExtractor


def main():
    """Run simple environmental data extraction"""
    
    print("🌍 EnvXtract Simple Extraction Example")
    print("=" * 50)
    
    # =================================================================
    # CONFIGURATION - Modify these paths for your data
    # =================================================================
    
    # Input data paths
    RASTER_DIR = "data/input/rasters"                    # Directory containing raster files
    NUTS_FILE = "data/input/NUTS_RG_L3.shp"           # Administrative boundaries shapefile
    POINTS_FILE = "data/input/combined_selected_ALL-points.geojson"    # Point locations shapefile
    
    # Output directory
    OUTPUT_DIR = "data/output"
    
    # Raster file pattern (modify based on your files)
    RASTER_PATTERN = "*.tif"  # All TIF files
    # RASTER_PATTERN = "*NO2*.tif"     # Only NO2 files
    # RASTER_PATTERN = "*PM25*.tif"    # Only PM25 files
    
    # =================================================================
    # SETUP
    # =================================================================
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Find raster files
    raster_files = glob.glob(os.path.join(RASTER_DIR, RASTER_PATTERN))
    
    if not raster_files:
        print(f"❌ No raster files found in {RASTER_DIR} with pattern {RASTER_PATTERN}")
        print("   Please check your file paths and pattern")
        return
    
    print(f"📁 Found {len(raster_files)} raster files:")
    for f in raster_files:
        print(f"   - {os.path.basename(f)}")
    
    # Check boundary files
    if not os.path.exists(NUTS_FILE):
        print(f"⚠️  NUTS file not found: {NUTS_FILE}")
        print("   Skipping NUTS extraction")
        nuts_file = None
    else:
        nuts_file = NUTS_FILE
        print(f"✅ NUTS file found: {os.path.basename(NUTS_FILE)}")
    
    if not os.path.exists(POINTS_FILE):
        print(f"⚠️  Points file not found: {POINTS_FILE}")
        print("   Skipping points extraction")
        points_file = None
    else:
        points_file = POINTS_FILE
        print(f"✅ Points file found: {os.path.basename(POINTS_FILE)}")
    
    if not nuts_file and not points_file:
        print("❌ No boundary files found. Please check your file paths.")
        return
    
    # =================================================================
    # EXTRACTION 1: NUTS REGIONS (Administrative Boundaries)
    # =================================================================
    
    if nuts_file:
        print(f"\n🗺️  Extracting data for NUTS regions...")
        
        nuts_config = {
            "raster_files": raster_files,
            "boundary_files": [nuts_file],
            "output_dir": os.path.join(OUTPUT_DIR, "nuts_results"),
            "output_prefix": "nuts_extraction",
            
            # Extract only mean values
            "single_statistic": "mean",
            
            # Process only polygons (skip points)
            "process_polygons": True,
            "process_points": False,
            
            # Output options
            "save_csv": True,
            "save_geojson": False,
            "use_raster_names_in_columns": True,
            
            # Reduce log noise
            "log_level": "INFO"
        }
        
        try:
            processor = RasterExtractor(config_dict=nuts_config)
            nuts_results = processor.run()
            
            if nuts_results['results'] is not None:
                print(f"✅ NUTS extraction completed!")
                print(f"   📊 Results shape: {nuts_results['results'].shape}")
                print(f"   📁 Files saved:")
                for path in nuts_results['export_paths']:
                    print(f"      - {path}")
            else:
                print("❌ NUTS extraction failed")
                
        except Exception as e:
            print(f"❌ Error in NUTS extraction: {e}")
    
    # =================================================================
    # EXTRACTION 2: POINT LOCATIONS (Monitoring Stations)
    # =================================================================
    
    if points_file:
        print(f"\n📍 Extracting data for point locations...")
        
        points_config = {
            "raster_files": raster_files,
            "boundary_files": [points_file],
            "output_dir": os.path.join(OUTPUT_DIR, "points_results"),
            "output_prefix": "points_extraction",
            
            # Extract only mean values
            "single_statistic": "mean",
            
            # Process only points (skip polygons)
            "process_polygons": False,
            "process_points": True,
            
            # Point-specific options
            "buffer_distance": 0.0,  # Exact point values (no buffer)
            # "buffer_distance": 1000.0,  # Uncomment for 1km buffer around points
            
            # Output options
            "save_csv": True,
            "save_geojson": False,
            "use_raster_names_in_columns": True,
            
            # Reduce log noise
            "log_level": "INFO"
        }
        
        try:
            processor = RasterExtractor(config_dict=points_config)
            points_results = processor.run()
            
            if points_results['results'] is not None:
                print(f"✅ Points extraction completed!")
                print(f"   📊 Results shape: {points_results['results'].shape}")
                print(f"   📁 Files saved:")
                for path in points_results['export_paths']:
                    print(f"      - {path}")
            else:
                print("❌ Points extraction failed")
                
        except Exception as e:
            print(f"❌ Error in points extraction: {e}")
    
    # =================================================================
    # SUMMARY
    # =================================================================
    
    print(f"\n🎉 Extraction completed!")
    print(f"📁 Check results in: {OUTPUT_DIR}")
    print(f"   - nuts_results/     (administrative regions)")
    print(f"   - points_results/   (monitoring stations)")
    print(f"\n💡 Next steps:")
    print(f"   - Load CSV files for analysis")
    print(f"   - Combine with other datasets")
    print(f"   - Create visualizations")


def example_load_results():
    """Example of how to load and use the results"""
    import pandas as pd
    
    # Load NUTS results
    nuts_csv = "data/output/nuts_results/nuts_extraction_*.csv"
    nuts_files = glob.glob(nuts_csv)
    if nuts_files:
        nuts_df = pd.read_csv(nuts_files[0])
        print(f"NUTS data shape: {nuts_df.shape}")
        print(f"NUTS columns: {list(nuts_df.columns)}")
    
    # Load points results
    points_csv = "data/output/points_results/points_extraction_*.csv"
    points_files = glob.glob(points_csv)
    if points_files:
        points_df = pd.read_csv(points_files[0])
        print(f"Points data shape: {points_df.shape}")
        print(f"Points columns: {list(points_df.columns)}")


if __name__ == "__main__":
    main()
    
    # Uncomment to see example of loading results
    # print("\n" + "="*50)
    # print("📊 Example: Loading Results")
    # example_load_results()