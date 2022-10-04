# Seg2Map Engine :motor_scooter: :dash:

*Common codes for processing geospatial imagery within the Doodleverse*

An idealized Doodleverse workflow could be thought of as :

1. Doodler - which allows operators to annotate imagery
2. Gym - which allows operators to train models with labeled imagery from doodler.
3. Use the trained model to predict segmentations on new imagery.
(and optionally Zoo, which is a way to store Gym models)

As Earth surface scientists, a key objective for us is to push geospatial imagery through this workflow. Geospatial imagery is often in formats that are not innately compatible with tensorflow (i.e., GeoTIFF). Images can also be large (i.e., many pixels in the X and Y). As a result imagery often needs to be processed to be compatible with the Doodleverse. There are two main processing steps which we can think of, and they occur at both ends of the doodler pipeline:
1. Pre-Doodler: large GeoTIFFs need to be tiled (and maybe even resized), and then converted to jpg imagery.
2. Post-Gym: take segmentations and reconstituted a new geotiff with the same size/scale/format of of the original images.

This is where s2m_engine comes into the picture! 

Tentative roadmap:
- Script to read in GeoTiff, split into appropriate size files, and save coordinate info
- Script to read in segmentations, recombine them to make a large, mosaiced segmentation that is a GeoTIFF with the same size/shape as the original geospatial image

...

