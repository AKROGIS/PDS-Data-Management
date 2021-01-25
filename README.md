# Tools for PDS Management

A collection of tools (mainly python scripts) for managing the Permanent
Data Set (PDS) of the Alaska Region GIS Team of the National Park Service.

These tools are specific to the NPS, and have very limited general application.
There is very little documentation provided, but most of the scripts are short
and easily understood.

## Contents

A description of the contents of the folders in the repo follows.

### `Facility-Sync`

Instructions and a script for creating a new facilities FGDB from the master
data in SDE.  It also includes a generic SDE to FGDB export tool.

### `ifsar_readmes`

Contains documentation on the IfSAR update process as well as details to
verify the contents of the PDS with all of the distribution disks from USGS.

### `ifsar_scripts`

Scripts for processing IfSAR submittals.  See the IfSAR
[Update Process](ifsar_readmes\Update%20Process.md) for details.
This folder is no longer active as the last of the IfSAR data was
received in January 2021.

### `misc-reorg-scripts`

Scripts developed during the PDS (X drive) reorganization in 2017.  Many of
these scripts were to better understand the contents of the old PDS, and to
verify that the contents of the reorganized PDS were complete.  These scripts
have very little value as is now that the reorganization is complete, but
they can be valuable as a starting point for similar tools.

### `remote-mover`

A tool to run as a scheduled task before the nightly robocopy of the PDS to
the parks.  This tool uses the moves database to identify changes that can
be more efficiently accomplished by moving data on the remote servers before
robocopy tries to delete the old and transmit the new data to the the server.

### `robo-copy`

DOS batch files, that run as a nightly task, to use robocopy to sync the Park
servers with changes to the PDS.  Also includes a batch file to use robocopy
to sync an external drive with changes to the PDS.

### `sfm_processing`

Batch files, [GDAL](https://gdal.org/) scripts,
[ArcGIS raster processing templates](https://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/adding-a-processing-template-to-a-mosaic-dataset.htm)
and metadata templates for use in processing and publishing Structure From
Motion (SFM) datasets created by the NPS.

### `x-mappings`

Batch files to manage remapping a user's profile from the old X drive (PDS)
to the new X drive.  Also includes a script to create an X drive mapping for
a system account (like `arcgis` for the ArcGIS Server) on another server.

## Build

There is nothing to build to use these tools.

## Deploy

Most of these tools do not need to be deployed.  Just clone this repository
to a local file system.  The exceptions are:

* `remote_mover` - copy this folder to the GIS application server, and create a
  scheduled task to run `remote_mover.py` with python 2.7 or python 3.x. Review
  and edit if necessary `config_file.py` to set paths to the moves database and
  folder of server junction points (See the `robo-copy` below). Review and edit
  if necessary `config_logger.py` to set the logging parameters.  The scheduled
  task should execute at least 5 minutes before the robocopy task begins. This
  task must be run with the same account that runs the `robo-copy` tasks below.
  This account must have write permission to the deployed folder to update the
  timestamp and log files. After installing (and when there are no new moves in
  the database) the script should be run once manually with the -s option and a
  date in the future.  This will create a timestamp file for the next run.
* `robo-copy` -  - copy this folder contents to a folder on the GIS application
  server. The scripts assume the folder will be `E:\XDrive\UpdateTools`. Run
  [x-mappings/make-remote-server-links.bat](x-mappings/make-remote-server-links.bat)
  to create the server junction points at `E:\XDrive\RemoteServers`.  The
  scripts also expect a folder for logs at `E:\Xdrive\Logs`. If you want or need
  to change either of these paths, then edit the scripts as necessary. Create
  a scheduled task to run `robo-scheduler.bat` in the evening and `robo-kill.bat`
  in the morning.  The two `xml` files can be imported to the scheduled task
  console for this purpose. These tasks must be run with a NPS system account
  that has permissions to write to the Park GIS server (but not the regional
  GIS server). See the password keeper on the GIS team drive for authentication
  details, or contact IT.
* `x-mappings` - Therein lies an importable scheduled task (and `bat` file) that
  will create an X-drive mapping for the system account that runs ArcGIS server.
  This task needs to be deployed on each server with ArcGIS server and set to
  run before ArcGIS server starts.  This allows the ArcGIS to use the raster
  mosaic datasets that have X-drive paths embedded in them for the source and
  overview rasters.

## Use

### Python

Before executing a python script, open it in a text editor and check any
path or file names in the script that should be edited to reflect the
file system where the script and data are deployed.  The script can then
be run in a CMD/Powershell window, with the
[IDLE](https://en.wikipedia.org/wiki/IDLE) application,
with the
[Python extension to VS Code](https://code.visualstudio.com/docs/languages/python),
or any other Python execution environment.  All scripts work with Python 2.7 and
most will also work with Python 3.  The "obsolete" scripts in `ifsar_scripts`
and `misc-reorg-scripts` have not been tested with Python 3, but the others have
been.

### SQL Scripts

1) Open the script file in SQL Server Management Studio
([SSMS](https://docs.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms?view=sql-server-ver15)),
or [Azure Data Studio](https://docs.microsoft.com/en-us/sql/azure-data-studio/download-azure-data-studio?view=sql-server-ver15).
2) Connect to the appropriate server and database.
3) Select the statement you want to run and click `Run` in the toolbar.
   When applicable, see the comments in the file, you can run all the SQL
   commands in the file sequentially by clicking `Run` when nothing is selected.
