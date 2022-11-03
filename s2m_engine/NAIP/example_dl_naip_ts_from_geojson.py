# Written by Dr Daniel Buscombe, Marda Science LLC
# for the USGS Coastal Change Hazards Program
#
# MIT License
#
# Copyright (c) 2022, Marda Science LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# For a list of polygons in a geojson file

# 1. download all the 0.5-m NAIP imagery. Bands downloaded separately and as a multiband geotiff
# 1a. If the imagery is larger than an allowable GEE data packet (33MB), region is quartered and each quarter

import geemap,ee #, reverse_geocoder
import os, json , shutil
from ipyleaflet import GeoJSON
import numpy as np
from glob import glob
from area import area
from joblib import Parallel, delayed

from shapely.geometry import LineString, MultiPolygon, Polygon
from shapely.ops import split



##  ogr2ogr -t_srs EPSG:4326 -f GEOJSON elwhaMR_epsg4326.geojson elwhaMR.geojson

with open('example.geojson') as f:
    json_data = json.load(f)

features = json_data['features'][0]

MAXCLOUD = 5  #percentage maximum cloud cover tolerated

###=================================================
############### NAIP #########################
###=================================================
gee_collection = 'USDA/NAIP/DOQQ'

OUT_RES_M = 0.5 #1

nx, ny = 4,4 # number of columns and rows
site = 'elwhaMR'


for year in ['2006', '2009','2011','2013','2015','2017']:

    start_date = year+'-01-01'
    end_date = year+'-12-31'

    try:
        os.mkdir('naip'+year)
    except:
        pass

    try:
        os.mkdir('naip'+year+os.sep+site)
    except:
        pass

    # initialize Earth Engine
    # ee.Authenticate()
    ee.Initialize()

    coordinates = features['geometry']['coordinates'][0]
    lng, lat = np.mean(coordinates[0], axis=0)
    print((lng, lat))
    area_sqkm = area(features['geometry'])/1e6
    #print(area_sqkm)

    collection = ee.ImageCollection(gee_collection)

    polygon = Polygon([tuple(c) for c in coordinates[0]])
    minx, miny, maxx, maxy = polygon.bounds

    dx = (maxx - minx) / nx  # width of a small part
    dy = (maxy - miny) / ny  # height of a small part
    horizontal_splitters = [LineString([(minx, miny + i*dy), (maxx, miny + i*dy)]) for i in range(ny)]
    vertical_splitters = [LineString([(minx + i*dx, miny), (minx + i*dx, maxy)]) for i in range(nx)]
    splitters = horizontal_splitters + vertical_splitters

    result = polygon
    for splitter in splitters:
        result = MultiPolygon(split(result, splitter))
    parts = [list(part.exterior.coords) for part in result.geoms]

    print("Number of individual tiles: {}".format(len(parts)))

    counter = 1
    for part in parts:
        print(counter)
        try:
            os.mkdir('naip'+year+os.sep+str(site)+os.sep+'chunk'+str(counter))
        except:
            pass

        print(area({'type':'Polygon','coordinates': [[list(p) for p in part]]})/1e6)
        collection = ee.ImageCollection(gee_collection)

        polys = ee.Geometry.Polygon(part)

        centroid = polys.centroid()
        lng, lat = centroid.getInfo()['coordinates']
        #print("lng = {}, lat = {}".format(lng, lat))

        #lng_lat = ee.Geometry.Point(lng, lat)
        collection = collection.filterBounds(polys)
        collection = collection.filterDate(start_date, end_date).sort('system:time_start', True)
        count = collection.size().getInfo()
        #print("Number of cloudy scenes: ", count)
        img_lst = collection.toList(1000)

        N = []
        for i in range(0, count):
            image = ee.Image(img_lst.get(i))
            name = image.get('system:index').getInfo()
            N.append(name)
            print(name)

        for n in N:
            image = ee.Image('USDA/NAIP/DOQQ/'+n)
            #geemap.ee_export_image(image, os.getcwd()+os.sep+'site_'+str(site)+'_'+n+'_part_'+str(counter)+'_of_'+str(len(parts))+'.tif', scale=OUT_RES_M, region=polys, file_per_band=True)
            geemap.ee_export_image(image, os.getcwd()+os.sep+'naip'+year+os.sep+str(site)+os.sep+'chunk'+str(counter)+os.sep+'chunk'+str(counter)+'_'+n+'.tif', scale=OUT_RES_M, region=polys, file_per_band=True, crs="EPSG:4326")
            geemap.ee_export_image(image, os.getcwd()+os.sep+'naip'+year+os.sep+str(site)+os.sep+'chunk'+str(counter)+os.sep+'chunk'+str(counter)+'_'+n+'_multiband.tif', scale=OUT_RES_M, region=polys, file_per_band=False, crs="EPSG:4326")

        counter += 1


    # move multiband files into own directory

    outdirec = os.getcwd()+os.sep+'naip'+year+os.sep+str(site)+os.sep+'multiband'
    try:
        os.mkdir( outdirec)
    except:
        pass

    for folder in glob( os.getcwd()+os.sep+'naip'+year+os.sep+site+os.sep+'chunk*', recursive=True ):
        # print(folder)
        files = glob(folder+os.sep+'*multiband.tif')
        # print(files)
        [shutil.copyfile(file,outdirec+os.sep+file.split(os.sep)[-1]) for file in files]


    # ## run gdal to merge into big tiff 
    # os.system('gdalbuildvrt -srcnodata 0 -vrtnodata 0 tmp.vrt '+outdirec+os.sep+'*.tif')
    # os.system('gdal_translate tmp.vrt mosaic.tif -co BIGTIFF=YES  -co COMPRESS=DEFLATE -co TILED=YES')

