@ECHO OFF
SETLOCAL ENABLEEXTENSIONS
SETLOCAL ENABLEDELAYEDEXPANSION
REM the name of the script
SET me=%~n0
REM the directory where the script lives                 
SET parent=%~dp0
SET "src_dir=%cd%"


REM to use GDAL commands you must first run the command C:\users\resarwas\gdal\SDKShell.bat
REM Run this from the directory to translate
REM need to make a folder called 'new' first

FOR %%f in (*.tif) DO (

    SET "src=%%f"
    SET "dest=new\%%f"

    REM remove the alpha band, define the no data value, use internal tiling (to load only portion of image) and compress (lossless)
    REM sometimes compression (especially LZW on natural color images) is larger (and slower), so compare
    REM use -a_srs {srs_def} to define the spatial reference system of the output file (no projection is done).  easiest to use WKID (i.e 4326 = WGS84, 4269 = GCS_North_American_1983)
    REM use -of GTIFF -co TILED=YES to create a geotiff with internal tiles (to improve image load times)
    REM use -a_nodata {value} to specify a no data value to all bands.  65535
    REM use -b to select a subset of bands from the source, and the ordering in the output i.e. -b 4 -b 3 -b 3 omits band 1 and puts band 4 as the first output band; band numbering starts with 1
    REM use -co COMPRESS=LZW for lossless compression.
    REM see https://www.gdal.org/gdal_translate.html for additional options to gdal_translate

    gdal_translate -of GTIFF -b 1 -b 2 -b 3 -a_nodata 65535 -co COMPRESS=LZW -co TILED=YES !src! !dest!

    REM add internal overviews
    REM see https://www.gdal.org/gdaladdo.html for additional information
    REM The mumber of levels depends on how many pixels are in the image.  The smallest overview should be ~ 256x256
    REM for the smallest possible JPEG-In-TIFF overviews, use: --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR
    REM for monochrome geotiffs use: 
    REM -r is the resample method,  nearest is the default
    REM use -ro to open the image as readonly and create external overviews (*.ovr), otherwise geotiff will create internal overviews
    REM The advised level values should be 2, 4, 8, ... so that a 3x3 resampling Gaussian kernel is selected

    gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average !dest! 2 4 8 16 32

    REM add stats;  the hist option generates a histogram which is stored in a *.tif.aux.xml sidecar file with ArcGIS needs
    gdalinfo -stats -hist !dest!
)
