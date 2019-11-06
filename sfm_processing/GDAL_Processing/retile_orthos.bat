gdal_translate -of GTIFF  -srcwin     0     0 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-0-0.tif new\2018_Bear_Gl_ORTHO-0-0.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-0-0.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-0-0.tif
gdal_translate -of GTIFF  -srcwin     0 10000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-0-0.tif new\2018_Bear_Gl_ORTHO-0-1.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-0-1.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-0-1.tif
gdal_translate -of GTIFF  -srcwin 10000     0 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-0-0.tif new\2018_Bear_Gl_ORTHO-1-0.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-1-0.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-1-0.tif
gdal_translate -of GTIFF  -srcwin 10000 10000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-0-0.tif new\2018_Bear_Gl_ORTHO-1-1.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-1-1.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-1-1.tif

gdal_translate -of GTIFF  -srcwin     0     0 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-0-1.tif new\2018_Bear_Gl_ORTHO-0-2.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-0-2.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-0-2.tif
gdal_translate -of GTIFF  -srcwin     0 10000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-0-1.tif new\2018_Bear_Gl_ORTHO-0-3.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-0-3.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-0-3.tif
gdal_translate -of GTIFF  -srcwin 10000     0 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-0-1.tif new\2018_Bear_Gl_ORTHO-1-2.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-1-2.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-1-2.tif
gdal_translate -of GTIFF  -srcwin 10000 10000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-0-1.tif new\2018_Bear_Gl_ORTHO-1-3.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-1-3.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-1-3.tif

gdal_translate -of GTIFF  -srcwin     0     0 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-0-2.tif new\2018_Bear_Gl_ORTHO-0-4.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-0-4.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-0-4.tif
gdal_translate -of GTIFF  -srcwin     0 10000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-0-2.tif new\2018_Bear_Gl_ORTHO-0-5.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-0-5.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-0-5.tif
gdal_translate -of GTIFF  -srcwin 10000     0 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-0-2.tif new\2018_Bear_Gl_ORTHO-1-4.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-1-4.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-1-4.tif
gdal_translate -of GTIFF  -srcwin 10000 10000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-0-2.tif new\2018_Bear_Gl_ORTHO-1-5.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-1-5.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-1-5.tif

gdal_translate -of GTIFF  -srcwin     0     0 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-1-0.tif new\2018_Bear_Gl_ORTHO-2-0.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-2-0.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-2-0.tif
gdal_translate -of GTIFF  -srcwin     0 10000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-1-0.tif new\2018_Bear_Gl_ORTHO-2-1.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-2-1.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-2-1.tif
gdal_translate -of GTIFF  -srcwin 10000     0 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-1-0.tif new\2018_Bear_Gl_ORTHO-3-0.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-3-0.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-3-0.tif
gdal_translate -of GTIFF  -srcwin 10000 10000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-1-0.tif new\2018_Bear_Gl_ORTHO-3-1.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-3-1.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-3-1.tif

gdal_translate -of GTIFF  -srcwin     0     0 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-1-1.tif new\2018_Bear_Gl_ORTHO-2-2.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-2-2.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-2-2.tif
gdal_translate -of GTIFF  -srcwin     0 10000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-1-1.tif new\2018_Bear_Gl_ORTHO-2-3.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-2-3.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-2-3.tif
gdal_translate -of GTIFF  -srcwin 10000     0 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-1-1.tif new\2018_Bear_Gl_ORTHO-3-2.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-3-2.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-3-2.tif
gdal_translate -of GTIFF  -srcwin 10000 10000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-1-1.tif new\2018_Bear_Gl_ORTHO-3-3.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-3-3.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-3-3.tif

gdal_translate -of GTIFF  -srcwin     0     0 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-1-2.tif new\2018_Bear_Gl_ORTHO-2-4.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-2-4.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-2-4.tif
gdal_translate -of GTIFF  -srcwin     0 10000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-1-2.tif new\2018_Bear_Gl_ORTHO-2-5.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-2-5.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-2-5.tif
gdal_translate -of GTIFF  -srcwin 10000     0 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-1-2.tif new\2018_Bear_Gl_ORTHO-3-4.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-3-4.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-3-4.tif
gdal_translate -of GTIFF  -srcwin 10000 10000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-1-2.tif new\2018_Bear_Gl_ORTHO-3-5.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-3-5.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-3-5.tif

gdal_translate -of GTIFF  -srcwin     0     0 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-1-3.tif new\2018_Bear_Gl_ORTHO-2-6.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-2-6.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-2-6.tif
gdal_translate -of GTIFF  -srcwin     0 10000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-1-3.tif new\2018_Bear_Gl_ORTHO-2-7.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-2-7.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-2-7.tif
gdal_translate -of GTIFF  -srcwin 10000     0 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-1-3.tif new\2018_Bear_Gl_ORTHO-3-6.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-3-6.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-3-6.tif
gdal_translate -of GTIFF  -srcwin 10000 10000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=2 -CO TILED=YES 2018_Bear_Gl_ORTHO-1-3.tif new\2018_Bear_Gl_ORTHO-3-7.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_ORTHO-3-7.tif
gdalinfo -stats -hist new\2018_Bear_Gl_ORTHO-3-7.tif
