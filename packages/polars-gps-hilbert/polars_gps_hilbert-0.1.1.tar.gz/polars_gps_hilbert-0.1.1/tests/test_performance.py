#!/usr/bin/env python3
"""Performance tests for GPS Hilbert indexing plugin."""

import polars as pl
import polars_gps_hilbert as gps
import time
import pytest
from pathlib import Path

def test_throughput_small_dataset():
    """Test throughput on small dataset."""
    # Create 10k points
    import random
    data = []
    for i in range(10000):
        data.append({
            "latitude": random.uniform(30.0, 45.0),
            "longitude": random.uniform(-120.0, -70.0),
            "timestamp": 1640995200 + i * 30
        })
    
    df = pl.DataFrame(data)
    
    start_time = time.time()
    result = df.with_columns(
        gps.hilbert_index("latitude", "longitude", "timestamp").alias("hilbert_idx")
    )
    elapsed = time.time() - start_time
    
    throughput = len(result) / elapsed
    
    # Should process at least 100k points per second
    assert throughput > 100_000
    assert len(result["hilbert_idx"].unique()) > 9000  # Most should be unique

def test_memory_efficiency():
    """Test memory efficiency of indexing."""
    # Create 5k points
    import random
    data = []
    for i in range(5000):
        data.append({
            "latitude": random.uniform(30.0, 45.0),
            "longitude": random.uniform(-120.0, -70.0),
            "timestamp": 1640995200 + i * 30
        })
    
    df = pl.DataFrame(data)
    original_size = df.estimated_size()
    
    indexed = df.with_columns(
        gps.hilbert_index("latitude", "longitude", "timestamp").alias("hilbert_idx")
    )
    
    indexed_size = indexed.estimated_size()
    overhead = (indexed_size - original_size) / len(df)
    
    # Should be close to 8 bytes per index (u64)
    assert 7 <= overhead <= 10

def test_bounds_performance():
    """Test performance difference between auto and pre-computed bounds."""
    import random
    data = []
    for i in range(1000):
        data.append({
            "latitude": random.uniform(30.0, 45.0),
            "longitude": random.uniform(-120.0, -70.0),
            "timestamp": 1640995200 + i * 30
        })
    
    df = pl.DataFrame(data)
    
    # Auto bounds
    start_time = time.time()
    result1 = df.with_columns(
        gps.hilbert_index("latitude", "longitude", "timestamp").alias("hilbert_idx")
    )
    time_auto = time.time() - start_time
    
    # Pre-computed bounds
    bounds = {
        "lat_min": 30.0, "lat_max": 45.0,
        "lon_min": -120.0, "lon_max": -70.0,
        "ts_min": 1640995200, "ts_max": 1640995200 + 1000 * 30
    }
    
    start_time = time.time()
    result2 = df.with_columns(
        gps.hilbert_index("latitude", "longitude", "timestamp", bounds=bounds).alias("hilbert_idx")
    )
    time_pre = time.time() - start_time
    
    # Both should complete in reasonable time
    assert time_auto < 1.0
    assert time_pre < 1.0

@pytest.mark.slow
def test_large_dataset_performance():
    """Test performance on larger dataset (marked as slow test)."""
    pytest.skip("Skipping slow test - run manually for performance testing")
    
    # This would test with 100k+ points
    # Only run when specifically testing performance