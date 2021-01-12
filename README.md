# Tools for PDS Management

A collection of tools (mainly python scripts) for managing the Permanent
Data Set (PDS) of the Alaska Region GIS Team of the National Park Service.

These tools are specific to the NPS, and have very limited general application.
There is very little documentation provided, but most of the scripts are short
and easily understood.

A description of the contents of the folders in the repo follows.

## `Facility-Sync`

Instructions and a script for creating a new facilities FGDB from the master
data in SDE.  It also includes a couple of attempts at a generic SDE to FGDB
sync tool.

## `ifsar_readmes`

Contains documentation on the IFSAR update process as well as details to
verify the contents of the PDS with all of the distribution disks from USGS.

## `misc-reorg-scripts`

Scripts developed during the PDS (X drive) reorganization in 2017.  Many of
these scripts were to better understand the contents of the old PDS, and to
verify that the contents of the reorganized PDS were complete.  These scripts
have very little value as is now that the reorganization is complete, but
they can be valuable as a starting point for similar tools.

## `remote-mover`

A tool to run as a scheduled task before the nightly robocopy of the PDS to
the parks.  This tool uses the moves database to identify changes that can
be more efficiently accomplished by moving data on the remote servers before
robocopy tries to delete the old and transmit the new data to the the server.

## `robo-copy`

DOS batch files, that run as a nightly task, to use robo copy to sync the Park
servers with changes to the PDS.  Also includes a batch file to use robocopy
to sync an external drive with changes to the PDS.

## `sfm_processing`

Batch files, [GDAL](https://gdal.org/) scripts,
[ArcGIS raster processing templates](https://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/adding-a-processing-template-to-a-mosaic-dataset.htm)
and metadata templates for use in processing and publishing Structure From
Motion (SFM) datasets created by the NPS.

## `x-mappings`

Batch files to manage remapping a user's profile from the old X drive (PDS)
to the new X drive.  Also includes a script to create an X drive mapping for
a system account (like `arcgis` for the ArcGIS Server) on another server.
