# -*- coding: utf-8 -*-
"""
walk file system
*.mxd - list data frames, and all layers recursively (flag any missing data sources)
*.lyr - list all layers recursively  (flag any missing data sources)
*.gdb
*.mdb - list all datasets
*.shp - list
*.gdb/mosaic - list all photo workspaces  (flag any missing data sources)

use arcpy
 ListDatasets, ListFeatureClasses, ListFiles, ListRasters, ListTables, and ListWorkspaces
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import arcpy


def inspect_featureclasses(level, dataset=None):
    # print '**** Feature Classes ****'
    found = set([])
    for kind in [
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
    ]:
        if dataset is None:
            items = arcpy.ListFeatureClasses("*", kind)
        else:
            items = arcpy.ListFeatureClasses("*", kind, dataset)
        if items:
            for item in items:
                if item not in found:
                    found.add(item)
                    print(" " * level * 4 + "FeatureClass " + kind + " " + item)


def inspect_workspace(w, level):
    # print '#### ' + w + ' ####'
    arcpy.env.workspace = w
    found = set([])

    inspect_featureclasses(level)

    # print '**** Files ****'
    # for kind in ["File"]:
    #    items = arcpy.ListFiles()
    #    if items:
    #        for item in items:
    #            print 'File', kind, item

    # print '**** Rasters ****'
    for kind in ["BMP", "GIF", "IMG", "JP2", "JPG", "PNG", "TIF", "GRID", "All"]:
        items = arcpy.ListRasters("*", kind)
        if items:
            for item in items:
                if item not in found:
                    found.add(item)
                    print(" " * level * 4 + "Raster " + kind + " " + item)

    # print '**** Tables ****'
    for kind in ["dBASE", "INFO", "All"]:
        items = arcpy.ListTables("*", kind)
        if items:
            for item in items:
                if item not in found:
                    found.add(item)
                    print(" " * level * 4 + "Table " + kind + " " + item)

    # print '**** Datasets ****'
    for kind in [
        "GeometricNetwork",
        "Mosaic",
        "Network",
        "ParcelFabric",
        "Raster",
        "RasterCatalog",
        "Schematic",
        "Terrain",
        "Tin",
        "Topology",
        "Feature",
        "Coverage",
        "All",
    ]:
        items = arcpy.ListDatasets("*", kind)
        if items:
            for item in items:
                if item not in found:
                    found.add(item)
                    print(" " * level * 4 + "Dataset " + kind + " " + item)
                    if kind == "Feature":
                        inspect_featureclasses(level + 1, item)

    # print '**** Workspaces ****'
    for kind in ["FileGDB", "Folder", "SDE", "Access", "Coverage", "All"]:
        items = arcpy.ListWorkspaces("*", kind)
        if items:
            for item in items:
                if item not in found:
                    found.add(item)
                    print(" " * level * 4 + "Workspace " + kind + " " + item)
                    inspect_workspace(item, level + 1)


# for d in [r"x:\Albers\base\climate", r"x:\Albers\base\climate\snow"]:
for d in [
    r"X:\Albers\base\cultural\statewid\TrailsNPS.gdb"
]:  # r"x:\Albers\base\climate"]:
    print("Workspace Folder " + d)
    inspect_workspace(d, 1)
