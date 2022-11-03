# 📦 Seg2Map Engine :motor_scooter: :dash:

*Common codes for processing geospatial imagery within the Doodleverse*

An idealized Doodleverse workflow could be thought of as :

1. Doodler - which allows operators to annotate imagery
2. Gym - which allows operators to train models with labeled imagery from doodler.
3. Use the trained model to predict segmentations on new imagery.

As Earth surface scientists, a key objective for us is to push geospatial imagery through this workflow. Geospatial imagery is often in formats that are not innately compatible with tensorflow (i.e., GeoTIFF). Images can also be large (i.e., many pixels in the X and Y). As a result imagery often needs to be processed to be compatible with the Doodleverse. There are main processing steps which we can think of, and they occur at both ends of the doodler pipeline:
1. Pre-Doodler: large GeoTIFFs need to be tiled (and maybe even resized), and then converted to jpg imagery.
2. Pre-Doodler: programmatically access GeoTIFFs for doodling using geemap
3. Post-Gym: take segmentations and reconstituted a new geotiff with the same size/scale/format of of the original images.

This is where s2m_engine comes into the picture! 

Tentative roadmap:
- Script to read in GeoTiff, split into appropriate size files, and save coordinate info
- Script to read in segmentations, recombine them to make a large, mosaiced segmentation that is a GeoTIFF with the same size/shape as the original geospatial image
- Script to download GeoTIFF imagery. We will start with NAIP imagery
- Others to be detailed at a later date
...

This repo is intended to eventually be a pip installable package, hosted on pypi.org. This follows an established practice in the Doodleverse; individual applications such as Gym and Doodler outsource their core functionality to a pip-installable package for two reasons:

1. several downstream applications can use the same core functionality. This is already in evidence with [DashDoodler's](https://github.com/Doodleverse/dash_doodler) and [HoloDoodler](https://github.com/Doodleverse/holodoodler) usage of the [doodler_engine](https://github.com/Doodleverse/doodler_engine) codes, and Gym's and Zoo's common usage of the [doodleverse-utils](https://github.com/Doodleverse/doodleverse_utils) codes. Similarly, this `s2m_engine` repo is designed to work with the (future) [Seg2Map](https://github.com/Doodleverse/seg2map) and [MorphoSedimentaryMapper](https://github.com/dbuscombe-usgs/MorphoSedimentaryMapper) applications
2. these pip repositories have no specified dependencies; they are intended to be installed into an existing environment specific to the intended application. That could be a conda environment, python virtual environment, or something similar where `pip` packages can be installed

However, for interim testing and development purposes, for conda users, the following conda workflow could be temporarily adopted. These are geospatial workflows so `geopandas` and `shapely` are generally useful for data wrangling like format conversions and reprojecting. `earthengine-api` and `geemap` are suggested for easily accessing geospatial imagery. This also installs `gdal` from OSGeo. This is a crucial dependency, but is hidden in the conda recipe below. `notebook` provides access to IDEs `jupyter` and `ipython` (but vscode, spyder, etc, etc, could alternatively be used)

```
conda create -n s2m_dev python=3.8
conda activate s2m_dev
conda install -c conda-forge geopandas earthengine-api scikit-image matplotlib notebook geemap shapely -y
pip install area
```

Use of `ee` and `geemap` require installation of the [gcloud cli](https://cloud.google.com/sdk/docs/install#deb). Then you must run `earthengine authenticate` and sign in with your google account. This is free and requires only a gmail address