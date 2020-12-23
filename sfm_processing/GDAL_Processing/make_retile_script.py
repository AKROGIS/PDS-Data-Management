import sys

# This script will create a GDAL commands to retile (sub-divide) images
# into smaller chunks. The output can be saved into a batch file for execution
# in the directory containing the source images.  commands assumes there is a
# sub folder called "new" for the output files.
# The commands will create loseless compressed GeoTIFFs with pyramids and stats.

# I believe source tiles around 10,000 x 10,000 pixels is a good
# compromise. Larger images take longer to load, and are more sensitive to
# hicups during network transfers.

# Output Size  (10000 is good for 32bit 1band DEMs, and 5000 is good for 16bit-3band orthos)
# This keeps the output files in the 100 to 200 MB range
xsize = 5000
ysize = 5000

# The base name of the source images.
# If the source image name is in the form {basename}-{c}-{r}.{ext}
#   set in_columns and in_rows to the range of c and r respectively.
#   set add_numbers = True
#   NOTE: if in_columns or in_rows are > 1 then add_numbers is ignored (and assumed True)
# If there is one source image with the format {basename}.{ext}
#   set both in_columns and in-rows to 1.
#   set add_numbers = False
# If the column or row numbers in the source image are padded with leading zeros, i.e 00, 01, .. 99 
#   set pad_column_with_leading_zeros and pad_row_with_leading_zeros to True or False appropriately
base_name = "2018_BELA_ATV_South_RGB"
in_columns = 17
in_rows = 16
add_numbers = True
pad_column_with_leading_zeros = False
pad_row_with_leading_zeros = False

# Number of new tiles per source image
# Adjust n_cols and n_rows, so that (n-1 * size) < source_size < (n * size)
# source_size is the number of pixels in the source image (from ArcCatalog or gdalinfo)
n_cols = 4
n_rows = 4

# GDAL command settings
predictor = 2  # 2 for Ortho, 3 for DEM
extra = ""     # for adding no-data or band removal  -a_nodata none  -b 1 -b 2 -b 3  
cmd_base = "gdal_translate -of GTIFF {7} -srcwin {0:5} {1:5} {2:5} {3:5} -CO COMPRESS=DEFLATE -co PREDICTOR={6} -CO TILED=YES {4}.tif {5}.tif"

# End of configuration options.

if in_columns < 1 or in_rows < 1:
    print("Error: Both in_columns and in_rows must be greater than zero.")
    sys.exit()
if n_cols < 1 or n_rows < 1:
    print("Error: Both n_cols and n_rows must be greater than zero.")
    sys.exit()
if n_cols < 2 and n_rows < 2:
    print("Error: One of n_cols or n_rows must be greater than one.")
    sys.exit()
old_name = base_name
cformat_in = "-{1:02}" if pad_column_with_leading_zeros else "-{1}"
rformat_in = "-{2:02}" if pad_row_with_leading_zeros else "-{2}"
cformat_out = "-{1}" if in_columns * n_cols <= 10 else "-{1:02}"
rformat_out = "-{2}" if in_rows * n_rows <= 10 else "-{2:02}"
if in_columns > 1 or in_rows > 1:
    add_numbers = True
for c in range(in_columns):
    for r in range(in_rows):
        if add_numbers:
            old_name = ("{0}" + cformat_in + rformat_in).format(base_name,c, r)
        new_base_name = "new\\" + base_name
        start_cell_x = n_cols * c
        start_cell_y = n_rows * r
        for i in range(n_cols):
            xoff = xsize*i
            xname = start_cell_x + i
            for j in range(n_rows):
                yname = start_cell_y + j

                new_name = ("{0}" + cformat_out + rformat_out).format(new_base_name, xname, yname)
                yoff = ysize*j
                cmd = cmd_base.format(xoff, yoff, xsize, ysize, old_name, new_name, predictor, extra)
                print cmd
                if predictor == 2:
                    print "gdaladdo --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL -r average {0}.tif".format(new_name)
                if predictor == 3:
                    print "gdaladdo --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL -r average {0}.tif".format(new_name)
                print "gdalinfo -stats -hist {0}.tif".format(new_name)
