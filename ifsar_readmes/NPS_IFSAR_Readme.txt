IFSAR Organization and NPS Modifications
========================================

This file documents all the changes we (NPS AKR GIS Team) have made to the
originally delivered IFSAR data.  If you had to rebuild this folder, you would
create the folders described in the adjacent file *NPS_IFSAR_Folders.txt* from
the distribution disks, described in the adjacent file *NPS_IFSAR_Manifest.txt*.
Then you would apply the changes described in this document.

Find duplicates and other problems
----------------------------------
 * List the tif images in X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR with https://github.com/regan-sarwas/pds-reorg/blob/master/list-images.py
 * Add additional attributes to this list with https://github.com/regan-sarwas/pds-reorg/blob/master/organize_ifsar.py
 * Import this list into SQL Server
 * Analyze with https://github.com/regan-sarwas/pds-reorg/blob/master/Ifsar%20file%20analysis.sql
 * Once problems are addressed, export the list of tif files for each mosaic.

Update Summer_2016_Lot1
-----------------------
The  original submittal of Summer_2016_Lot1 was placed in
**2017_IFSAR\disk2\AK_IFSAR_copies\Summer_2016_Lot1**, It was resubmitted
with minor changes as **2017_IFSAR\Deliveries_5Dec2017\Summer_2016_Lot1**,
creating duplicates. The original submittal folder was updated with just the
changes from the resubmittal, and then the resubmittal was deleted. See the
file **Readme.txt** in 2017_IFSAR\Deliveries_5Dec2017\Summer_2016_Lot1 for
details of the differences, and which files were updated.
The X drive was updated on 2018-05-24.

Update Summer_2016_Lot04
------------------------
The  original submittal of Summer_2016_Lot04 was placed in
**2017_IFSAR\IfSAR Delieveries\Summer_2016_Lot4_Cell_150** and only contained
Cell 150.  It was resubmitted with minor changes to Cell 150 and as 5 new cells
as **2017_IFSAR\Deliveries_5Dec2017\Summer_2016_Lot04**, creating duplicates.
I documented the differences between the submittals, and deleted the first
partial submittal.  For details, see the readme.txt and checksum file in
**2017_IFSAR\IfSAR Delieveries\Summer_2016_Lot4_Cell_150**.

Removed old style stats
-----------------------
Older submittals have old style stats files (*.aux). These cause a huge bloat in
the raster mosaic (creating a GB sized table, which should only be a few MB).
Deleting the aux files and recreating the mosaic yields a much smaller raster mosaic.
The old stats are in the following folders:
  * FEDI_Data (except Copper River and Glacier_Bay sub-folders)
  * Final_EdgeMatched_Data
  * Intermap_Data

The full list of files is in the adjacent file *old_style_stats.txt* (each line
is a file without the X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR\ prefix).  The
Python script *remove_old_stats.py* will remove each file in the list.

Removed Legacy IFSAR
--------------------
As of October 2018, the newer IFSAR data overlaps most of the Legacy data
in **GINA_CIAP_G7317** making it obsolete.  The data for NPRA, Adak, Akun,
Merrill Pass and Rainy Pass is not yet covered.  NPRA was received direct from
BLM, and is in **X:\Extras\AKR\Statewide\DEM\NPRA-IfSAR_Intermap_2002**.  The
others have been reformatted to remove short comings, and are in
**X:\Extras\AKR\Statewide\DEM\Legacy_IFSAR**. Details of the reformatting are in
readme files in the sub folders.

To Do
-----
* Fix mosaic
  - remove paths to SDMI_IFSAR\2017_IFSAR\disk4
  - remove paths to Summer_2016_Lot4_Cell_150

  if I do this on the existing geodatabase the small update
  happens in a multi-GB file, which will be impossible to robo copy
  to several parks - need to delete the old style stats first and rebuild the mosaic.
* Use arcpy to recalc
  stats at 1,1 with ignore values of -10000 and -32767.  This creates a
  new *.tif.aux.xml and creates (or updates) a *.tif.xml file to document the process.
  The files with old stats are listed in ...
* remove/replace old pyramid (*.rrd) file??
* delete overviews for not used files
