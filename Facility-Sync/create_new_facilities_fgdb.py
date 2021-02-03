# -*- coding: utf-8 -*-
"""
A tool to export the NPS Alaska facilities2 SDE database to a file geodatabase.

This tool started as a model builder script on 2018-04-06 but was modified to
include database specific filters, calculations and transformations.  It also
builds new database items (like relationships) on the fly.

It will likely break if the database schema changes, and very little attempt
was made to ameliorate this, but it is simple enough and short enough that
making the necessary changes should not be too hard.

This tool was tested with ArcGIS 10.6.1 and Pro 2.5.1
Non-standard modules:
  Relies on the esri `arcpy` module installed with ArcGIS.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import os
import sys

import arcpy

# Bizare esri bug discoverd during testing.
# When I switched the CONNECTION_FILE from a connection file in my profile to
# one on the network (which will work with all users and all versions), ArcGIS
# 10.6.1 failed to copy the metadata for BLDG_PT, BLDG_PY, FMSSExport and FMSS
# Assets.  Pro worked fine with the network connection file, and 10.x had no
# other issues.  Using that network configuration file in ArcCatalog 10.x works
# fine.  I can see nothing wrong with it (I think it is a copy of what I have
# in my profile).  IF you need to use ArcGIS 10.x and the metadata is missing,
# copy the connection file to your profile, and swap the connection file.

# Configuration Constants:
FGDB_NAME = "akr_facility"
FGDB_EXT = ".gdb"
WORKING_FOLDER = r"C:\tmp\pds\facility-sync"
XDRIVE_FOLDER = r"X:\AKR\Statewide\cultural"
CONNECTION_FILE = (
    # r"Database Connections\inpakrovmais - facilities as akr_reader_web.sde"
    r"X:\GIS\SDE Connection Files\inpakrovmais.akr_facilities.akr_reader_web.sde"
)
SDE_SCHEMA = "akr_facility2."
tables = [
    "dbo.FMSSExport",
    "dbo.FMSSExport_Asset",
    "gis.AKR_ATTACH",
    "gis.AKR_ASSET",
]
fcs = [
    "dbo.AKR_BLDG_PT",
    "dbo.AKR_BLDG_PY",
    "gis.AKR_ATTACH_PT",
    "gis.PARKLOTS_PY",
    "gis.ROADS_LN",
    "gis.ROADS_FEATURE_PT",
    "gis.TRAILS_ATTRIBUTE_PT",
    "gis.TRAILS_FEATURE_PT",
    "gis.TRAILS_LN",
    "gis.AKR_ASSET_PT",
    "gis.AKR_ASSET_LN",
    "gis.AKR_ASSET_PY",
]


# derived variables
NEW_FGDB_NAME = "{0}_new{1}".format(FGDB_NAME, FGDB_EXT)
SAVED_FGDB_NAME = "{0}_{1}{2}".format(FGDB_NAME, datetime.date.today(), FGDB_EXT)
xdrive_fgdb = os.path.join(XDRIVE_FOLDER, FGDB_NAME + FGDB_EXT)
new_fgdb = os.path.join(WORKING_FOLDER, NEW_FGDB_NAME)
saved_fgdb = os.path.join(WORKING_FOLDER, SAVED_FGDB_NAME)
sde_tables = [os.path.join(CONNECTION_FILE, SDE_SCHEMA + table) for table in tables]
sde_fcs = [os.path.join(CONNECTION_FILE, SDE_SCHEMA + fc) for fc in fcs]

# convenience variables
# only needed for items that will have added/calculated fields, or derived metadata
Building_Polygon = os.path.join(new_fgdb, "AKR_BLDG_PY")
PARKLOTS_py = os.path.join(new_fgdb, "PARKLOTS_PY")
ROADS_ln = os.path.join(new_fgdb, "ROADS_LN")
TRAILS_ln = os.path.join(new_fgdb, "TRAILS_LN")
Building_Centroid = os.path.join(new_fgdb, "AKR_BLDG_PT")
FMSS_Locations = os.path.join(new_fgdb, "FMSSExport")
FMSS_Assets = os.path.join(new_fgdb, "FMSSExport_Asset")


# Process: Delete
if arcpy.Exists(new_fgdb):
    arcpy.Delete_management(new_fgdb, "Workspace")
if arcpy.Exists(saved_fgdb):
    arcpy.Delete_management(saved_fgdb, "Workspace")

# Process: Saved published fgdb
arcpy.Copy_management(xdrive_fgdb, saved_fgdb, "Workspace")
# Process: Create File GDB
folder, fgdb = os.path.split(new_fgdb)
arcpy.CreateFileGDB_management(folder, fgdb, "CURRENT")


# Process: Table To Geodatabase (multiple)
arcpy.TableToGeodatabase_conversion(sde_tables, new_fgdb)
# Process: Feature Class to Geodatabase (multiple)
arcpy.FeatureClassToGeodatabase_conversion(sde_fcs, new_fgdb)


# Process: Add Field
arcpy.AddField_management(
    PARKLOTS_py, "Perim_Feet", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""
)
# Process: Calculate Field
arcpy.CalculateField_management(
    PARKLOTS_py, "Perim_Feet", "!shape.length@feet!", "PYTHON_9.3", ""
)

# Process: Add Field (2)
arcpy.AddField_management(
    PARKLOTS_py, "Area_SqFt", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""
)
# Process: Calculate Field (2)
arcpy.CalculateField_management(
    PARKLOTS_py, "Area_SqFt", "!shape.area@SQUAREFEET!", "PYTHON_9.3", ""
)

# Process: Add Field (3)
arcpy.AddField_management(
    Building_Polygon,
    "Perim_Feet",
    "DOUBLE",
    "",
    "",
    "",
    "",
    "NULLABLE",
    "NON_REQUIRED",
    "",
)
# Process: Calculate Field (3)
arcpy.CalculateField_management(
    Building_Polygon, "Perim_Feet", "!shape.length@feet!", "PYTHON_9.3", ""
)

# Process: Add Field (4)
arcpy.AddField_management(
    Building_Polygon,
    "Area_SqFt",
    "DOUBLE",
    "",
    "",
    "",
    "",
    "NULLABLE",
    "NON_REQUIRED",
    "",
)
# Process: Calculate Field (4)
arcpy.CalculateField_management(
    Building_Polygon, "Area_SqFt", "!shape.area@SQUAREFEET!", "PYTHON_9.3", ""
)

# Process: Add Field (5)
arcpy.AddField_management(
    ROADS_ln, "Length_Feet", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""
)
# Process: Calculate Field (6)
arcpy.CalculateField_management(
    ROADS_ln, "Length_Feet", "!shape.length@feet!", "PYTHON_9.3", ""
)

# Process: Add Field (6)
arcpy.AddField_management(
    ROADS_ln, "Length_Miles", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""
)
# Process: Calculate Field (5)
arcpy.CalculateField_management(
    ROADS_ln, "Length_Miles", "!shape.length@miles!", "PYTHON_9.3", ""
)

# Process: Add Field (7)
arcpy.AddField_management(
    TRAILS_ln, "Length_Feet", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""
)
# Process: Calculate Field (8)
arcpy.CalculateField_management(
    TRAILS_ln, "Length_Feet", "!shape.length@feet!", "PYTHON_9.3", ""
)

# Process: Add Field (8)
arcpy.AddField_management(
    TRAILS_ln, "Length_Miles", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""
)
# Process: Calculate Field (7)
arcpy.CalculateField_management(
    TRAILS_ln, "Length_Miles", "!shape.length@miles!", "PYTHON_9.3", ""
)
# Process: Add Attachment Indexes
AKR_ATTACH = os.path.join(new_fgdb, "AKR_ATTACH")
arcpy.AddIndex_management(AKR_ATTACH, "FACLOCID", "FACLOCID_IDX", "#", "#")
arcpy.AddIndex_management(AKR_ATTACH, "FACASSETID", "FACASSETID_IDX", "#", "#")
arcpy.AddIndex_management(AKR_ATTACH, "FEATUREID", "FEATUREID_IDX", "#", "#")
arcpy.AddIndex_management(AKR_ATTACH, "GEOMETRYID", "GEOMETRYID_IDX", "#", "#")

# Add Metadata
# ============


def copy_metadata(source, destination):
    """
    Copy Metadata from the source feature class to the destination feature class

    Copying metadata is different in Pro (Python 3), than it is in 10.x (Python 2)
    source and destination are paths to feature classes (strings).

    Assumes ArcGIS Metadata format. Choices are:
        FROM_ARCGIS -> ARCGIS_METADATA
        FROM_FGDC -> FGDC_CSDGM
        FROM_ISO_19139 -> ISO19139_UNKNOWN
    """
    print("Copy metadata from {0} to {1}".format(source, destination))
    if sys.version_info[0] < 3:
        arcpy.ImportMetadata_conversion(source, "FROM_ARCGIS", destination)
    else:
        dest = arcpy.metadata.Metadata(destination)
        dest.importMetadata(source, "ARCGIS_METADATA")
        dest.save()


Source_Metadata = os.path.join(
    CONNECTION_FILE, SDE_SCHEMA + "GIS.AKR_BLDG_PY_Template_for_Metadata"
)
copy_metadata(Source_Metadata, Building_Polygon)
Source_Metadata = os.path.join(
    CONNECTION_FILE, SDE_SCHEMA + "GIS.AKR_BLDG_PT_Template_for_Metadata"
)
copy_metadata(Source_Metadata, Building_Centroid)
Source_Metadata = os.path.join(
    CONNECTION_FILE, SDE_SCHEMA + "GIS.FMSSExport_Template_for_Metadata"
)
copy_metadata(Source_Metadata, FMSS_Locations)
Source_Metadata = os.path.join(
    CONNECTION_FILE, SDE_SCHEMA + "GIS.FMSSExport_Asset_Template_for_Metadata"
)
copy_metadata(Source_Metadata, FMSS_Assets)

# Add History
# ===========
# TODO: ArcGIS provides no way to add the history tables.
# I think I need a direct database connection, then copy the *_H tables,
# then convert them to a feature class.

# Add Relationships
# =================
print("Creating Relationships")
arcpy.env.workspace = new_fgdb
# Asset to Location
# fmt: off
arcpy.CreateRelationshipClass_management(
    "FMSSExport", "FMSSExport_Asset",
    "Location_Asset_Relation", "COMPOSITE",
    "Assets", "Owning Location",
    "NONE", "ONE_TO_MANY", "NONE",
    "Location", "Location"
)
# GIS Features to Locations
arcpy.CreateRelationshipClass_management(
    "FMSSExport", "AKR_BLDG_PY",
    "Location_BuildingFootprint_Relation", "SIMPLE",
    "Building Footprints", "FMSS Location Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Location", "FACLOCID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport", "AKR_BLDG_PT",
    "Location_BuildingCenter_Relation", "SIMPLE",
    "Building Centers", "FMSS Location Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Location", "FACLOCID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport", "PARKLOTS_PY",
    "Location_ParkingLot_Relation", "SIMPLE",
    "Parking Lots", "FMSS Location Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Location", "FACLOCID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport", "ROADS_LN",
    "Location_Roads_Relation", "SIMPLE",
    "Roads", "FMSS Location Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Location", "FACLOCID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport", "ROADS_FEATURE_PT",
    "Location_RoadFeatures_Relation", "SIMPLE",
    "Road Features", "FMSS Location Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Location", "FACLOCID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport", "TRAILS_LN",
    "Location_Trails_Relation", "SIMPLE",
    "Trails", "FMSS Location Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Location", "FACLOCID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport", "TRAILS_FEATURE_PT",
    "Location_TrailFeatures_Relation", "SIMPLE",
    "Trail Features", "FMSS Location Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Location", "FACLOCID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport", "AKR_ASSET_PT",
    "Location_PointAssetFeatures_Relation", "SIMPLE",
    "Facility Assets", "FMSS Location Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Location", "FACLOCID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport", "AKR_ASSET_LN",
    "Location_LineAssetFeatures_Relation", "SIMPLE",
    "Facility Assets", "FMSS Location Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Location", "FACLOCID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport", "AKR_ASSET_PY",
    "Location_PolyAssetFeatures_Relation", "SIMPLE",
    "Facility Assets", "FMSS Location Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Location", "FACLOCID"
)

# GIS Features to Assets
arcpy.CreateRelationshipClass_management(
    "FMSSExport_Asset", "AKR_ASSET_PT",
    "Asset_PointAssetFeatures_Relation", "SIMPLE",
    "Facility Assets", "FMSS Asset Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Asset", "FACASSETID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport_Asset", "AKR_ASSET_LN",
    "Asset_LineAssetFeatures_Relation", "SIMPLE",
    "Facility Assets", "FMSS Asset Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Asset", "FACASSETID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport_Asset", "AKR_ASSET_PY",
    "Asset_PolyAssetFeatures_Relation", "SIMPLE",
    "Facility Assets", "FMSS Asset Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Asset", "FACASSETID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport_Asset", "ROADS_FEATURE_PT",
    "Asset_RoadFeatures_Relation", "SIMPLE",
    "Road Features", "FMSS Asset Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Asset", "FACASSETID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport_Asset", "TRAILS_FEATURE_PT",
    "Asset_TrailFeatures_Relation", "SIMPLE",
    "Trail Features", "FMSS Asset Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Asset", "FACASSETID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport_Asset", "TRAILS_ATTRIBUTE_PT",
    "Asset_TrailAttributes_Relation", "SIMPLE",
    "Trail Attributes", "FMSS Asset Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Asset", "FACASSETID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport_Asset", "TRAILS_LN",
    "Asset_Trails_Relation", "SIMPLE",
    "Trails", "FMSS Asset Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Asset", "FACASSETID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport_Asset", "ROADS_LN",
    "Asset_Roads_Relation", "SIMPLE",
    "Roads", "FMSS Asset Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Asset", "FACASSETID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport_Asset", "PARKLOTS_PY",
    "Asset_ParkingLots_Relation", "SIMPLE",
    "Parking Lots", "FMSS Asset Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Asset", "FACASSETID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport_Asset", "AKR_BLDG_PT",
    "Asset_BuildingPoint_Relation", "SIMPLE",
    "Building Point", "FMSS Asset Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Asset", "FACASSETID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport_Asset", "AKR_BLDG_PY",
    "Asset_BuildingPoly_Relation", "SIMPLE",
    "Building Poly", "FMSS Asset Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Asset", "FACASSETID"
)

# GIS Feature to GIS Feature
# Trail Attributes belong to a trail
arcpy.CreateRelationshipClass_management(
    "TRAILS_LN", "TRAILS_ATTRIBUTE_PT",
    "Trail_Attribute_Relation", "COMPOSITE",
    "Attributes", "Trail",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
# Trail Feature's SEGMENTID is the GEOMETRYID of the closest segment of the "Parent" trail
arcpy.CreateRelationshipClass_management(
    "TRAILS_LN", "TRAILS_FEATURE_PT",
    "Trail_Feature_Relation", "SIMPLE",
    "Features", "Trail",
    "NONE", "ONE_TO_MANY", "NONE",
    "GEOMETRYID", "SEGMENTID"
)
# Roads Feature's SEGMENTID is the GEOMETRYID of the closest segment of the "Parent" road
arcpy.CreateRelationshipClass_management(
    "ROADS_LN", "ROADS_FEATURE_PT",
    "Road_Feature_Relation", "SIMPLE",
    "Features", "Road",
    "NONE", "ONE_TO_MANY", "NONE",
    "GEOMETRYID", "SEGMENTID"
)
# Building Center to Footprint
arcpy.CreateRelationshipClass_management(
    "AKR_BLDG_PT", "AKR_BLDG_PY",
    "BuildingCenter_Footprint_Relation", "SIMPLE",
    "Footprints", "Centroid",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
# Attachments
# Photos/GeoPhotos to FMSS Location/Asset
arcpy.CreateRelationshipClass_management(
    "FMSSExport", "AKR_ATTACH",
    "Location_Attachment_Relation", "SIMPLE",
    "Photos", "FMSS Location Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Location", "FACLOCID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport", "AKR_ATTACH_PT",
    "Location_AttachmentPoint_Relation", "SIMPLE",
    "GeoPhotos", "FMSS Location Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Location", "FACLOCID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport_Asset", "AKR_ATTACH",
    "Asset_Attachment_Relation", "SIMPLE",
    "Photos", "FMSS Asset Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Asset", "FACLOCID"
)
arcpy.CreateRelationshipClass_management(
    "FMSSExport_Asset", "AKR_ATTACH_PT",
    "Asset_AttachmentPoint_Relation", "SIMPLE",
    "GeoPhotos", "FMSS Asset Record",
    "NONE", "ONE_TO_MANY", "NONE",
    "Asset", "FACLOCID"
)
# Photos to GIS Features
arcpy.CreateRelationshipClass_management(
    "AKR_BLDG_PT", "AKR_ATTACH",
    "BuildingPoint_Attachment_Relation", "SIMPLE",
    "Photos", "Building Point",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
arcpy.CreateRelationshipClass_management(
    "AKR_BLDG_PY", "AKR_ATTACH",
    "BuildingPoly_Attachment_Relation", "SIMPLE",
    "Photos", "Building Poly",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
arcpy.CreateRelationshipClass_management(
    "ROADS_LN", "AKR_ATTACH",
    "Road_Attachment_Relation", "SIMPLE",
    "Photos", "Road",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
arcpy.CreateRelationshipClass_management(
    "PARKLOTS_PY", "AKR_ATTACH",
    "ParkingLot_Attachment_Relation", "SIMPLE",
    "Photos", "Parking Lot",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
arcpy.CreateRelationshipClass_management(
    "TRAILS_LN", "AKR_ATTACH",
    "Trail_Attachment_Relation", "SIMPLE",
    "Photos", "Trail",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
arcpy.CreateRelationshipClass_management(
    "TRAILS_FEATURE_PT", "AKR_ATTACH",
    "TrailFeature_Attachment_Relation", "SIMPLE",
    "Photos", "Trail Feature",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
arcpy.CreateRelationshipClass_management(
    "ROADS_FEATURE_PT", "AKR_ATTACH",
    "RoadFeature_Attachment_Relation", "SIMPLE",
    "Photos", "Road Feature",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
arcpy.CreateRelationshipClass_management(
    "AKR_ASSET_PT", "AKR_ATTACH",
    "MiscPointFeatures_Attachment_Relation", "SIMPLE",
    "Photos", "Misc Feature",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
arcpy.CreateRelationshipClass_management(
    "AKR_ASSET_LN", "AKR_ATTACH",
    "MiscLineFeatures_Attachment_Relation", "SIMPLE",
    "Photos", "Misc Feature",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
arcpy.CreateRelationshipClass_management(
    "AKR_ASSET_PY", "AKR_ATTACH",
    "MiscPolyFeatures_Attachment_Relation", "SIMPLE",
    "Photos", "Misc Feature",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
# TODO: Non-Geo Photos can also be linked by GEOMETRYID to a GIS Feature
# GeoPhotos to GIS Features
arcpy.CreateRelationshipClass_management(
    "AKR_BLDG_PT", "AKR_ATTACH_PT",
    "BuildingPoint_AttachmentPoint_Relation", "SIMPLE",
    "GeoPhotos", "Building Point",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
arcpy.CreateRelationshipClass_management(
    "AKR_BLDG_PY", "AKR_ATTACH_PT",
    "BuildingPoly_AttachmentPoint_Relation", "SIMPLE",
    "GeoPhotos", "Building Poly",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
arcpy.CreateRelationshipClass_management(
    "ROADS_LN", "AKR_ATTACH_PT",
    "Road_AttachmentPoint_Relation", "SIMPLE",
    "GeoPhotos", "Road",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
arcpy.CreateRelationshipClass_management(
    "PARKLOTS_PY", "AKR_ATTACH_PT",
    "ParkingLot_AttachmentPoint_Relation", "SIMPLE",
    "GeoPhotos", "Parking Lot",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
arcpy.CreateRelationshipClass_management(
    "TRAILS_LN", "AKR_ATTACH_PT",
    "Trail_AttachmentPoint_Relation", "SIMPLE",
    "GeoPhotos", "Trail",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
arcpy.CreateRelationshipClass_management(
    "TRAILS_FEATURE_PT", "AKR_ATTACH_PT",
    "TrailFeature_AttachmentPoint_Relation", "SIMPLE",
    "GeoPhotos", "Trail Feature",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
arcpy.CreateRelationshipClass_management(
    "ROADS_FEATURE_PT", "AKR_ATTACH_PT",
    "RoadFeature_AttachmentPoint_Relation", "SIMPLE",
    "GeoPhotos", "Road Feature",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
arcpy.CreateRelationshipClass_management(
    "AKR_ASSET_PT", "AKR_ATTACH_PT",
    "MiscPointFeatures_AttachmentPoint_Relation", "SIMPLE",
    "GeoPhotos", "Misc Feature",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
arcpy.CreateRelationshipClass_management(
    "AKR_ASSET_LN", "AKR_ATTACH_PT",
    "MiscLineFeatures_AttachmentPoint_Relation", "SIMPLE",
    "GeoPhotos", "Misc Feature",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
arcpy.CreateRelationshipClass_management(
    "AKR_ASSET_PY", "AKR_ATTACH_PT",
    "MiscPolyFeatures_AttachmentPoint_Relation", "SIMPLE",
    "GeoPhotos", "Misc Feature",
    "NONE", "ONE_TO_MANY", "NONE",
    "FEATUREID", "FEATUREID"
)
# fmt: on
