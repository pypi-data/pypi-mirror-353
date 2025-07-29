# Advanced Raster Extraction Configuration Examples

## 🚀 Quick Start - Generate Config Files

```bash
# Create comprehensive config with all options explained
python raster_extractor.py --create-config

# Create multiple scenario-specific configs
python raster_extractor.py --create-scenarios
```

## 📋 Configuration File Examples

### 1. **Simple Mean-Only Extraction** (`config_simple_mean.yaml`)

```yaml
# Perfect for quick analysis - just extract mean values
raster_dir: "/data/environmental"
raster_pattern: "*.tif"  # All TIF files
boundary_files: 
  - "/boundaries/nuts_regions_l3.shp"

output_dir: "results_mean_only"
single_statistic: "mean"  # ONLY compute mean values

# Disable point processing if you only want polygons
process_points: false
process_polygons: true

save_csv: true
save_geojson: false
log_level: "INFO"
```

### 2. **Air Quality Comprehensive Analysis** (`config_air_quality.yaml`)

```yaml
# Multiple environmental variables with comprehensive statistics
raster_files:
  - "/data/environmental/NO2_2020.tif"
  - "/data/environmental/PM25_2020.tif"
  - "/data/environmental/PM10_2020.tif"
  - "/data/environmental/BC_2020.tif"

boundary_files: 
  - "/boundaries/nuts_regions_l3.shp"

output_dir: "air_quality_analysis_2020"
target_crs: "EPSG:3035"

# Multiple statistics for research
statistics:
  basic: ["mean", "median", "max"]
  percentiles: [90, 95, 99]
  custom: ["coverage_percent"]

# Quality filters
min_coverage_percent: 10.0  # Require at least 10% coverage
process_polygons: true
process_points: false

# Output options
save_csv: true
save_excel: true
use_raster_names_in_columns: true
```

### 3. **Point-Based Monitoring Stations** (`config_stations.yaml`)

```yaml
# Extract values at monitoring station locations
raster_dir: "/data/meteorological"
raster_pattern: "*TEMP*.tif"

boundary_files: 
  - "/stations/weather_stations.csv"

output_dir: "station_temperatures"

# ONLY process points, NO polygons
process_polygons: false
process_points: true

# Buffer around stations for area-based analysis
buffer_distance: 1000.0  # 1km buffer

# Just need mean temperature
single_statistic: "mean"

# Flexible coordinate detection
coordinate_fields:
  x: ["longitude", "lon", "x_coord"]
  y: ["latitude", "lat", "y_coord"]

save_csv: true
```

### 4. **Batch Processing with Auto-Discovery** (`config_batch.yaml`)

```yaml
# Process ALL rasters against ALL boundaries automatically
raster_dir: "/climate_data/2020"
boundary_dir: "/administrative_boundaries"
boundary_pattern: "*nuts*.shp"

output_dir: "climate_analysis_2020"

# Target specific statistics
statistics:
  basic: ["mean", "min", "max"]
  percentiles: [10, 90]

# Create separate output file for each raster
separate_files_per_raster: true

# Include both geometry types
process_polygons: true
process_points: true

save_csv: true
save_geojson: true
log_level: "DEBUG"
```

### 5. **Single Percentile Extraction** (`config_p90_only.yaml`)

```yaml
# Extract only 90th percentile values
raster_files:
  - "/data/pollution/NO2_annual.tif"
  - "/data/pollution/PM25_annual.tif"

boundary_files:
  - "/boundaries/administrative_regions.shp"

output_dir: "p90_analysis"

# ONLY 90th percentile
single_statistic: "p90"

process_points: false  # Skip points
save_csv: true
```

## 🎯 Usage Examples

### Command Line Usage

```bash
# Use specific config file
python raster_extractor.py --config config_air_quality.yaml

# Override config with CLI parameters
python raster_extractor.py --config config_simple.yaml --single-stat mean --no-points

# Quick run without config file
python raster_extractor.py \
  --raster-dir "/data/environmental" \
  --raster-pattern "*NO2*.tif" \
  --boundaries "/boundaries/nuts.shp" \
  --output "quick_results" \
  --single-stat "mean"

# Batch processing with auto-discovery
python raster_extractor.py \
  --raster-dir "/environmental_data" \
  --boundary-dir "/admin_boundaries" \
  --boundary-pattern "*.shp" \
  --output "batch_results"
```

### Programmatic Usage

```python
from raster_extractor import RasterExtractor

# Method 1: Use config file
processor = RasterExtractor(config_file="config_air_quality.yaml")
results = processor.run()

# Method 2: Override config at runtime
processor = RasterExtractor(
    config_file="config_base.yaml",
    single_statistic="mean",
    process_points=False,
    output_dir="custom_results"
)
results = processor.run()

# Method 3: Direct configuration
config = {
    "raster_files": ["/data/NO2.tif", "/data/PM25.tif"],
    "boundary_files": ["/boundaries/regions.shp"],
    "single_statistic": "mean",
    "output_dir": "analysis_results"
}
processor = RasterExtractor(config_dict=config)
results = processor.run()

# Method 4: Batch processing interface
processor = RasterExtractor()
results = processor.extract_batch(
    raster_files=["/data/raster1.tif", "/data/raster2.tif"],
    boundary_files=["/boundaries/regions.shp"],
    single_statistic="p90",
    process_points=False
)
```

## ⚙️ Key Configuration Options

### Input/Output Control
- `raster_files` / `raster_dir` + `raster_pattern`: Specify exact files or auto-discover
- `boundary_files` / `boundary_dir` + `boundary_pattern`: Same for boundaries
- `output_dir`, `output_prefix`: Control output location and naming

### Geometry Processing
- `process_points: false` - Skip point geometries entirely
- `process_polygons: false` - Skip polygon geometries entirely  
- `geometry_types_allowed` - Fine-grained control over geometry types

### Statistics Control
- `single_statistic: "mean"` - Extract only one statistic
- `single_statistic: "p90"` - Extract only 90th percentile
- `statistics:` - Define multiple statistics (basic, percentiles, custom)

### Quality Control
- `min_coverage_percent: 10.0` - Require minimum coverage
- `min_valid_pixels: 5` - Require minimum valid pixels
- `buffer_distance: 1000.0` - Buffer around points (meters)

### Output Options
- `save_csv: true` - Always saves CSV results
- `save_geojson: true` - Include spatial outputs
- `separate_files_per_raster: true` - One output per raster vs combined

## 🔄 Typical Workflows

### Workflow 1: Environmental Monitoring
1. Set `raster_dir` to your environmental data folder
2. Set `single_statistic: "mean"` for simple analysis
3. Set `process_points: false` if only using administrative boundaries
4. Run and get CSV with mean values per region

### Workflow 2: Research Analysis
1. List specific `raster_files` for your study variables
2. Define comprehensive `statistics` (mean, percentiles, etc.)
3. Set quality filters (`min_coverage_percent`)
4. Use both CSV and Excel outputs

### Workflow 3: Monitoring Stations
1. Point to station CSV file in `boundary_files`
2. Set `process_polygons: false` and `process_points: true`
3. Add `buffer_distance` for area around stations
4. Use `single_statistic` for simple extraction

Just **edit the file paths** in these configs and you're ready to run! 🎯