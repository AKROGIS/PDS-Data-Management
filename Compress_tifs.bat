@ECHO OFF
SETLOCAL ENABLEEXTENSIONS
SETLOCAL ENABLEDELAYEDEXPANSION
REM the name of the script
SET me=%~n0
REM the directory where the script lives                 
SET parent=%~dp0
SET "src_dir=%cd%"


REM to use GDAL commands you must first run the command C:\users\resarewas\gdal\SDKShell.bat
REM Run this from the directory to translate
REM need to make a folder called 'new' first

FOR %%f in (*.tif) DO (

    SET "src=%%f"
    SET "dest=new\%%f"

    REM remove the alpha band, define the no data value, use internal tiling (to load only portion of image) and compress (lossless)
    REM sometimes compression (especially LZW on natural color images) is larger (and slower), so compare
    gdal_translate -of GTIFF -b 1 -b 2 -b 3 -a_nodata 65535 -co COMPRESS=LZW -co TILED=YES !src! !dest!

    REM add internal overviews The mumber of levels depends on how many pixels are in the image.  The smallest overview should be ~ 256x256
    gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average !dest! 2 4 8 16 32

    REM add stats;  the hist option generates a histogram which is stored in a *.tif.aux.xml sidecar file with ArcGIS needs
    gdalinfo -stats -hist !dest!
)
