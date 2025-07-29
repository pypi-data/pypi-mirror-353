"""Data export module for pollution data."""

import json
import logging
from enum import Enum
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import xarray as xr
from rasterio.crs import CRS
from rasterio.transform import Affine

logger = logging.getLogger(__name__)


class ExportFormat(str, Enum):
    """Supported export formats."""

    CSV = "csv"
    GEOJSON = "geojson"
    SHAPEFILE = "shapefile"
    NETCDF = "netcdf"
    GEOTIFF = "geotiff"
    JSON = "json"


class AggregationMethod(str, Enum):
    """Supported aggregation methods."""

    MEAN = "mean"
    MAX = "max"
    MIN = "min"
    SUM = "sum"


@runtime_checkable
class SpatialData(Protocol):
    """Protocol for spatial data types."""

    def to_crs(self, crs: Any) -> "SpatialData":
        """Reproject spatial data to the specified CRS.

        Parameters
        ----------
        crs : Any
            Target coordinate reference system.

        Returns
        -------
        SpatialData
            Reprojected spatial data.

        """
        ...

    def to_file(self, filename: str, driver: str = "GeoJSON") -> None:
        """Export spatial data to a file.

        Parameters
        ----------
        filename : str
            Path to the output file.
        driver : str, optional
            File format driver, by default "GeoJSON".

        """
        ...


def ensure_path(path: str | Path) -> Path:
    """Ensure path exists and return Path object."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def aggregate_data(data: xr.DataArray, method: str, dim: str = "time") -> xr.DataArray:
    """Aggregate data along a dimension using specified method."""
    method = AggregationMethod(method)
    if method == AggregationMethod.MEAN:
        return data.mean(dim=dim)
    if method == AggregationMethod.MAX:
        return data.max(dim=dim)
    if method == AggregationMethod.MIN:
        return data.min(dim=dim)
    if method == AggregationMethod.SUM:
        return data.sum(dim=dim)
    raise ValueError(f"Unsupported aggregation method: {method}")


def get_crs(dataset: xr.Dataset, default: str = "EPSG:3035") -> CRS:
    """Get CRS from dataset or return default."""
    if "crs" in dataset:
        crs_wkt = dataset.crs.attrs.get("crs_wkt", "")
        if crs_wkt:
            try:
                return CRS.from_wkt(crs_wkt)
            except Exception as e:
                logger.warning(f"Could not parse CRS from WKT ({e!s}), using {default}")
    return CRS.from_string(default)


def create_transform(x_coords: np.ndarray, y_coords: np.ndarray) -> tuple:
    """Calculate transform for GeoTIFF."""
    x_res = x_coords[1] - x_coords[0]
    y_res = y_coords[1] - y_coords[0]
    return Affine.translation(
        x_coords[0] - x_res / 2, y_coords[0] - y_res / 2
    ) * Affine.scale(x_res, y_res)


def select_time_data(
    data: xr.DataArray,
    time_index: int | str | slice,
    aggregation_method: str | None = None,
) -> xr.DataArray:
    """Select and potentially aggregate time data."""
    if isinstance(time_index, slice):
        data = data.sel(time=time_index)
        if aggregation_method:
            data = aggregate_data(data, aggregation_method)
        else:
            data = data.isel(time=0)
    elif isinstance(time_index, str):
        data = data.sel(time=time_index, method="nearest")
    else:
        data = data.isel(time=time_index)
    return data


class DataExporter:
    """Class for exporting pollution data to various formats.

    Supports export to NetCDF, GeoTIFF, CSV, GeoJSON, Shapefile, and other formats.
    """

    def __init__(self, dataset: xr.Dataset, pollution_variable: str):
        """Initialize the data exporter.

        Parameters
        ----------
        dataset : xr.Dataset
            The pollution dataset
        pollution_variable : str
            Name of the pollution variable to export

        """
        self.dataset = dataset
        self.pollution_variable = pollution_variable

    def to_netcdf(
        self,
        output_path: str | Path,
        time_subset: slice | None = None,
        spatial_subset: dict | None = None,
        compression: dict[str, Any] | None = None,
    ) -> None:
        """Export data to NetCDF format.

        Parameters
        ----------
        output_path : str or Path
            Output file path
        time_subset : slice, optional
            Time subset to export
        spatial_subset : dict, optional
            Spatial subset bounds
        compression : dict, optional
            Compression parameters for NetCDF

        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Apply subsets
        data = self.dataset.copy()

        if time_subset:
            data = data.sel(time=time_subset)

        if spatial_subset:
            data = data.sel(
                x=slice(spatial_subset.get("minx"), spatial_subset.get("maxx")),
                y=slice(spatial_subset.get("miny"), spatial_subset.get("maxy")),
            )

        # Set up compression
        if compression is None:
            compression = {"zlib": True, "complevel": 4}

        encoding = {var: compression for var in data.data_vars}

        # Export
        data.to_netcdf(output_path, encoding=encoding)
        logger.info(f"Data exported to NetCDF: {output_path}")

    def _get_time_subset_data(
        self,
        data: xr.DataArray,
        time_index: int | str | slice,
        aggregation_method: str | None = None,
    ) -> xr.DataArray:
        """Get a time subset of the data with optional aggregation.

        Parameters
        ----------
        data : xr.DataArray
            Input data array
        time_index : int, str, or slice
            Time index/slice to select
        aggregation_method : str, optional
            Method to aggregate data over time dimension

        Returns
        -------
        xr.DataArray
            Subset and potentially aggregated data

        """
        if isinstance(time_index, slice):
            data = data.sel(time=time_index)
            if aggregation_method:
                if aggregation_method == "mean":
                    data = data.mean(dim="time")
                elif aggregation_method == "max":
                    data = data.max(dim="time")
                elif aggregation_method == "min":
                    data = data.min(dim="time")
                elif aggregation_method == "sum":
                    data = data.sum(dim="time")
                else:
                    raise ValueError(f"Unsupported aggregation: {aggregation_method}")
            else:
                data = data.isel(time=0)
        elif isinstance(time_index, str):
            data = data.sel(time=time_index, method="nearest")
        else:
            data = data.isel(time=time_index)
        return data

    def _get_transform(self, x_coords: np.ndarray, y_coords: np.ndarray) -> tuple:
        """Calculate transform for GeoTIFF.

        Parameters
        ----------
        x_coords : np.ndarray
            X coordinates
        y_coords : np.ndarray
            Y coordinates

        Returns
        -------
        tuple
            Transform matrix for GeoTIFF

        """
        x_res = x_coords[1] - x_coords[0]
        y_res = y_coords[1] - y_coords[0]

        return Affine.translation(
            x_coords[0] - x_res / 2,
            y_coords[0] - y_res / 2,
        ) * Affine.scale(x_res, y_res)

    def _get_crs(self) -> CRS:
        """Get CRS from dataset or return default.

        Returns
        -------
        CRS
            Coordinate reference system

        """
        if "crs" in self.dataset:
            crs_wkt = self.dataset.crs.attrs.get("crs_wkt", "")
            if crs_wkt:
                try:
                    return CRS.from_wkt(crs_wkt)
                except Exception as e:
                    logger.warning(
                        f"Could not parse CRS from WKT ({e!s}), using EPSG:3035"
                    )
            return CRS.from_epsg(3035)  # Default LAEA Europe
        return CRS.from_epsg(3035)  # Default LAEA Europe

    def to_geotiff(
        self,
        output_path: str | Path,
        time_index: int | str | slice = 0,
        aggregation_method: str | None = None,
        nodata_value: float = -9999.0,
        compress: str = "lzw",
        dtype: str = "float32",
    ) -> None:
        """Export data to GeoTIFF format.

        Parameters
        ----------
        output_path : str or Path
            Output file path
        time_index : int, str, or slice
            Time index/slice to export
        aggregation_method : str, optional
            Temporal aggregation method if time_index is a slice
        nodata_value : float
            NoData value for the GeoTIFF
        compress : str
            Compression method
        dtype : str
            Data type for the output

        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Process data
        data = self._get_time_subset_data(
            self.dataset[self.pollution_variable], time_index, aggregation_method
        )

        # Get spatial information
        transform = self._get_transform(data.x.values, data.y.values)
        crs = self._get_crs()

        # Prepare data array
        data_array = data.values

        # Handle NaN values
        data_array = np.where(np.isnan(data_array), nodata_value, data_array)

        # Convert data type
        data_array = data_array.astype(dtype)

        # Write GeoTIFF
        with rasterio.open(
            output_path,
            "w",
            driver="GTiff",
            height=data_array.shape[0],
            width=data_array.shape[1],
            count=1,
            dtype=dtype,
            crs=crs,
            transform=transform,
            nodata=nodata_value,
            compress=compress,
            tiled=True,
            blockxsize=256,
            blockysize=256,
        ) as dst:
            # Write data
            dst.write(data_array, 1)

            # Write metadata
            metadata = {
                "pollution_variable": self.pollution_variable,
                "source_file": str(getattr(self.dataset, "source", "")),
                "creation_date": pd.Timestamp.now().isoformat(),
            }

            # Add time information
            if hasattr(data, "time"):
                if data.time.size == 1:
                    metadata["time"] = pd.to_datetime(data.time.values).isoformat()
                else:
                    start_time = pd.to_datetime(data.time.values[0]).isoformat()
                    end_time = pd.to_datetime(data.time.values[-1]).isoformat()
                    metadata["time_range"] = f"{start_time} to {end_time}"
                    if aggregation_method:
                        metadata["temporal_aggregation"] = aggregation_method

            # Add variable attributes
            if hasattr(data, "attrs"):
                for key, value in data.attrs.items():
                    if isinstance(value, str | int | float):
                        metadata[key] = str(value)

            dst.update_tags(**metadata)

        logger.info(f"Data exported to GeoTIFF: {output_path}")

    def to_csv(
        self,
        output_path: str | Path,
        include_coordinates: bool = True,
        time_format: str = "%Y-%m-%d",
        spatial_aggregation: str | None = None,
    ) -> None:
        """Export data to CSV format.

        Parameters
        ----------
        output_path : str or Path
            Output file path
        include_coordinates : bool
            Whether to include x, y coordinates
        time_format : str
            Time format string
        spatial_aggregation : str, optional
            Spatial aggregation method ('mean', 'max', 'min', 'sum')

        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = self.dataset[self.pollution_variable]

        if spatial_aggregation:
            # Aggregate spatially
            if spatial_aggregation == "mean":
                data = data.mean(dim=["x", "y"])
            elif spatial_aggregation == "max":
                data = data.max(dim=["x", "y"])
            elif spatial_aggregation == "min":
                data = data.min(dim=["x", "y"])
            elif spatial_aggregation == "sum":
                data = data.sum(dim=["x", "y"])

            # Convert to DataFrame
            df = data.to_dataframe().reset_index()

        else:
            # Convert to DataFrame with all spatial points
            df = data.to_dataframe().reset_index()

        # Format time column
        if "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"]).dt.strftime(time_format)

        # Remove coordinate columns if not needed
        if not include_coordinates and spatial_aggregation:
            coord_cols = ["x", "y"]
            df = df.drop(columns=[col for col in coord_cols if col in df.columns])

        # Export
        df.to_csv(output_path, index=False)
        logger.info(f"Data exported to CSV: {output_path}")

    def extracted_points_to_formats(
        self,
        extracted_data: xr.Dataset,
        output_dir: str | Path,
        formats: list[str] | None = None,
        base_filename: str = "extracted_points",
    ) -> dict[str, Path]:
        """Export extracted point data to multiple formats."""
        if formats is None:
            formats = ["csv", "geojson"]
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_paths = {}

        # Convert to DataFrame
        df = extracted_data.to_dataframe().reset_index()

        # Export to CSV
        if "csv" in formats:
            csv_path = output_dir / f"{base_filename}.csv"
            df.to_csv(csv_path, index=False)
            output_paths["csv"] = csv_path

        # Export to GeoJSON
        if "geojson" in formats:
            from shapely.geometry import Point

            geometry = [
                Point(row.x, row.y)
                for _, row in df.iterrows()
                if "x" in row and "y" in row
            ]
            gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:3035")
            geojson_path = output_dir / f"{base_filename}.geojson"
            gdf.to_file(geojson_path, driver="GeoJSON")
            output_paths["geojson"] = geojson_path

        logger.info(f"Extracted point data exported to: {list(output_paths.values())}")
        return output_paths

    def extracted_polygons_to_formats(
        self,
        extracted_data: xr.Dataset,
        original_polygons: gpd.GeoDataFrame,
        output_dir: str | Path,
        formats: list[str] | None = None,
        base_filename: str = "extracted_polygons",
    ) -> dict[str, Path]:
        """Export extracted polygon data to multiple formats.

        Parameters
        ----------
        extracted_data : xr.Dataset
            Extracted polygon data
        original_polygons : gpd.GeoDataFrame
            Original polygon boundaries
        output_dir : str or Path
            Output directory
        formats : list of str
            List of output formats
        base_filename : str
            Base filename for outputs

        Returns
        -------
        dict
            Dictionary mapping format names to output file paths

        """
        if formats is None:
            formats = ["csv", "geojson"]
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_paths = {}

        # Convert to DataFrame
        df = extracted_data.to_dataframe().reset_index()

        # Create summary DataFrame
        summary_df = (
            df.groupby("polygon_id")
            .agg({self.pollution_variable: ["mean", "min", "max", "std", "count"]})
            .round(4)
        )

        # Flatten column names
        summary_df.columns = [
            "_".join(col).strip() for col in summary_df.columns.values
        ]
        summary_df = summary_df.reset_index()

        # Merge with original polygon attributes
        if len(original_polygons) == len(summary_df):
            # Add polygon attributes (excluding geometry)
            polygon_attrs = original_polygons.drop(columns=["geometry"]).reset_index(
                drop=True
            )
            summary_df = pd.concat([summary_df, polygon_attrs], axis=1)

        # Export to different formats
        if "csv" in formats:
            csv_path = output_dir / f"{base_filename}.csv"
            df.to_csv(csv_path, index=False)
            output_paths["csv"] = csv_path

            # Also export summary
            summary_csv_path = output_dir / f"{base_filename}_summary.csv"
            summary_df.to_csv(summary_csv_path, index=False)
            output_paths["csv_summary"] = summary_csv_path

        if "geojson" in formats:
            # Create GeoDataFrame with polygon geometries
            if len(original_polygons) == len(summary_df):
                gdf = gpd.GeoDataFrame(
                    summary_df,
                    geometry=original_polygons.geometry.values,
                    crs=original_polygons.crs,
                )

                geojson_path = output_dir / f"{base_filename}.geojson"
                gdf.to_file(geojson_path, driver="GeoJSON")
                output_paths["geojson"] = geojson_path

        if "shapefile" in formats:
            # Create GeoDataFrame with polygon geometries
            if len(original_polygons) == len(summary_df):
                gdf = gpd.GeoDataFrame(
                    summary_df,
                    geometry=original_polygons.geometry.values,
                    crs=original_polygons.crs,
                )

                shapefile_path = output_dir / f"{base_filename}.shp"
                gdf.to_file(shapefile_path, driver="ESRI Shapefile")
                output_paths["shapefile"] = shapefile_path

        logger.info(
            f"Extracted polygon data exported to: {list(output_paths.values())}"
        )
        return output_paths

    def time_series_to_formats(
        self,
        time_series_data: xr.Dataset,
        output_dir: str | Path,
        formats: list[str] | None = None,
        base_filename: str = "time_series",
    ) -> dict[str, Path]:
        """Export time series data to multiple formats.

        Parameters
        ----------
        time_series_data : xr.Dataset
            Time series data
        output_dir : str or Path
            Output directory
        formats : list of str
            List of output formats
        base_filename : str
            Base filename for outputs

        Returns
        -------
        dict
            Dictionary mapping format names to output file paths

        """
        if formats is None:
            formats = ["csv"]
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_paths = {}

        # Convert to DataFrame
        df = time_series_data.to_dataframe().reset_index()

        # Export to different formats
        if "csv" in formats:
            csv_path = output_dir / f"{base_filename}.csv"
            df.to_csv(csv_path, index=False)
            output_paths["csv"] = csv_path

        if "json" in formats:
            json_path = output_dir / f"{base_filename}.json"
            df.to_json(json_path, orient="records", date_format="iso")
            output_paths["json"] = json_path

        logger.info(f"Time series data exported to: {list(output_paths.values())}")
        return output_paths

    def create_metadata_file(
        self, output_path: str | Path, processing_info: dict[str, Any] | None = None
    ) -> None:
        """Create a metadata file for the exported data.

        Parameters
        ----------
        output_path : str or Path
            Output path for metadata file
        processing_info : dict, optional
            Additional processing information

        """
        output_path = Path(output_path)

        # Collect metadata
        metadata = {
            "dataset_info": {
                "pollution_variable": self.pollution_variable,
                "dimensions": dict(self.dataset.dims),
                "coordinates": list(self.dataset.coords),
                "time_range": {
                    "start": pd.to_datetime(self.dataset.time.values[0]).isoformat(),
                    "end": pd.to_datetime(self.dataset.time.values[-1]).isoformat(),
                },
                "spatial_bounds": {
                    "x_min": float(self.dataset.x.min()),
                    "x_max": float(self.dataset.x.max()),
                    "y_min": float(self.dataset.y.min()),
                    "y_max": float(self.dataset.y.max()),
                },
            },
            "variable_attributes": dict(self.dataset[self.pollution_variable].attrs),
            "global_attributes": dict(self.dataset.attrs),
            "export_info": {
                "export_date": pd.Timestamp.now().isoformat(),
                "software": "dss-pollution-extraction",
            },
        }

        # Add processing information
        if processing_info:
            metadata["processing_info"] = processing_info

        # Add CRS information
        if "crs" in self.dataset:
            metadata["coordinate_system"] = dict(self.dataset.crs.attrs)

        # Write metadata
        with open(output_path, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Metadata file created: {output_path}")
