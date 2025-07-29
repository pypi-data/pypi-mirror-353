# fastArray/io.py
from shapely.geometry import shape, mapping
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
import rasterio

def clip_raster(path: str, geojson_geom: dict, dst_crs: str = None):
    """Clips raster to geojson geometry and reprojects to dst_crs if given."""
    with rasterio.open(path) as src:
        if dst_crs:
            transform, width, height = calculate_default_transform(
                src.crs, dst_crs, src.width, src.height, *src.bounds)
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': dst_crs,
                'transform': transform,
                'width': width,
                'height': height
            })

            dst = np.empty((src.count, height, width), dtype=src.dtypes[0])
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=dst[i - 1],
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)
            return dst

        else:
            out_image, _ = mask(src, [geojson_geom], crop=True)
            return out_image
