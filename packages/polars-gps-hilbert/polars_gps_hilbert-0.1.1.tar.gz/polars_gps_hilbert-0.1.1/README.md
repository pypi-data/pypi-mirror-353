# polars-gps-hilbert

> ⚠️ **EXPERIMENTAL SOFTWARE**: This plugin is in active development and should not be used in production environments. APIs may change without notice.

A high-performance Polars plugin for GPS trajectory indexing using 3D Hilbert curves. This plugin enables efficient spatial-temporal indexing of GPS data for applications like trajectory analysis, route deviation detection, and spatial queries.

## Features

- **3D Hilbert Curve Indexing**: Combines latitude, longitude, and timestamp into a single index
- **Lazy Evaluation**: Supports out-of-core processing for datasets larger than memory
- **Automatic Bounds Detection**: Automatically computes spatial and temporal bounds or accepts pre-computed values
- **High Performance**: Written in Rust for maximum performance (10-15M points/second)
- **Polars Integration**: Seamless integration with Polars' expression API and lazy evaluation

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/nullbutt/polars-gps-hilbert.git
cd polars-gps-hilbert

# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Build and install the plugin
./build_and_test.sh
```

### Requirements

- Python >= 3.8
- Rust toolchain (for building from source)
- Polars >= 0.20.0
- UV (for Python project management)

## Quick Start

```python
import polars as pl
import polars_gps_hilbert as gps

# Load GPS trajectory data
df = pl.read_parquet("gps_data.parquet")

# Add Hilbert index with automatic bounds computation
df = df.with_columns(
    gps.hilbert_index("latitude", "longitude", "timestamp").alias("hilbert_idx")
)

# Use for spatial queries
nearby_points = df.sort("hilbert_idx").slice(1000, 100)
```

## Usage Examples

### Basic Indexing

```python
import polars as pl
import polars_gps_hilbert as gps

df = pl.DataFrame({
    "latitude": [37.7749, 34.0522, 40.7128],
    "longitude": [-122.4194, -118.2437, -74.0060],
    "timestamp": [1640995200, 1640998800, 1641002400]
})

result = df.with_columns(
    gps.hilbert_index("latitude", "longitude", "timestamp").alias("hilbert_idx")
)
```

### With Pre-computed Bounds (Better Performance)

```python
bounds = {
    "lat_min": -90.0, "lat_max": 90.0,
    "lon_min": -180.0, "lon_max": 180.0,
    "ts_min": 1640995200, "ts_max": 1767225600
}

df = df.with_columns(
    gps.hilbert_index("latitude", "longitude", "timestamp", bounds=bounds).alias("hilbert_idx")
)
```

### Lazy Evaluation for Large Datasets

```python
# Perfect for datasets larger than memory
lf = pl.scan_parquet("huge_gps_dataset.parquet")

result = lf.with_columns(
    gps.hilbert_index("latitude", "longitude", "timestamp").alias("hilbert_idx")
).filter(
    pl.col("hilbert_idx") < 1000000
).collect()
```

### Spatial Range Queries

```python
# Sort by Hilbert index for efficient spatial queries
df_sorted = df.sort("hilbert_idx")

# Find nearby points using index ranges
reference_idx = df_sorted["hilbert_idx"][1000]
range_size = 1000000

nearby = df_sorted.filter(
    (pl.col("hilbert_idx") >= reference_idx - range_size) &
    (pl.col("hilbert_idx") <= reference_idx + range_size)
)
```

## Performance

Benchmarked on Apple M1 MacBook Pro:

- **Throughput**: 10-15 million points/second
- **Memory overhead**: 8 bytes per index (21.8% increase)
- **Spatial locality**: Excellent for nearby GPS points
- **Scales linearly**: Tested up to 200M points

## Dataset Generation

Generate test datasets for benchmarking:

```bash
# Generate 1M point test dataset
cd examples
python generate_sample_data.py

# Generate full 200M point dataset (requires significant time/space)
python generate_sample_data.py --full
```

Test datasets include:
- GPS points across 50+ countries
- 5,000+ unique vehicles
- Realistic trajectory simulation
- Timestamps from 2022-2025

## Testing

```bash
# Run basic functionality tests
pytest tests/test_basic.py

# Run performance tests
pytest tests/test_performance.py

# Run all tests
pytest tests/

# Run examples
python examples/basic_usage.py

# Benchmark 200M dataset
python examples/benchmark_200M.py
```

## Project Structure

```
polars-gps-hilbert/
├── src/                     # Rust source code
│   ├── lib.rs              # Library entry point
│   ├── expressions.rs      # Polars expression functions
│   ├── gps_hilbert.rs     # Core Hilbert indexing logic
│   └── utils.rs           # Utility functions
├── python/                 # Python bindings
│   └── polars_gps_hilbert/
│       └── __init__.py    # Python API
├── examples/               # Usage examples and benchmarks
│   ├── basic_usage.py     # Basic usage examples
│   ├── generate_sample_data.py  # Dataset generation
│   └── benchmark_200M.py  # Large-scale benchmarks
├── tests/                  # Test suite
│   ├── test_basic.py      # Basic functionality tests
│   ├── test_performance.py # Performance tests
│   └── test_gps_hilbert.py # Legacy comprehensive tests
└── Cargo.toml             # Rust dependencies
```

## Technical Details

- **Hilbert Curves**: Uses the `lindel` crate for efficient 3D Hilbert curve computation
- **Precision**: Configurable bits per dimension (default: 21 bits, 63 total)
- **Bounds**: Auto-computed or pre-specified for optimal performance  
- **Null Handling**: Graceful handling of missing GPS coordinates
- **Validation**: Input validation for GPS coordinate ranges

## Use Cases

1. **Vehicle Trajectory Analysis**: Index millions of GPS points for efficient trajectory reconstruction
2. **Route Deviation Detection**: Quickly identify when vehicles deviate from expected routes
3. **Spatial-Temporal Clustering**: Group nearby points in space and time
4. **Geofencing**: Efficient point-in-region queries
5. **Traffic Pattern Analysis**: Analyze movement patterns across time and space

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on [Polars](https://www.pola.rs/) for high-performance data processing
- Uses [lindel](https://github.com/DoubleHyphen/lindel) for Hilbert curve implementations
- Inspired by spatial indexing techniques in geographic information systems