#!/usr/bin/env python3
"""Efficient 200M GPS trajectory data generator using streaming writes."""

import polars as pl
from datetime import datetime, timedelta
import random
import os

# Countries with their approximate lat/lon boundaries
COUNTRIES = {
    "USA": {"lat": (25.0, 49.0), "lon": (-125.0, -66.0)},
    "Canada": {"lat": (41.0, 83.0), "lon": (-141.0, -52.0)},
    "Mexico": {"lat": (14.0, 33.0), "lon": (-118.0, -86.0)},
    "Brazil": {"lat": (-34.0, 5.0), "lon": (-74.0, -34.0)},
    "UK": {"lat": (50.0, 59.0), "lon": (-8.0, 2.0)},
    "France": {"lat": (42.0, 51.0), "lon": (-5.0, 8.0)},
    "Germany": {"lat": (47.0, 55.0), "lon": (6.0, 15.0)},
    "Spain": {"lat": (36.0, 44.0), "lon": (-9.0, 3.0)},
    "Italy": {"lat": (37.0, 47.0), "lon": (7.0, 19.0)},
    "Poland": {"lat": (49.0, 55.0), "lon": (14.0, 24.0)},
    "Russia": {"lat": (41.0, 82.0), "lon": (19.0, 169.0)},
    "China": {"lat": (18.0, 54.0), "lon": (73.0, 135.0)},
    "Japan": {"lat": (24.0, 46.0), "lon": (123.0, 146.0)},
    "India": {"lat": (8.0, 37.0), "lon": (68.0, 97.0)},
    "Australia": {"lat": (-44.0, -10.0), "lon": (113.0, 154.0)},
    "South Africa": {"lat": (-35.0, -22.0), "lon": (16.0, 33.0)},
    "Egypt": {"lat": (22.0, 32.0), "lon": (25.0, 35.0)},
    "Nigeria": {"lat": (4.0, 14.0), "lon": (3.0, 15.0)},
    "Kenya": {"lat": (-5.0, 5.0), "lon": (34.0, 42.0)},
    "Argentina": {"lat": (-55.0, -22.0), "lon": (-74.0, -53.0)},
    "Chile": {"lat": (-56.0, -17.0), "lon": (-76.0, -66.0)},
    "Peru": {"lat": (-18.0, 0.0), "lon": (-81.0, -68.0)},
    "Colombia": {"lat": (-4.0, 13.0), "lon": (-79.0, -66.0)},
    "Venezuela": {"lat": (0.0, 12.0), "lon": (-73.0, -59.0)},
    "Thailand": {"lat": (6.0, 21.0), "lon": (97.0, 106.0)},
    "Vietnam": {"lat": (8.0, 24.0), "lon": (102.0, 110.0)},
    "Indonesia": {"lat": (-11.0, 6.0), "lon": (95.0, 141.0)},
    "Philippines": {"lat": (5.0, 21.0), "lon": (117.0, 127.0)},
    "Malaysia": {"lat": (1.0, 7.0), "lon": (100.0, 119.0)},
    "Singapore": {"lat": (1.2, 1.5), "lon": (103.6, 104.0)},
    "South Korea": {"lat": (33.0, 39.0), "lon": (124.0, 132.0)},
    "Turkey": {"lat": (36.0, 42.0), "lon": (26.0, 45.0)},
    "Saudi Arabia": {"lat": (16.0, 32.0), "lon": (34.0, 56.0)},
    "UAE": {"lat": (22.0, 26.0), "lon": (51.0, 57.0)},
    "Israel": {"lat": (29.0, 33.0), "lon": (34.0, 36.0)},
    "Iran": {"lat": (25.0, 40.0), "lon": (44.0, 64.0)},
    "Pakistan": {"lat": (24.0, 37.0), "lon": (61.0, 77.0)},
    "Bangladesh": {"lat": (21.0, 27.0), "lon": (88.0, 93.0)},
    "Myanmar": {"lat": (10.0, 28.0), "lon": (92.0, 102.0)},
    "New Zealand": {"lat": (-47.0, -34.0), "lon": (166.0, 179.0)},
    "Norway": {"lat": (58.0, 71.0), "lon": (5.0, 31.0)},
    "Sweden": {"lat": (55.0, 69.0), "lon": (11.0, 24.0)},
    "Finland": {"lat": (60.0, 70.0), "lon": (20.0, 32.0)},
    "Denmark": {"lat": (54.0, 58.0), "lon": (8.0, 15.0)},
    "Netherlands": {"lat": (50.0, 54.0), "lon": (3.0, 7.0)},
    "Belgium": {"lat": (49.0, 52.0), "lon": (2.0, 6.0)},
    "Switzerland": {"lat": (45.0, 48.0), "lon": (6.0, 11.0)},
    "Austria": {"lat": (46.0, 49.0), "lon": (9.0, 17.0)},
    "Portugal": {"lat": (37.0, 42.0), "lon": (-10.0, -6.0)},
    "Czech Republic": {"lat": (48.0, 51.0), "lon": (12.0, 19.0)},
    "Hungary": {"lat": (45.0, 49.0), "lon": (16.0, 23.0)},
    "Romania": {"lat": (43.0, 48.0), "lon": (20.0, 30.0)},
    "Bulgaria": {"lat": (41.0, 44.0), "lon": (22.0, 28.0)},
    "Greece": {"lat": (34.0, 42.0), "lon": (19.0, 30.0)},
    "Croatia": {"lat": (42.0, 47.0), "lon": (13.0, 19.0)},
}

def generate_vehicle_trajectory(vehicle_id: int, country: str, start_time: datetime, num_points: int, sampling_rate_seconds: int = 30) -> pl.DataFrame:
    """Generate GPS trajectory for a single vehicle."""
    bounds = COUNTRIES[country]
    
    # Start from a random point in the country
    lat = random.uniform(bounds["lat"][0], bounds["lat"][1])
    lon = random.uniform(bounds["lon"][0], bounds["lon"][1])
    
    lats = []
    lons = []
    timestamps = []
    
    current_time = start_time
    
    # Simulate vehicle movement
    for _ in range(num_points):
        # Add some noise and movement
        lat += random.gauss(0, 0.001)  # ~100m movement
        lon += random.gauss(0, 0.001)
        
        # Keep within country bounds
        lat = max(bounds["lat"][0], min(bounds["lat"][1], lat))
        lon = max(bounds["lon"][0], min(bounds["lon"][1], lon))
        
        lats.append(lat)
        lons.append(lon)
        timestamps.append(int(current_time.timestamp()))
        
        current_time += timedelta(seconds=sampling_rate_seconds)
    
    return pl.DataFrame({
        "vehicle_id": [vehicle_id] * num_points,
        "latitude": lats,
        "longitude": lons,
        "timestamp": timestamps,
        "country": [country] * num_points,
    })

def generate_200M_dataset():
    """Generate 200M row dataset efficiently using separate parquet files."""
    total_rows = 200_000_000
    num_vehicles = 5000
    chunk_size = 10_000_000  # 10M rows per chunk file
    
    print(f"Generating {total_rows:,} GPS trajectory points...")
    print(f"Vehicles: {num_vehicles:,}")
    print(f"Countries: {len(COUNTRIES)}")
    print(f"Chunk size: {chunk_size:,} rows")
    
    # Distribute vehicles across countries
    vehicles_per_country = num_vehicles // len(COUNTRIES)
    remaining_vehicles = num_vehicles % len(COUNTRIES)
    
    vehicle_country_map = {}
    vehicle_id = 0
    
    for i, country in enumerate(COUNTRIES.keys()):
        count = vehicles_per_country + (1 if i < remaining_vehicles else 0)
        for _ in range(count):
            vehicle_country_map[vehicle_id] = country
            vehicle_id += 1
    
    # Calculate points per vehicle
    avg_points_per_vehicle = total_rows // num_vehicles
    
    # Start time range: 2022-01-01 to 2025-01-01
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2025, 1, 1)
    
    rows_generated = 0
    chunk_dfs = []
    chunk_num = 0
    chunk_files = []
    
    for vehicle_id, country in vehicle_country_map.items():
        # Random start time for this vehicle
        start_time = start_date + timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        
        # Vary the number of points per vehicle
        num_points = int(random.gauss(avg_points_per_vehicle, avg_points_per_vehicle * 0.2))
        num_points = max(100, min(num_points, avg_points_per_vehicle * 2))
        
        if rows_generated + num_points > total_rows:
            num_points = total_rows - rows_generated
        
        df = generate_vehicle_trajectory(vehicle_id, country, start_time, num_points)
        chunk_dfs.append(df)
        rows_generated += num_points
        
        # Write chunk to separate file when it gets large
        if sum(len(df) for df in chunk_dfs) >= chunk_size:
            chunk_df = pl.concat(chunk_dfs)
            chunk_file = f"gps_chunk_{chunk_num:03d}.parquet"
            chunk_df.write_parquet(chunk_file)
            chunk_files.append(chunk_file)
            chunk_dfs = []
            chunk_num += 1
            
            print(f"Progress: {rows_generated:,} / {total_rows:,} rows ({rows_generated/total_rows*100:.1f}%) - Wrote {chunk_file}")
        
        if rows_generated >= total_rows:
            break
    
    # Write remaining data
    if chunk_dfs:
        chunk_df = pl.concat(chunk_dfs)
        chunk_file = f"gps_chunk_{chunk_num:03d}.parquet"
        chunk_df.write_parquet(chunk_file)
        chunk_files.append(chunk_file)
        print(f"Progress: {rows_generated:,} / {total_rows:,} rows (100.0%) - Wrote {chunk_file}")
    
    print(f"\nGenerated {rows_generated:,} GPS points")
    print(f"Created {len(chunk_files)} chunk files:")
    
    total_size = 0
    for chunk_file in chunk_files:
        size = os.path.getsize(chunk_file) / (1024 * 1024)  # MB
        total_size += size
        print(f"  {chunk_file}: {size:.1f} MB")
    
    print(f"Total dataset size: {total_size:.1f} MB ({total_size/1024:.1f} GB)")
    
    # Create a single combined file for easier testing
    print(f"\nCombining all chunks into final dataset...")
    all_chunks = [pl.scan_parquet(f) for f in chunk_files]
    combined = pl.concat(all_chunks)
    combined.sink_parquet("gps_trajectories_200M.parquet")
    
    # Print some statistics
    df = pl.scan_parquet("gps_trajectories_200M.parquet")
    print(f"\nFinal dataset statistics:")
    print(f"Total rows: {df.select(pl.len()).collect().item():,}")
    print(f"Unique vehicles: {df.select(pl.col('vehicle_id').n_unique()).collect().item():,}")
    print(f"Unique countries: {df.select(pl.col('country').n_unique()).collect().item():,}")
    
    bounds = df.select([
        pl.col("latitude").min().alias("lat_min"),
        pl.col("latitude").max().alias("lat_max"),
        pl.col("longitude").min().alias("lon_min"),
        pl.col("longitude").max().alias("lon_max"),
        pl.col("timestamp").min().alias("ts_min"),
        pl.col("timestamp").max().alias("ts_max"),
    ]).collect()
    
    print(f"\nBounds:")
    print(f"Latitude: [{bounds['lat_min'][0]:.4f}, {bounds['lat_max'][0]:.4f}]")
    print(f"Longitude: [{bounds['lon_min'][0]:.4f}, {bounds['lon_max'][0]:.4f}]")
    print(f"Timestamp: [{bounds['ts_min'][0]} - {bounds['ts_max'][0]}]")
    
    ts_min = datetime.fromtimestamp(bounds['ts_min'][0])
    ts_max = datetime.fromtimestamp(bounds['ts_max'][0])
    print(f"Date range: {ts_min.date()} to {ts_max.date()}")
    
    # Clean up chunk files
    print(f"\nCleaning up {len(chunk_files)} temporary chunk files...")
    for chunk_file in chunk_files:
        os.remove(chunk_file)
    
    final_size = os.path.getsize("gps_trajectories_200M.parquet") / (1024 * 1024 * 1024)  # GB
    print(f"Final file: gps_trajectories_200M.parquet ({final_size:.1f} GB)")

if __name__ == "__main__":
    print("Efficient 200M GPS Trajectory Generator")
    print("=" * 50)
    
    response = input("⚠️  This will generate 200M GPS points (~8-10 GB). Continue? (y/N): ")
    if response.lower() == 'y':
        generate_200M_dataset()
        print("\n" + "=" * 50)
        print("🎉 200M dataset generation completed!")
        print("Ready for testing with: python benchmark_200M.py")
    else:
        print("Cancelled.")