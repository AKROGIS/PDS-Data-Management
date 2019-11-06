gdal_translate -of GTIFF  -srcwin     0     0 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=3 -CO TILED=YES 2018_Bear_Gl_DEM.tif new\2018_Bear_Gl_DEM-0-0.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_DEM-0-0.tif
gdalinfo -stats -hist new\2018_Bear_Gl_DEM-0-0.tif
gdal_translate -of GTIFF  -srcwin     0 10000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=3 -CO TILED=YES 2018_Bear_Gl_DEM.tif new\2018_Bear_Gl_DEM-0-1.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_DEM-0-1.tif
gdalinfo -stats -hist new\2018_Bear_Gl_DEM-0-1.tif
gdal_translate -of GTIFF  -srcwin     0 20000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=3 -CO TILED=YES 2018_Bear_Gl_DEM.tif new\2018_Bear_Gl_DEM-0-2.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_DEM-0-2.tif
gdalinfo -stats -hist new\2018_Bear_Gl_DEM-0-2.tif
gdal_translate -of GTIFF  -srcwin     0 30000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=3 -CO TILED=YES 2018_Bear_Gl_DEM.tif new\2018_Bear_Gl_DEM-0-3.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_DEM-0-3.tif
gdalinfo -stats -hist new\2018_Bear_Gl_DEM-0-3.tif
gdal_translate -of GTIFF  -srcwin 10000     0 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=3 -CO TILED=YES 2018_Bear_Gl_DEM.tif new\2018_Bear_Gl_DEM-1-0.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_DEM-1-0.tif
gdalinfo -stats -hist new\2018_Bear_Gl_DEM-1-0.tif
gdal_translate -of GTIFF  -srcwin 10000 10000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=3 -CO TILED=YES 2018_Bear_Gl_DEM.tif new\2018_Bear_Gl_DEM-1-1.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_DEM-1-1.tif
gdalinfo -stats -hist new\2018_Bear_Gl_DEM-1-1.tif
gdal_translate -of GTIFF  -srcwin 10000 20000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=3 -CO TILED=YES 2018_Bear_Gl_DEM.tif new\2018_Bear_Gl_DEM-1-2.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_DEM-1-2.tif
gdalinfo -stats -hist new\2018_Bear_Gl_DEM-1-2.tif
gdal_translate -of GTIFF  -srcwin 10000 30000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=3 -CO TILED=YES 2018_Bear_Gl_DEM.tif new\2018_Bear_Gl_DEM-1-3.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_DEM-1-3.tif
gdalinfo -stats -hist new\2018_Bear_Gl_DEM-1-3.tif
gdal_translate -of GTIFF  -srcwin 20000     0 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=3 -CO TILED=YES 2018_Bear_Gl_DEM.tif new\2018_Bear_Gl_DEM-2-0.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_DEM-2-0.tif
gdalinfo -stats -hist new\2018_Bear_Gl_DEM-2-0.tif
gdal_translate -of GTIFF  -srcwin 20000 10000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=3 -CO TILED=YES 2018_Bear_Gl_DEM.tif new\2018_Bear_Gl_DEM-2-1.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_DEM-2-1.tif
gdalinfo -stats -hist new\2018_Bear_Gl_DEM-2-1.tif
gdal_translate -of GTIFF  -srcwin 20000 20000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=3 -CO TILED=YES 2018_Bear_Gl_DEM.tif new\2018_Bear_Gl_DEM-2-2.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_DEM-2-2.tif
gdalinfo -stats -hist new\2018_Bear_Gl_DEM-2-2.tif
gdal_translate -of GTIFF  -srcwin 20000 30000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=3 -CO TILED=YES 2018_Bear_Gl_DEM.tif new\2018_Bear_Gl_DEM-2-3.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_DEM-2-3.tif
gdalinfo -stats -hist new\2018_Bear_Gl_DEM-2-3.tif
gdal_translate -of GTIFF  -srcwin 30000     0 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=3 -CO TILED=YES 2018_Bear_Gl_DEM.tif new\2018_Bear_Gl_DEM-3-0.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_DEM-3-0.tif
gdalinfo -stats -hist new\2018_Bear_Gl_DEM-3-0.tif
gdal_translate -of GTIFF  -srcwin 30000 10000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=3 -CO TILED=YES 2018_Bear_Gl_DEM.tif new\2018_Bear_Gl_DEM-3-1.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_DEM-3-1.tif
gdalinfo -stats -hist new\2018_Bear_Gl_DEM-3-1.tif
gdal_translate -of GTIFF  -srcwin 30000 20000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=3 -CO TILED=YES 2018_Bear_Gl_DEM.tif new\2018_Bear_Gl_DEM-3-2.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_DEM-3-2.tif
gdalinfo -stats -hist new\2018_Bear_Gl_DEM-3-2.tif
gdal_translate -of GTIFF  -srcwin 30000 30000 10000 10000 -CO COMPRESS=DEFLATE -co PREDICTOR=3 -CO TILED=YES 2018_Bear_Gl_DEM.tif new\2018_Bear_Gl_DEM-3-3.tif
gdaladdo --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL -r average new\2018_Bear_Gl_DEM-3-3.tif
gdalinfo -stats -hist new\2018_Bear_Gl_DEM-3-3.tif