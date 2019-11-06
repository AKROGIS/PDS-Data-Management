
in_columns = 1
in_rows = 1
base_name = "KEFJ_2017_Exit_DEM_UTM6"
n_cols = 3
n_rows = 3
xsize = 10000
ysize = 10000
predictor = 3  # 2 for Ortho, 3 for DEM
extra = ""     # for adding no-data or band removal  -a_nodata none  -b 1 -b 2 -b 3  
cmd_base = "gdal_translate -of GTIFF {7} -srcwin {0:5} {1:5} {2:5} {3:5} -CO COMPRESS=DEFLATE -co PREDICTOR={6} -CO TILED=YES {4}.tif {5}.tif"

old_name = base_name
for c in range(in_columns):
    for r in range(in_rows):
        if in_columns > 1 or in_rows > 1:
            old_name = base_name + "-{0}-{1}".format(c, r)
        new_base_name = "new\\" + base_name
        start_cell_x = n_cols * c
        start_cell_y = n_rows * r
        for i in range(n_cols):
            xoff = xsize*i
            xname = start_cell_x + i
            for j in range(n_rows):
                yname = start_cell_y + j
                new_name = "{0}-{1}-{2}".format(new_base_name, xname, yname)
                yoff = ysize*j
                cmd = cmd_base.format(xoff, yoff, xsize, ysize, old_name, new_name, predictor, extra)
                print cmd
                if predictor == 2:
                    print "gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average {0}.tif".format(new_name)
                if predictor == 3:
                    print "gdaladdo --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL -r average {0}.tif".format(new_name)
                print "gdalinfo -stats -hist {0}.tif".format(new_name)
