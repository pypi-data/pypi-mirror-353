# fastarray

**fastarray** is a fast, lightweight Python package for preprocessing geospatial optical imagery (e.g., Sentinel-2) to prepare it for machine learning workflows. It simplifies operations like index computation (NDVI, NDWI, etc.), reprojection, patching, and transformation into PyTorch-ready tensors—while preserving geospatial coordinates.

---

## 🚀 Features

- ✅ Compute vegetation and water indices (NDVI, NDWI, etc.)
- ✅ Read raster data into coordinate-aware arrays
- ✅ Clip and reproject rasters using geometries (e.g., GeoJSON or Shapely)
- ✅ Split imagery into fixed-size patches
- ✅ Convert to PyTorch tensors for ML pipelines
- ✅ Fully Pythonic (no heavy GDAL/C++ dependencies)
- ✅ Fast and async-friendly where possible

---

## 📦 Installation

```bash
pip install fastarray

