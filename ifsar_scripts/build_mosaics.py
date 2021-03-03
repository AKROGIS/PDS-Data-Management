# -*- coding: utf-8 -*-
"""
Extracts a list of raster image paths form a CSV file and adds to a mosaic dataset.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import os

import arcpy

import csv23


class Config(object):
    """Namespace for configuration parameters. Edit as needed."""

    # pylint: disable=useless-object-inheritance,too-few-public-methods

    # The geodatabase of raster mosaics. This must be a local copy of the
    # master geodatabase on the PDS.
    mosaic_database = "C:/tmp/pds/new_ifsar/SDMI_IFSAR.gdb"

    # The matching of mosaic rasters to the CSV file of paths to add.
    # The CSV path is relative to the current working directory.
    # The CSV has no header, and only one column which is an absolute path
    # to a raster data file.
    mosaic_csv = {
        "DSM": "data/build_ifsar_2021_dsm.csv",
        "DTM": "data/build_ifsar_2021_dtm.csv",
        "ORI": "data/build_ifsar_2021_ori.csv",
        "ORI_SUP1": "data/build_ifsar_2021_ori1.csv",
        "ORI_SUP2": "data/build_ifsar_2021_ori2.csv",
        "ORI_SUP3": "data/build_ifsar_2021_ori3.csv",
    }


def load_csv_file(csv_path):
    """Return a list of the rows in the CSV."""

    records = []
    with csv23.open(csv_path, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # ignore the header
        for row in csv_reader:
            row = csv23.fix(row)
            records.append(row)
    return records


def make_raster_list_for_mosaic(csv_data):
    """Extract the names of the rasters for the CSV data."""

    raster_path_index = 0
    rasters = []
    for record in csv_data:
        if record[raster_path_index] is not None:
            rasters.append(record[raster_path_index])
    return rasters


def add_rasters_to_mosaic(fgdb, mosaic, rasters):
    """Add the list of rasters to the mosaic dataset in the fgdb."""

    dataset = os.path.join(fgdb, mosaic)
    arcpy.AddRastersToMosaicDataset_management(
        in_mosaic_dataset=dataset,
        raster_type="Raster Dataset",
        input_path=rasters,
        update_overviews="NO_OVERVIEWS",
    )


def add_rasters():
    """Add the rasters in csv_file to the mosaic dataset in the fgdb."""

    fgdb = Config.mosaic_database
    for mosaic, csv_path in Config.mosaic_csv.items():
        csv_data = load_csv_file(csv_path)
        rasters = make_raster_list_for_mosaic(csv_data)
        print("Adding {0} rasters to {1}".format(len(rasters), mosaic))
        add_rasters_to_mosaic(fgdb, mosaic, rasters)


if __name__ == "__main__":
    add_rasters()
