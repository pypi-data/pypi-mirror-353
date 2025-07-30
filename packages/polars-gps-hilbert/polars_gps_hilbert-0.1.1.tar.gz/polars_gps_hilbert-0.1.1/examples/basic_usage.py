#!/usr/bin/env python3
"""Basic usage examples for polars-gps-hilbert plugin."""

import polars as pl
import polars_gps_hilbert as gps

def example_basic_indexing():
    """Basic Hilbert indexing example."""
    print("=== Basic Hilbert Indexing ===")
    
    # Create sample GPS data
    df = pl.DataFrame({
        "vehicle_id": [1, 1, 1, 2, 2, 2],
        "latitude": [37.7749, 37.7751, 37.7753, 34.0522, 34.0524, 34.0526],
        "longitude": [-122.4194, -122.4192, -122.4190, -118.2437, -118.2435, -118.2433],
        "timestamp": [1640995200, 1640995230, 1640995260, 1640995200, 1640995230, 1640995260],
    })
    
    print("Original data:")
    print(df)
    
    # Add Hilbert index
    result = df.with_columns(
        gps.hilbert_index("latitude", "longitude", "timestamp").alias("hilbert_idx")
    )
    
    print("\nWith Hilbert index:")
    print(result)
    
    return result

def example_with_bounds():
    """Example using pre-computed bounds for better performance."""
    print("\n=== Using Pre-computed Bounds ===")
    
    df = pl.DataFrame({
        "latitude": [37.7749, 34.0522, 40.7128],
        "longitude": [-122.4194, -118.2437, -74.0060],
        "timestamp": [1640995200, 1640998800, 1641002400]
    })
    
    # Pre-compute bounds for your dataset
    bounds = {
        "lat_min": 30.0, "lat_max": 45.0,
        "lon_min": -125.0, "lon_max": -70.0,
        "ts_min": 1640995200, "ts_max": 1641002400
    }
    
    result = df.with_columns(
        gps.hilbert_index("latitude", "longitude", "timestamp", bounds=bounds).alias("hilbert_idx")
    )
    
    print("With pre-computed bounds:")
    print(result)
    
    return result

def example_lazy_evaluation():
    """Example using lazy evaluation for large datasets."""
    print("\n=== Lazy Evaluation ===")
    
    # Create some sample data and save to parquet
    df = pl.DataFrame({
        "vehicle_id": [i % 10 for i in range(1000)],
        "latitude": [37.7749 + (i % 100) * 0.001 for i in range(1000)],
        "longitude": [-122.4194 + (i % 100) * 0.001 for i in range(1000)],
        "timestamp": [1640995200 + i * 30 for i in range(1000)],
    })
    
    df.write_parquet("sample_gps_data.parquet")
    
    # Use lazy evaluation
    lf = pl.scan_parquet("sample_gps_data.parquet")
    
    # Apply indexing and filtering lazily
    result = lf.with_columns(
        gps.hilbert_index("latitude", "longitude", "timestamp").alias("hilbert_idx")
    ).filter(
        pl.col("vehicle_id") < 5
    ).collect()
    
    print(f"Processed {len(result)} points lazily:")
    print(result.head())
    
    # Clean up
    import os
    os.remove("sample_gps_data.parquet")
    
    return result

def example_spatial_queries():
    """Example showing spatial queries using Hilbert indices."""
    print("\n=== Spatial Queries ===")
    
    # Create data with geographic clusters
    import random
    data = []
    
    # Cluster 1: San Francisco area
    for i in range(100):
        data.append({
            "point_id": i,
            "latitude": 37.7749 + random.uniform(-0.01, 0.01),
            "longitude": -122.4194 + random.uniform(-0.01, 0.01),
            "timestamp": 1640995200 + i * 30
        })
    
    # Cluster 2: Los Angeles area  
    for i in range(100, 200):
        data.append({
            "point_id": i,
            "latitude": 34.0522 + random.uniform(-0.01, 0.01),
            "longitude": -118.2437 + random.uniform(-0.01, 0.01),
            "timestamp": 1640995200 + i * 30
        })
    
    df = pl.DataFrame(data)
    
    # Add Hilbert indices
    indexed = df.with_columns(
        gps.hilbert_index("latitude", "longitude", "timestamp").alias("hilbert_idx")
    ).sort("hilbert_idx")
    
    print(f"Created {len(indexed)} points in 2 geographic clusters")
    
    # Find nearby points using Hilbert index range
    reference_idx = indexed["hilbert_idx"][50]  # Pick a point from SF cluster
    range_size = 1000000
    
    nearby = indexed.filter(
        (pl.col("hilbert_idx") >= reference_idx - range_size) &
        (pl.col("hilbert_idx") <= reference_idx + range_size)
    )
    
    print(f"\nFound {len(nearby)} nearby points using Hilbert index range:")
    print(nearby.select(["point_id", "latitude", "longitude", "hilbert_idx"]).head())
    
    # Check spatial locality
    lat_range = nearby["latitude"].max() - nearby["latitude"].min()
    lon_range = nearby["longitude"].max() - nearby["longitude"].min()
    
    print(f"\nSpatial locality check:")
    print(f"Latitude range: {lat_range:.4f} degrees")
    print(f"Longitude range: {lon_range:.4f} degrees")
    
    return indexed

if __name__ == "__main__":
    print("Polars GPS Hilbert Indexing Examples")
    print("=" * 50)
    
    example_basic_indexing()
    example_with_bounds()
    example_lazy_evaluation()
    example_spatial_queries()
    
    print("\n" + "=" * 50)
    print("Examples completed!")