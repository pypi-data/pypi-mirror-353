from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional, Dict, Union

import polars as pl
from polars.plugins import register_plugin_function

if TYPE_CHECKING:
    from polars import Expr

__version__ = "0.1.0"

lib = Path(__file__).parent


def hilbert_index(
    lat_col: str,
    lon_col: str, 
    ts_col: str,
    *,
    bounds: Optional[Dict[str, Union[float, int]]] = None,
    bits_per_dim: int = 21,
) -> Expr:
    """
    Compute 3D Hilbert index for GPS trajectory data.
    
    Parameters
    ----------
    lat_col : str
        Name of the latitude column (float64)
    lon_col : str
        Name of the longitude column (float64)
    ts_col : str
        Name of the timestamp column (int64, unix timestamp)
    bounds : dict, optional
        Pre-computed bounds with keys: lat_min, lat_max, lon_min, lon_max, ts_min, ts_max
        If not provided, bounds will be computed from the data
    bits_per_dim : int, default 21
        Number of bits per dimension (max 21 for 3D to fit in u64)
        
    Returns
    -------
    Expr
        Expression that computes the Hilbert index
        
    Examples
    --------
    >>> df = pl.DataFrame({
    ...     "lat": [37.7749, 34.0522, 40.7128],
    ...     "lon": [-122.4194, -118.2437, -74.0060],
    ...     "ts": [1640995200, 1640998800, 1641002400]
    ... })
    >>> df.with_columns(
    ...     hilbert_idx=hilbert_index("lat", "lon", "ts")
    ... )
    """
    return register_plugin_function(
        plugin_path=lib,
        args=[pl.col(lat_col), pl.col(lon_col), pl.col(ts_col)],
        kwargs={"bounds": bounds, "bits_per_dim": bits_per_dim},
        is_elementwise=True,
        function_name="hilbert_index",
    )


def compute_bounds(
    lat_col: str,
    lon_col: str,
    ts_col: str,
) -> Expr:
    """
    Compute bounds for GPS data.
    
    Parameters
    ----------
    lat_col : str
        Name of the latitude column
    lon_col : str  
        Name of the longitude column
    ts_col : str
        Name of the timestamp column
        
    Returns
    -------
    Expr
        Expression that computes bounds as a struct
        
    Examples
    --------
    >>> df = pl.DataFrame({
    ...     "lat": [37.7749, 34.0522, 40.7128],
    ...     "lon": [-122.4194, -118.2437, -74.0060],
    ...     "ts": [1640995200, 1640998800, 1641002400]
    ... })
    >>> bounds = df.select(compute_bounds("lat", "lon", "ts")).item()
    """
    return register_plugin_function(
        plugin_path=lib,
        args=[pl.col(lat_col), pl.col(lon_col), pl.col(ts_col)],
        is_elementwise=False,
        function_name="compute_bounds",
    )


class HilbertNamespace:
    """Polars namespace for GPS Hilbert operations."""
    
    def __init__(self, df: Union[pl.DataFrame, pl.LazyFrame]):
        self._df = df
    
    def compute_and_index(
        self,
        lat_col: str = "latitude",
        lon_col: str = "longitude", 
        ts_col: str = "timestamp",
        index_col: str = "hilbert_idx",
        bits_per_dim: int = 21,
    ) -> Union[pl.DataFrame, pl.LazyFrame]:
        """
        Compute bounds and apply Hilbert indexing in one operation.
        
        This is optimized for lazy evaluation where bounds are computed
        first, then used for indexing.
        """
        if isinstance(self._df, pl.LazyFrame):
            # For lazy frames, we need to collect bounds first
            bounds_df = self._df.select(
                compute_bounds(lat_col, lon_col, ts_col).alias("bounds")
            ).collect()
            
            bounds_struct = bounds_df["bounds"][0]
            bounds = {
                "lat_min": bounds_struct["lat_min"],
                "lat_max": bounds_struct["lat_max"],
                "lon_min": bounds_struct["lon_min"],
                "lon_max": bounds_struct["lon_max"],
                "ts_min": bounds_struct["ts_min"],
                "ts_max": bounds_struct["ts_max"],
            }
            
            return self._df.with_columns(
                hilbert_index(lat_col, lon_col, ts_col, bounds=bounds, bits_per_dim=bits_per_dim).alias(index_col)
            )
        else:
            # For eager DataFrames
            bounds_struct = self._df.select(
                compute_bounds(lat_col, lon_col, ts_col)
            ).item()
            
            bounds = {
                "lat_min": bounds_struct["lat_min"],
                "lat_max": bounds_struct["lat_max"],
                "lon_min": bounds_struct["lon_min"],
                "lon_max": bounds_struct["lon_max"],
                "ts_min": bounds_struct["ts_min"],
                "ts_max": bounds_struct["ts_max"],
            }
            
            return self._df.with_columns(
                hilbert_index(lat_col, lon_col, ts_col, bounds=bounds, bits_per_dim=bits_per_dim).alias(index_col)
            )


# Register namespace
pl.api.register_dataframe_namespace("gps_hilbert")(HilbertNamespace)
pl.api.register_lazyframe_namespace("gps_hilbert")(HilbertNamespace)