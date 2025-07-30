#!/usr/bin/env python3
"""Benchmark script for 200M row GPS dataset."""

import polars as pl
import polars_gps_hilbert as gps
import time
import psutil
import os
from pathlib import Path

def benchmark_200M_dataset():
    """Benchmark the plugin on 200M row dataset."""
    print("200 Million Row GPS Dataset Benchmark")
    print("=" * 60)
    
    data_path = Path("gps_trajectories_200M.parquet")
    if not data_path.exists():
        print("❌ 200M row dataset not found!")
        print("Generate it first with: python generate_sample_data.py --full")
        return
    
    # Check file size
    file_size_gb = data_path.stat().st_size / (1024 ** 3)
    print(f"Dataset file size: {file_size_gb:.2f} GB")
    
    # Memory info
    memory = psutil.virtual_memory()
    print(f"Available RAM: {memory.total / (1024**3):.1f} GB")
    print(f"Free RAM: {memory.free / (1024**3):.1f} GB")
    
    if file_size_gb > memory.free / (1024**3) * 0.8:
        print("⚠️  Dataset is large relative to available RAM - using lazy evaluation")
        use_lazy = True
    else:
        print("✅ Sufficient RAM available for eager evaluation")
        use_lazy = False
    
    print()
    
    if use_lazy:
        benchmark_lazy_200M(data_path)
    else:
        benchmark_eager_200M(data_path)

def benchmark_lazy_200M(data_path):
    """Benchmark using lazy evaluation."""
    print("🚀 Lazy Evaluation Benchmark")
    print("-" * 40)
    
    # Create lazy frame
    lf = pl.scan_parquet(data_path)
    
    # Test 1: Index and filter to smaller subset
    print("Test 1: Index + Filter (to 10M rows)")
    start_time = time.time()
    
    result = lf.with_columns(
        gps.hilbert_index("latitude", "longitude", "timestamp").alias("hilbert_idx")
    ).filter(
        pl.col("vehicle_id") < 250  # Should give us ~10M rows (5% of vehicles)
    ).collect()
    
    elapsed = time.time() - start_time
    
    print(f"   Processed: {len(result):,} rows")
    print(f"   Time: {elapsed:.2f} seconds")
    print(f"   Throughput: {len(result) / elapsed:,.0f} rows/second")
    print(f"   Memory usage: {psutil.Process().memory_info().rss / (1024**2):.0f} MB")
    
    # Test 2: Spatial query
    print("\nTest 2: Spatial Query (Hilbert range)")
    start_time = time.time()
    
    # Use the indexed result for spatial query
    sorted_result = result.sort("hilbert_idx")
    reference_idx = sorted_result["hilbert_idx"][len(sorted_result)//2]
    range_size = 10_000_000
    
    spatial_query = sorted_result.filter(
        (pl.col("hilbert_idx") >= reference_idx - range_size) &
        (pl.col("hilbert_idx") <= reference_idx + range_size)
    )
    
    elapsed = time.time() - start_time
    
    print(f"   Found: {len(spatial_query):,} nearby points")
    print(f"   Query time: {elapsed:.3f} seconds")
    
    # Check spatial locality
    if len(spatial_query) > 0:
        lat_range = spatial_query["latitude"].max() - spatial_query["latitude"].min()
        lon_range = spatial_query["longitude"].max() - spatial_query["longitude"].min()
        countries = spatial_query["country"].n_unique()
        
        print(f"   Spatial locality:")
        print(f"     Lat range: {lat_range:.4f}°")
        print(f"     Lon range: {lon_range:.4f}°") 
        print(f"     Countries: {countries}")

def benchmark_eager_200M(data_path):
    """Benchmark using eager evaluation (if RAM allows)."""
    print("🏃 Eager Evaluation Benchmark")
    print("-" * 40)
    
    # Load full dataset
    print("Loading 200M rows into memory...")
    start_time = time.time()
    df = pl.read_parquet(data_path)
    load_time = time.time() - start_time
    
    print(f"   Load time: {load_time:.2f} seconds")
    print(f"   Dataset size: {len(df):,} rows")
    print(f"   Memory usage: {psutil.Process().memory_info().rss / (1024**2):.0f} MB")
    
    # Index the full dataset
    print("\nIndexing 200M rows...")
    start_time = time.time()
    
    indexed = df.with_columns(
        gps.hilbert_index("latitude", "longitude", "timestamp").alias("hilbert_idx")
    )
    
    index_time = time.time() - start_time
    
    print(f"   Index time: {index_time:.2f} seconds")
    print(f"   Throughput: {len(indexed) / index_time:,.0f} rows/second")
    print(f"   Memory usage: {psutil.Process().memory_info().rss / (1024**2):.0f} MB")
    
    # Quick spatial locality test
    print("\nTesting spatial locality...")
    sorted_df = indexed.sort("hilbert_idx")
    dataset_size = len(sorted_df)
    
    # Take slice from middle, but ensure it's within bounds
    start_idx = min(dataset_size // 2, dataset_size - 1000)
    slice_size = min(1000, dataset_size - start_idx)
    slice_df = sorted_df.slice(start_idx, slice_size)
    
    if len(slice_df) > 0:
        lat_range = slice_df["latitude"].max() - slice_df["latitude"].min()
        lon_range = slice_df["longitude"].max() - slice_df["longitude"].min()
        countries = slice_df["country"].n_unique()
        
        print(f"   {len(slice_df)} consecutive Hilbert indices:")
        print(f"     Lat range: {lat_range:.4f}°")
        print(f"     Lon range: {lon_range:.4f}°")
        print(f"     Countries: {countries}")
    else:
        print("   No data available for spatial locality test")

def benchmark_streaming():
    """Benchmark streaming/chunked processing."""
    print("\n🌊 Streaming Processing Benchmark")
    print("-" * 40)
    
    data_path = Path("gps_trajectories_200M.parquet")
    if not data_path.exists():
        print("❌ 200M row dataset not found!")
        return
    
    # Process in chunks
    chunk_size = 5_000_000  # 5M rows per chunk
    total_processed = 0
    total_time = 0
    
    print(f"Processing in {chunk_size:,} row chunks...")
    
    # Read parquet file info to estimate number of chunks
    lf = pl.scan_parquet(data_path)
    # We'll process first 50M rows in chunks as a demo
    demo_rows = 50_000_000
    num_chunks = demo_rows // chunk_size
    
    for chunk_num in range(num_chunks):
        offset = chunk_num * chunk_size
        print(f"   Chunk {chunk_num + 1}/{num_chunks} (rows {offset:,} - {offset + chunk_size:,})")
        
        start_time = time.time()
        
        # Process chunk
        chunk_result = lf.slice(offset, chunk_size).with_columns(
            gps.hilbert_index("latitude", "longitude", "timestamp").alias("hilbert_idx")
        ).collect()
        
        chunk_time = time.time() - start_time
        chunk_throughput = len(chunk_result) / chunk_time
        
        print(f"     Processed: {len(chunk_result):,} rows in {chunk_time:.2f}s ({chunk_throughput:,.0f} rows/sec)")
        
        total_processed += len(chunk_result)
        total_time += chunk_time
    
    print(f"\nStreaming Summary:")
    print(f"   Total processed: {total_processed:,} rows")
    print(f"   Total time: {total_time:.2f} seconds")
    print(f"   Average throughput: {total_processed / total_time:,.0f} rows/second")

if __name__ == "__main__":
    print("Starting 200M Row Benchmark...")
    print("Make sure you have sufficient disk space and time!")
    print()
    
    benchmark_200M_dataset()
    benchmark_streaming()
    
    print("\n" + "=" * 60)
    print("Benchmark completed!")
    print("=" * 60)