# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 23:16:43 2016

@author: ekazakov
"""

from osgeo import gdal
import math
import os
import numpy as np
GDALWARP_PATH = '\"C:\Program Files\QGIS 2.16\OSGeo4W.bat\" gdalwarp '

def cut_raster_with_shp (raster_path, shp_path, output_path, nodata_value = 'Null'):
    #gdalwarp -dstnodata 0 -q -cutline E:\spb.shp -crop_to_cutline -tr 0.000169734933651 0.000169734933651 -of GTiff E:/sentinel_processing/calibrate_new_rs.tiff E:/sentinel_processing/new.tif    
    #inputRaster = gdal.Open(raster_path)
    ##tr_x = inputRaster.XResolution
    #tr_y = inputRaster.YResolution
    cmd = GDALWARP_PATH + '-dstnodata ' + nodata_value + ' -q -cutline ' + shp_path + ' -crop_to_cutline -of GTiff ' + raster_path + ' ' + output_path
    #print dir(inputRaster.GetRasterBand(1))
    os.system(cmd)
    
def raster_unique_values_count(inputRaster, roundValuesToNDigits=None):
    # load raster
    gdalData = gdal.Open(str(inputRaster))

    # get width and heights of the raster
    xsize = gdalData.RasterXSize
    ysize = gdalData.RasterYSize

    # get number of bands
    bands = gdalData.RasterCount

    uniqueValuesDicts = []

    # process the raster
    for i in xrange(1, bands + 1):
        band_i = gdalData.GetRasterBand(i)
        raster = band_i.ReadAsArray()

        # create dictionary for unique values count
        count = {}

        # count unique values for the given band
        for col in range(xsize):
            for row in range(ysize):
                cell_value = raster[row, col]

                # check if cell_value is NaN
                if math.isnan(cell_value):
                    cell_value = 'Null'

                # round floats if needed
                elif roundValuesToNDigits:
                    try:
                        cell_value = round(cell_value, int(roundValuesToNDigits))
                    except:
                        cell_value = round(cell_value)

                # add cell_value to dictionary
                try:
                    count[cell_value] += 1
                except:
                    count[cell_value] = 1

    uniqueValuesDicts.append(count)
    return uniqueValuesDicts
    
def raster_all_values(inputRaster, nodata = 0.0, write_to_file = None):
    # load raster
    gdalData = gdal.Open(str(inputRaster))
    xsize = gdalData.RasterXSize
    ysize = gdalData.RasterYSize

    # get number of bands
    bands = gdalData.RasterCount
    pixel_values = []
    # process the raster
    for i in xrange(1, bands + 1):
        band_i = gdalData.GetRasterBand(i)
        raster = band_i.ReadAsArray()
        # create dictionary for unique values count
        

        # count unique values for the given band
        for col in range(xsize):
            for row in range(ysize):
                cell_value = raster[row, col]
                if math.isnan(cell_value) or (cell_value == nodata):
                    pass
                else:
                    pixel_values.append(cell_value)
    
    if write_to_file:
        writer = open(write_to_file,'w')
        i = 0
        while i < len(pixel_values):
            writer.write(str(i) + ';' + str(pixel_values[i])+'\n')
            i += 1
    return pixel_values
    
raster_all_values('demo_1_xc_haralick_9.tif',np.nan,'test3.csv')
#cut_raster_with_shp('calibrate_new_rs.tiff','spb.shp','test.tiff','Null')