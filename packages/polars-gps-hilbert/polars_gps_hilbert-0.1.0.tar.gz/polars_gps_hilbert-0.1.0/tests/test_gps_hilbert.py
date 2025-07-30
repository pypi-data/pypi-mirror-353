"""Tests for GPS Hilbert indexing plugin."""

import pytest
import polars as pl
import polars_gps_hilbert as gps


def test_basic_hilbert_index():
    """Test basic Hilbert index computation."""
    df = pl.DataFrame({
        "lat": [37.7749, 34.0522, 40.7128],
        "lon": [-122.4194, -118.2437, -74.0060],
        "ts": [1640995200, 1640998800, 1641002400]
    })
    
    result = df.with_columns(
        gps.hilbert_index("lat", "lon", "ts").alias("idx")
    )
    
    assert "idx" in result.columns
    assert result["idx"].dtype == pl.UInt64
    assert result["idx"].null_count() == 0
    assert len(result["idx"].unique()) == 3  # All indices should be unique for different points


def test_hilbert_index_with_bounds():
    """Test Hilbert index with pre-computed bounds."""
    df = pl.DataFrame({
        "lat": [37.7749, 34.0522, 40.7128],
        "lon": [-122.4194, -118.2437, -74.0060],
        "ts": [1640995200, 1640998800, 1641002400]
    })
    
    bounds = {
        "lat_min": 30.0, "lat_max": 45.0,
        "lon_min": -125.0, "lon_max": -70.0,
        "ts_min": 1640995200, "ts_max": 1641002400
    }
    
    result = df.with_columns(
        gps.hilbert_index("lat", "lon", "ts", bounds=bounds).alias("idx")
    )
    
    assert "idx" in result.columns
    assert result["idx"].dtype == pl.UInt64


def test_compute_bounds():
    """Test bounds computation."""
    df = pl.DataFrame({
        "lat": [37.7749, 34.0522, 40.7128],
        "lon": [-122.4194, -118.2437, -74.0060],
        "ts": [1640995200, 1640998800, 1641002400]
    })
    
    bounds = df.select(gps.compute_bounds("lat", "lon", "ts")).item()
    
    assert bounds["lat_min"] == pytest.approx(34.0522)
    assert bounds["lat_max"] == pytest.approx(40.7128)
    assert bounds["lon_min"] == pytest.approx(-122.4194)
    assert bounds["lon_max"] == pytest.approx(-74.0060)
    assert bounds["ts_min"] == 1640995200
    assert bounds["ts_max"] == 1641002400


def test_null_handling():
    """Test handling of null values."""
    df = pl.DataFrame({
        "lat": [37.7749, None, 40.7128],
        "lon": [-122.4194, -118.2437, None],
        "ts": [1640995200, 1640998800, None]
    })
    
    result = df.with_columns(
        gps.hilbert_index("lat", "lon", "ts").alias("idx")
    )
    
    # Null inputs should produce 0 index
    assert result["idx"][1] == 0
    assert result["idx"][2] == 0


def test_invalid_coordinates():
    """Test handling of invalid GPS coordinates."""
    df = pl.DataFrame({
        "lat": [91.0, -91.0, 45.0],  # Invalid latitudes
        "lon": [181.0, -181.0, 0.0],  # Invalid longitudes
        "ts": [1640995200, 1640998800, 1641002400]
    })
    
    # Should raise an error for invalid coordinates
    with pytest.raises(pl.ComputeError):
        df.with_columns(
            gps.hilbert_index("lat", "lon", "ts").alias("idx")
        )


def test_namespace_api():
    """Test the namespace API."""
    df = pl.DataFrame({
        "latitude": [37.7749, 34.0522, 40.7128],
        "longitude": [-122.4194, -118.2437, -74.0060],
        "timestamp": [1640995200, 1640998800, 1641002400]
    })
    
    result = df.gps_hilbert.compute_and_index()
    
    assert "hilbert_idx" in result.columns
    assert result["hilbert_idx"].dtype == pl.UInt64


def test_lazy_evaluation():
    """Test lazy evaluation."""
    df = pl.DataFrame({
        "latitude": [37.7749, 34.0522, 40.7128],
        "longitude": [-122.4194, -118.2437, -74.0060],
        "timestamp": [1640995200, 1640998800, 1641002400]
    })
    
    lf = df.lazy()
    result = lf.gps_hilbert.compute_and_index()
    
    # Should return a LazyFrame
    assert isinstance(result, pl.LazyFrame)
    
    # Collect and verify
    collected = result.collect()
    assert "hilbert_idx" in collected.columns


def test_different_bit_sizes():
    """Test different bit sizes for precision."""
    df = pl.DataFrame({
        "lat": [37.7749, 37.7750, 37.7751],
        "lon": [-122.4194, -122.4193, -122.4192],
        "ts": [1640995200, 1640995201, 1640995202]
    })
    
    # Test with different bit sizes
    for bits in [10, 15, 21]:
        result = df.with_columns(
            gps.hilbert_index("lat", "lon", "ts", bits_per_dim=bits).alias(f"idx_{bits}")
        )
        assert f"idx_{bits}" in result.columns
        
        # Higher bit sizes should produce more unique indices for close points
        if bits > 10:
            assert len(result[f"idx_{bits}"].unique()) >= len(result[f"idx_10"].unique())


def test_spatial_locality():
    """Test that nearby points have similar Hilbert indices."""
    # Create points in a small area
    df = pl.DataFrame({
        "lat": [37.7749, 37.7750, 37.7751, 40.0, 40.0001, 40.0002],
        "lon": [-122.4194, -122.4193, -122.4192, -74.0, -73.9999, -73.9998],
        "ts": [1640995200] * 6
    })
    
    result = df.with_columns(
        gps.hilbert_index("lat", "lon", "ts").alias("idx")
    )
    
    # Points 0-2 are close to each other, as are points 3-5
    # Their indices should be more similar within groups than across groups
    group1_indices = result["idx"][:3].to_list()
    group2_indices = result["idx"][3:].to_list()
    
    # Calculate average difference within groups
    avg_diff_group1 = sum(abs(group1_indices[i] - group1_indices[j]) 
                          for i in range(3) for j in range(i+1, 3)) / 3
    avg_diff_group2 = sum(abs(group2_indices[i] - group2_indices[j]) 
                          for i in range(3) for j in range(i+1, 3)) / 3
    
    # Calculate average difference between groups
    avg_diff_between = sum(abs(group1_indices[i] - group2_indices[j]) 
                          for i in range(3) for j in range(3)) / 9
    
    # Within-group differences should be smaller than between-group differences
    assert avg_diff_group1 < avg_diff_between
    assert avg_diff_group2 < avg_diff_between