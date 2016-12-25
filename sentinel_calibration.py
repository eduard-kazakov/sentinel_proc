# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 01:46:12 2016

@author: ekazakov
"""
import xml.etree.ElementTree
import numpy as np
from scipy import interpolate, ndimage
from osgeo import gdal
import os

GDALWARP_PATH = '\"C:\Program Files\QGIS 2.16\OSGeo4W.bat\" gdalwarp '

def save_array_as_geotiff_gcp_mode (input_array, output_path, base_raster):
    print 'writing file ' + str(output_path) + '...'
    cols = base_raster.RasterXSize
    rows = base_raster.RasterYSize
    
    bands = 1
    cell_type = gdal.GDT_Float32
    driver_name = 'GTiff'
    driver = gdal.GetDriverByName(driver_name)
    #projection = base_raster.GetProjection()
    #transform = base_raster.GetGeoTransform()
    
    #transform = gdal.GCPsToGeoTransform(base_raster.GetGCPs())
    gcps = base_raster.GetGCPs()
    #gcps_count = base_raster.GetGCPCount ()
    gcps_projection = base_raster.GetGCPProjection ()
    out_data = driver.Create(output_path,cols,rows,bands,cell_type)
    #out_data.SetProjection (projection)
    #out_data.SetGeoTransform (transform)
    out_data.SetGCPs(gcps,gcps_projection)
    out_data.GetRasterBand(1).WriteArray (input_array)
    
def resave_geotiff_with_gdalwarp (input_geotiff_path, output_geotiff_path, t_srs, nodata):
    #gdalwarp -overwrite -t_srs EPSG:4326 -dstnodata 0 -of GTiff E:/dzz_mag/bolivia/LC82310722016225LGN00/LC82310722016225LGN00_B3.TIF E:/dzz_mag/bolivia/LC82310722016225LGN00/asd.tif
    cmd = GDALWARP_PATH + '-t_srs ' + t_srs + ' -dstnodata ' + str(nodata) + ' -of GTiff ' + input_geotiff_path + ' ' + output_geotiff_path
    print cmd
    os.system(cmd)

def fill_nan(A):
    B = A
    ok = ~np.isnan(B)
    xp = ok.ravel().nonzero()[0]
    fp = B[~np.isnan(B)]
    x  = np.isnan(B).ravel().nonzero()[0]
    B[np.isnan(B)] = np.interp(x, xp, fp)
    return B

def get_coefficients_array (xml_path, xml_element_name, xml_attribute_name, cols, rows):
    coefficients_rows = []
    e = xml.etree.ElementTree.parse(xml_path).getroot()
    print 'reading data...'
    for noiseVectorList in e.findall(xml_element_name):
        for child in noiseVectorList:
            for param in child:
                if param.tag == 'pixel':
                    currentPixels = str(param.text).split()
                if param.tag == xml_attribute_name:
                    currentValues = str(param.text).split()
                
            i = 0
            currentRow = np.empty([1,cols])
            currentRow[:] = np.nan
            while i < len(currentPixels):
                currentRow[0,int(currentPixels[i])] = float(currentValues[i])
                i += 1
            
                
            currentRow = fill_nan(currentRow)
            
            coefficients_rows.append(currentRow[0])
            
    print 'interpolating data...'
    zoom_x = float(cols) / len(coefficients_rows[0])
    zoom_y = float(rows) / len (coefficients_rows)
    return ndimage.zoom(coefficients_rows,[zoom_y,zoom_x])
 
def perform_radiometric_calibration (input_tiff_path, calibration_xml_path, output_tiff_path):
    
    measurement_file = gdal.Open(input_tiff_path)
    measurement_file_array = np.array(measurement_file.GetRasterBand(1).ReadAsArray().astype(np.float32))
    
    radiometric_coefficients_array = get_coefficients_array(calibration_xml_path,'calibrationVectorList','sigmaNought',measurement_file.RasterXSize,measurement_file.RasterYSize)
    print 'radiometric calibration...'
    calibrated_array = (measurement_file_array * measurement_file_array) / (radiometric_coefficients_array * radiometric_coefficients_array)
    
    save_array_as_geotiff_gcp_mode (calibrated_array, output_tiff_path, measurement_file)

    
    
def perform_noise_correction (input_tiff_path, calibration_xml_path, noise_xml_path, output_tiff_path):
    measurement_file = gdal.Open(input_tiff_path)
    measurement_file_array = np.array(measurement_file.GetRasterBand(1).ReadAsArray().astype(np.float32))
    
    radiometric_coefficients_array = get_coefficients_array(calibration_xml_path,'calibrationVectorList','sigmaNought',measurement_file.RasterXSize,measurement_file.RasterYSize)
    noise_coefficients_array = get_coefficients_array(noise_xml_path,'noiseVectorList','noiseLut',measurement_file.RasterXSize,measurement_file.RasterYSize)
    print 'noise correction...'
    noise_corrected_array = (measurement_file_array * measurement_file_array - noise_coefficients_array) / (radiometric_coefficients_array * radiometric_coefficients_array)
    save_array_as_geotiff_gcp_mode (noise_corrected_array, output_tiff_path, measurement_file)
    

#perform_noise_correction ('s1a-iw-grd-vh-20160117t042516-20160117t042541-009529-00dd75-002.tiff','calibr_sample.xml','noise_sample.xml','noise_calibrated.tiff')
#perform_radiometric_calibration ('s1a-iw-grd-vh-20160117t042516-20160117t042541-009529-00dd75-002.tiff','calibr_sample.xml','calibrate_new.tiff')
#resave_geotiff_with_gdalwarp ('calibrate_new.tiff','calibrate_new_rs.tiff','EPSG:4326',0)
#a = get_coefficients_array('calibr_sample.xml','calibrationVectorList','sigmaNought',26284,16682)
#print a