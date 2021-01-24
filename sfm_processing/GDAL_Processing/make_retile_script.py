# -*- coding: utf-8 -*-
"""
This script will output GDAL commands to re-tile images.

Re-tiling subdivides a source image into several smaller images.
into smaller chunks. The output can be saved into a batch file for execution
in the directory containing the source images.  commands assumes there is a
sub folder called "new" for the output files.
The commands will create loseless compressed GeoTIFFs with pyramids and stats.

I believe source tiles around 10,000 x 10,000 pixels is a good
compromise. Larger images take longer to load, and are more sensitive to
hicups during network transfers.

This tool was written for Python 2.7. It also work with Python 3.3+
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys


class Config:
    """Configuration Constants; edit as necessary for each execution."""

    # Output Size  (10000 is good for 32bit 1band DEM,
    #   and 5000 is good for 16bit-3band orthos)
    # This keeps the output files in the 100 to 200 MB range
    x_size = 5000
    y_size = 5000

    # The base name of the source images.
    # If the source image name is in the form {basename}-{c}-{r}.{ext}
    #   set in_columns and in_rows to the range of c and r respectively.
    #   set add_numbers = True
    #   NOTE: if in_columns or in_rows are > 1 then add_numbers is ignored
    #   (and assumed True)
    # If there is one source image with the format {basename}.{ext}
    #   set both in_columns and in-rows to 1.
    #   set add_numbers = False
    # If the column or row numbers in the source image are padded with leading
    #   zeros, i.e 00, 01, .. 99 set pad_column_with_leading_zeros and/or
    #   pad_row_with_leading_zeros to True or False appropriately
    base_name = "2018_BELA_ATV_South_RGB"
    in_columns = 2
    in_rows = 1
    add_numbers = True
    pad_column_with_leading_zeros = False
    pad_row_with_leading_zeros = False

    # Number of new tiles per source image
    # Adjust n_cols and n_rows, so that (n-1 * size) < source_size < (n * size)
    # source_size is the number of pixels in the source image (from ArcCatalog or gdalinfo)
    n_cols = 1
    n_rows = 2

    # GDAL command settings
    predictor = 2  # 2 for Ortho, 3 for DEM
    extra = ""  # for adding no-data or band removal  -a_nodata none  -b 1 -b 2 -b 3
    cmd_base = (
        "gdal_translate -of GTIFF {7} -srcwin {0:5} {1:5} {2:5} {3:5} "
        "-CO COMPRESS=DEFLATE -co PREDICTOR={6} -CO TILED=YES {4}.tif {5}.tif"
    )


def print_commands():
    """Prints the GDAL commands to re-tile per the configuration."""

    if Config.in_columns < 1 or Config.in_rows < 1:
        print("Error: Both in_columns and in_rows must be greater than zero.")
        sys.exit()
    if Config.n_cols < 1 or Config.n_rows < 1:
        print("Error: Both n_cols and n_rows must be greater than zero.")
        sys.exit()
    if Config.n_cols < 2 and Config.n_rows < 2:
        print("Error: One of n_cols or n_rows must be greater than one.")
        sys.exit()
    old_name = Config.base_name
    c_format_in = "-{1:02}" if Config.pad_column_with_leading_zeros else "-{1}"
    r_format_in = "-{2:02}" if Config.pad_row_with_leading_zeros else "-{2}"
    c_format_out = "-{1}" if Config.in_columns * Config.n_cols <= 10 else "-{1:02}"
    r_format_out = "-{2}" if Config.in_rows * Config.n_rows <= 10 else "-{2:02}"
    add_numbers = Config.add_numbers
    if Config.in_columns > 1 or Config.in_rows > 1:
        add_numbers = True
    for col in range(Config.in_columns):
        for row in range(Config.in_rows):
            if add_numbers:
                old_name = ("{0}" + c_format_in + r_format_in).format(
                    Config.base_name, col, row
                )
            new_base_name = os.path.join("new", Config.base_name)
            start_cell_x = Config.n_cols * col
            start_cell_y = Config.n_rows * row
            for i in range(Config.n_cols):
                x_off = Config.x_size * i
                x_name = start_cell_x + i
                for j in range(Config.n_rows):
                    y_name = start_cell_y + j

                    new_name = ("{0}" + c_format_out + r_format_out).format(
                        new_base_name, x_name, y_name
                    )
                    y_off = Config.y_size * j
                    cmd = Config.cmd_base.format(
                        x_off,
                        y_off,
                        Config.x_size,
                        Config.y_size,
                        old_name,
                        new_name,
                        Config.predictor,
                        Config.extra,
                    )
                    print(cmd)
                    if Config.predictor == 2:
                        add_cmd = (
                            "gdaladdo --config COMPRESS_OVERVIEW JPEG "
                            "--config PHOTOMETRIC_OVERVIEW YCBCR "
                            "--config INTERLEAVE_OVERVIEW PIXEL -r average {0}.tif"
                        )
                        print(add_cmd.format(new_name))
                    if Config.predictor == 3:
                        add_cmd = (
                            "gdaladdo --config COMPRESS_OVERVIEW JPEG "
                            "--config INTERLEAVE_OVERVIEW PIXEL -r average {0}.tif"
                        )
                        print(add_cmd.format(new_name))
                    print("gdalinfo -stats -hist {0}.tif".format(new_name))


if __name__ == "__main__":
    print_commands()
