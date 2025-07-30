use lindel::*;
use polars::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Bounds3D {
    pub lat_min: f64,
    pub lat_max: f64,
    pub lon_min: f64,
    pub lon_max: f64,
    pub ts_min: f64,  // Accept as f64 and convert internally
    pub ts_max: f64,  // Accept as f64 and convert internally
}

fn normalize_value(value: f64, min: f64, max: f64, max_val: u32) -> u32 {
    if max == min {
        return 0;
    }
    let normalized = (value - min) / (max - min);
    (normalized * max_val as f64).clamp(0.0, max_val as f64) as u32
}

fn normalize_timestamp(ts: i64, min: f64, max: f64, max_val: u32) -> u32 {
    if max == min {
        return 0;
    }
    let normalized = (ts as f64 - min) / (max - min);
    (normalized * max_val as f64).clamp(0.0, max_val as f64) as u32
}

pub fn compute_hilbert_index_with_bounds(
    lat: &Float64Chunked,
    lon: &Float64Chunked,
    ts: &Int64Chunked,
    bounds: Bounds3D,
    bits_per_dim: u32,
) -> PolarsResult<Series> {
    let max_val = (1u32 << bits_per_dim) - 1;
    
    let indices: Vec<u64> = lat
        .into_iter()
        .zip(lon.into_iter())
        .zip(ts.into_iter())
        .map(|((lat_opt, lon_opt), ts_opt)| {
            match (lat_opt, lon_opt, ts_opt) {
                (Some(lat), Some(lon), Some(ts)) => {
                    let x = normalize_value(lat, bounds.lat_min, bounds.lat_max, max_val);
                    let y = normalize_value(lon, bounds.lon_min, bounds.lon_max, max_val);
                    let z = normalize_timestamp(ts, bounds.ts_min, bounds.ts_max, max_val);
                    
                    let point = [x, y, z];
                    point.hilbert_index() as u64
                }
                _ => 0u64, // Handle null values
            }
        })
        .collect();
    
    Ok(Series::new("hilbert_index".into(), indices))
}

pub fn compute_hilbert_index(
    lat: &Float64Chunked,
    lon: &Float64Chunked,
    ts: &Int64Chunked,
    bits_per_dim: u32,
) -> PolarsResult<Series> {
    // Compute bounds from the data
    let lat_min = lat.min().unwrap_or(-90.0);
    let lat_max = lat.max().unwrap_or(90.0);
    let lon_min = lon.min().unwrap_or(-180.0);
    let lon_max = lon.max().unwrap_or(180.0);
    let ts_min = ts.min().unwrap_or(0);
    let ts_max = ts.max().unwrap_or(i64::MAX);
    
    let bounds = Bounds3D {
        lat_min,
        lat_max,
        lon_min,
        lon_max,
        ts_min: ts_min as f64,  // Convert to f64 for consistency
        ts_max: ts_max as f64,  // Convert to f64 for consistency
    };
    
    compute_hilbert_index_with_bounds(lat, lon, ts, bounds, bits_per_dim)
}