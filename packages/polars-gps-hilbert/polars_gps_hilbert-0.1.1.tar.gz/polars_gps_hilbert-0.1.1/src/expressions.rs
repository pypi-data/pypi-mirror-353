use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use serde::Deserialize;

use crate::gps_hilbert::{compute_hilbert_index, compute_hilbert_index_with_bounds, Bounds3D};

#[derive(Deserialize)]
struct HilbertKwargs {
    bounds: Option<Bounds3D>,
    bits_per_dim: Option<u32>,
}

#[polars_expr(output_type=UInt64)]
fn hilbert_index(inputs: &[Series], kwargs: HilbertKwargs) -> PolarsResult<Series> {
    let lat = inputs[0].f64()?;
    let lon = inputs[1].f64()?;
    let ts = inputs[2].i64()?;
    
    let bits = kwargs.bits_per_dim.unwrap_or(21); // Default to 21 bits per dimension (63 total)
    
    match kwargs.bounds {
        Some(bounds) => compute_hilbert_index_with_bounds(lat, lon, ts, bounds, bits),
        None => compute_hilbert_index(lat, lon, ts, bits),
    }
}

#[polars_expr(output_type=Float64)]
fn compute_bounds(inputs: &[Series]) -> PolarsResult<Series> {
    let lat = inputs[0].f64()?;
    let lon = inputs[1].f64()?;
    let ts = inputs[2].i64()?;
    
    let lat_min = lat.min().unwrap_or(f64::NAN);
    let lat_max = lat.max().unwrap_or(f64::NAN);
    let lon_min = lon.min().unwrap_or(f64::NAN);
    let lon_max = lon.max().unwrap_or(f64::NAN);
    let ts_min = ts.min().unwrap_or(0) as f64;
    let ts_max = ts.max().unwrap_or(0) as f64;
    
    // Return simple concatenated bounds as a float series
    let bounds_values = vec![lat_min, lat_max, lon_min, lon_max, ts_min, ts_max];
    Ok(Series::new("bounds".into(), bounds_values))
}