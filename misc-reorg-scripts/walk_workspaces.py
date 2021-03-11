# -*- coding: utf-8 -*-
"""
Recursively lists the contents of workspaces, starting at a folder

BUGS:
* This is very slow and may fail in unexpected cases.
* It can double list some datasets i.e. a *.png is a feature_dataset (bands), raster and file

uses arcpy
 ListDatasets, ListFeatureClasses, ListFiles, ListRasters, ListTables, and ListWorkspaces
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os.path

import arcpy


class Config(object):
    """Namespace for configuration parameters. Edit as needed."""

    # pylint: disable=useless-object-inheritance,too-few-public-methods

    # Start folder - Where in the file system to start recursively looking
    # for workspaces.
    start_folder = r"C:\tmp"

    # Tab size - How many spacess to use to indent successive levels in the
    # workspace hierarchy.
    tab_size = 4


def inspect_workspace(level, workspace, folder=False):
    if not folder:
        inspect_feature_datasets(level, workspace)
    inspect_feature_classes(level, workspace)
    inspect_rasters(level, workspace)
    inspect_tables(level, workspace)
    if folder:
        # FIXME:  inspect_files will re-list everything found above (not the other stuff)
        # inspect_files(level, workspace, set())
        item = "Workspace"
        level += 1
        found = set()
        # Pro returns all files as workspaces with "All"
        kinds = ["FileGDB", "Access", "SDE", "Coverage", "Folder"]  # , "All"]
        for kind in kinds:
            arcpy.env.workspace = workspace
            for name in arcpy.ListWorkspaces("*", kind):
                if name not in found:
                    found.add(name)
                    print_item(level, item, kind, name)
                    sub_workspace = os.path.join(workspace, name)
                    inspect_workspace(level, sub_workspace, kind == "Folder")


def inspect_feature_datasets(level, workspace):
    item = "Feature Dataset"
    level += 1
    arcpy.env.workspace = workspace
    found = set()
    kinds = [
        "GeometricNetwork",
        "Mosaic",
        "Network",
        "ParcelFabric",
        "Raster",
        "RasterCatalog",
        # "Schematic", # Throws an error with Pro
        "Terrain",
        "Tin",
        "Topology",
        "Feature",
        "Coverage",
        "All",
    ]
    for kind in kinds:
        for dataset in arcpy.ListDatasets("*", kind):
            if dataset not in found:
                found.add(dataset)
                print_item(level, item, kind, dataset)
                inspect_feature_classes(level, workspace, dataset)


def inspect_feature_classes(level, workspace, dataset=""):
    item = "Feature Class"
    level += 1
    arcpy.env.workspace = workspace
    found = set()
    kinds = [
        "Annotation",
        "Arc",
        "Dimension",
        "Edge",
        "Label",
        "Line",
        "Multipatch",
        "Node",
        "Point",
        "Polygon",
        "Polyline",
        "Region",
        "Route",
        "Tic",
        "All",
    ]
    for kind in kinds:
        for name in arcpy.ListFeatureClasses("*", kind, dataset):
            if name not in found:
                found.add(name)
                print_item(level, item, kind, name)


def inspect_rasters(level, workspace):
    item = "Raster"
    level += 1
    arcpy.env.workspace = workspace
    found = set()
    kinds = ["BMP", "GIF", "IMG", "JP2", "JPG", "PNG", "TIF", "GRID", "All"]
    for kind in kinds:
        for name in arcpy.ListRasters("*", kind):
            if name not in found:
                found.add(name)
                print_item(level, item, kind, name)


def inspect_tables(level, workspace):
    item = "Table"
    level += 1
    arcpy.env.workspace = workspace
    found = set()
    kinds = ["dBASE", "INFO", "All"]
    for kind in kinds:
        for name in arcpy.ListTables("*", kind):
            if name not in found:
                found.add(name)
                print_item(level, item, kind, name)


def inspect_files(level, folder, found):
    item = "File"
    level += 1
    arcpy.env.workspace = folder
    for name in arcpy.ListFiles():
        if name not in found:
            print_item(level, item, None, name)


def print_item(level, item, kind, name):
    indent = " " * level * Config.tab_size
    if kind is None:
        kind = ""
    elif kind == "All":
        kind = "(?)"
    else:
        kind = "({0})".format(kind)
    print("{0}{1}{2} {3}".format(indent, item, kind, name))


if __name__ == "__main__":
    print_item(0, "Workspace", "Folder", Config.start_folder)
    inspect_workspace(0, Config.start_folder, True)
