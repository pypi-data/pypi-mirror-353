use polars::prelude::*;

pub fn validate_gps_data(lat: &Float64Chunked, lon: &Float64Chunked) -> PolarsResult<()> {
    // Basic validation for GPS coordinates
    for val in lat.into_iter().flatten() {
        if val < -90.0 || val > 90.0 {
            return Err(PolarsError::ComputeError(
                format!("Invalid latitude value: {}", val).into(),
            ));
        }
    }
    
    for val in lon.into_iter().flatten() {
        if val < -180.0 || val > 180.0 {
            return Err(PolarsError::ComputeError(
                format!("Invalid longitude value: {}", val).into(),
            ));
        }
    }
    
    Ok(())
}