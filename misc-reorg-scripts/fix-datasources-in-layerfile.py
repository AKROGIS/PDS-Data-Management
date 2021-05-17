# -*- coding: utf-8 -*-
"""
Fix broken data sources in a layerfile.

Edit the layer file path and datasource paths in the script before running.

requires ArcMap 10.x arcpy
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import arcpy

layer = arcpy.mapping.Layer(r"X:\GIS\ThemeMgr\KATM Themes\Brooks Camp LiDAR\KATM Brooks Camp Contours.lyr")
# print(arcpy.mapping.ListBrokenDataSources(layer))
layer.replaceDataSource(r"X:\Albers\parks\katm\GeoDB\KATM_Base.gdb", "FILEGDB_WORKSPACE", "KATM_TOPO_BrooksRiverContours30cm2012_ln")
# print(arcpy.mapping.ListBrokenDataSources(layer))
layer.save()
