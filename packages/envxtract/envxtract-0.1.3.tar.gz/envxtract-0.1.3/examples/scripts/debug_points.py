#!/usr/bin/env python3
"""
Debug Points Shapefile
======================
Quick script to inspect your points shapefile and identify issues.

Usage:
    python debug_points.py
"""

import geopandas as gpd
import pandas as pd


def debug_points_file(points_file="data/input/combined_selected_ALL-points.shp"):
    """Debug the points shapefile to identify issues"""
    
    print("🔍 DEBUGGING POINTS SHAPEFILE")
    print("=" * 50)
    
    try:
        # Load the shapefile
        print(f"📂 Loading: {points_file}")
        gdf = gpd.read_file(points_file)
        
        print(f"✅ Successfully loaded!")
        print(f"📊 Shape: {gdf.shape} (rows, columns)")
        print(f"🗂️  CRS: {gdf.crs}")
        
        # Show column information
        print(f"\n📋 COLUMNS ({len(gdf.columns)} total):")
        for i, col in enumerate(gdf.columns):
            col_type = str(gdf[col].dtype)
            non_null = gdf[col].notna().sum()
            print(f"  {i+1:2d}. {col:<20} | {col_type:<12} | {non_null}/{len(gdf)} non-null")
        
        # Check geometry type
        print(f"\n🗺️  GEOMETRY INFO:")
        geom_types = gdf.geometry.geom_type.value_counts()
        print(f"Geometry types: {dict(geom_types)}")
        
        # Check for potential ID fields
        print(f"\n🔍 POTENTIAL ID FIELDS:")
        id_candidates = ['id', 'ID', 'objectid', 'OBJECTID', 'fid', 'FID', 'point_id', 'station_id', 'site_id']
        found_ids = []
        
        for candidate in id_candidates:
            if candidate in gdf.columns:
                found_ids.append(candidate)
                unique_vals = gdf[candidate].nunique()
                print(f"  ✅ {candidate}: {unique_vals} unique values")
        
        if not found_ids:
            print(f"  ⚠️  No standard ID fields found")
            print(f"  💡 Will need to create ID field (point_id)")
        
        # Show first few rows
        print(f"\n📋 FIRST 3 ROWS:")
        display_cols = [col for col in gdf.columns if col != 'geometry'][:5]  # Show first 5 non-geometry columns
        if len(display_cols) > 0:
            print(gdf[display_cols].head(3).to_string(index=True))
        
        # Check for empty geometries
        empty_geoms = gdf.geometry.isna().sum()
        if empty_geoms > 0:
            print(f"\n⚠️  WARNING: {empty_geoms} empty geometries found!")
        
        # Check bounds
        bounds = gdf.total_bounds
        print(f"\n📐 SPATIAL BOUNDS:")
        print(f"  X: {bounds[0]:.2f} to {bounds[2]:.2f}")
        print(f"  Y: {bounds[1]:.2f} to {bounds[3]:.2f}")
        
        # Suggest fixes
        print(f"\n💡 RECOMMENDED FIXES:")
        if not found_ids:
            print(f"  1. Add ID field: gdf['point_id'] = range(1, len(gdf)+1)")
        if empty_geoms > 0:
            print(f"  2. Remove empty geometries: gdf = gdf[gdf.geometry.notna()]")
        if gdf.crs is None:
            print(f"  3. Set CRS: gdf.set_crs('EPSG:4326', inplace=True)")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ File not found: {points_file}")
        print(f"   Please check the file path")
        return False
        
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return False


def fix_points_file(input_file, output_file=None):
    """Create a fixed version of the points file"""
    
    if output_file is None:
        output_file = input_file.replace('.shp', '_fixed.shp')
    
    print(f"\n🔧 FIXING POINTS FILE")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    
    try:
        gdf = gpd.read_file(input_file)
        
        # Remove empty geometries
        original_count = len(gdf)
        gdf = gdf[gdf.geometry.notna()]
        if len(gdf) < original_count:
            print(f"  ✂️  Removed {original_count - len(gdf)} empty geometries")
        
        # Add ID field if missing
        id_candidates = ['id', 'ID', 'objectid', 'OBJECTID', 'fid', 'FID']
        has_id = any(candidate in gdf.columns for candidate in id_candidates)
        
        if not has_id:
            gdf['point_id'] = range(1, len(gdf) + 1)
            print(f"  ➕ Added 'point_id' field")
        
        # Set CRS if missing
        if gdf.crs is None:
            gdf.set_crs('EPSG:4326', inplace=True)
            print(f"  🌍 Set CRS to EPSG:4326")
        
        # Save fixed file
        gdf.to_file(output_file)
        print(f"✅ Fixed file saved: {output_file}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error fixing file: {e}")
        return None


if __name__ == "__main__":
    # Debug the points file
    points_file = "data/input/combined_selected_ALL-points.shp"
    
    success = debug_points_file(points_file)
    
    if success:
        print(f"\n" + "="*50)
        response = input("Would you like to create a fixed version? (y/n): ").lower().strip()
        
        if response in ['y', 'yes']:
            fixed_file = fix_points_file(points_file)
            if fixed_file:
                print(f"\n💡 Use the fixed file in your extraction:")
                print(f'POINTS_FILE = "{fixed_file}"')