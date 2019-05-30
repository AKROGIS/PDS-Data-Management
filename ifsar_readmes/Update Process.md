PDS Update Process for IFSAR data
=================================

1. Get a new disk from Beth Kolton
   - She copies/compiles USGS delivery disks onto an I&M Archive portable HD
2. Copy the disk contents to the X drive
   - Put it in a year folder in `X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR`
   - The year is when the data was received at NPS
   - Create the year folder if needed (e.g `2019_IFSAR`)
   - Minimal path consolidation and renaming is acceptable (see 2019_IFSAR)
   - Do not copy manifest list or system files
   - Update `NPS_IFSAR_Folders.txt` and `NPS_IFSAR_Manifest.txt` in `X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR\_README`
   - Label the package for the I&M Archive portable HD with the 
     next available **X#** number (see the manifest document)
3. Return the disk to Beth
   - or put in the I&M cabinet)
4. Create a list of `.tif` files for analysis
   - This can be just the newly added files, or all the files in `SDMI_IFSAR`
   - Tools are in `https://github.com/regan-sarwas/pds-reorg`
   - Edit the last line of `pds-reorg/list-images.py`
   - Use a new output filename for the csv data
   - The search path can be just the new data (faster) or all the IFSAR data
   - Run `pds-reorg/list-images.py`
   - Edit `pds-reorg/organize_ifsar.py`
   - Edit lines 14 and 15 to set the input and output csv files.  The input
     to this command is the output from the previous command.
   - Run `pds-reorg/organize_ifsar.py`
   - Use Atom (not VS Code) to replace CRLF line endings with LF endings
     (required for SQL import)
   - Either replace or append to the table `ifsar_tif_all` in the
     SQLServer database `reorg` on `INPAKRO42492` depending on if a full or
     just new search of the SDMI_IFSAR tree was done.
   - If the database or table does not exist, it can be created from scratch
     (use `Tasks` -> `Import From Flatfile...` using SSMS in any database)
     from the output of `pds-reorg/organize_ifsar.py` as long as the full
     IFSAR tree was searched.
5. Analyze the data for issues
   - Use SQL queries in `pds-reorg/Ifsar file analysis.sql` and
     `pds-reorg/Ifsar file analysis2.sql` to ...
   - Identify tiles to skip
   - Identify dups, mismatches or other anomolies
   - Identify old style stats files
6. Repair data on the X Drive
   - For example, replace old style stats files
   - Delete duplicate data (resubmittals)
   - Document changes in `X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR\_README\NPS_IFSAR_Readme.txt`
7. Delete outdated rasters from Mosaic
   - Only if data is a resubmittal
   - Details to follow (after next resubmittal)
8. Create the list of tif files to import
   - One per each mosaic dataset in `X:\Mosaics\Statewide\DEMs\SDMI_IFSAR.gdb`
   - Use SQL EXPORT queries at the end of `pds-reorg/Ifsar file analysis.sql`
   - Save exports as `csv` files in `pds-reorg\data`
   - SSMS adds a utf8 BOM at the begining of the file.  The easiest way to deal
     with this is add a column name row at the top that is skipped.
9. Add new rasters to Mosaic
   - Copy `\Mosaics\Statewide\DEMs\SDMI_IFSAR.gdb` and Overviews to
     an editable location (`C:\tmp`) a portable HD copy of the X drive
     mounted as `X:` is the most fool proof.
   - Edit and run the script `pds-reorg/build_mosaics.py` for each
     mosaic dataset.
10. Add functions to the input rasters
    - Add Mosaics to ArcMap, and select the new footprints, then use
      `Selection` -> `Batch Edit Raster Functions` from the context menu,
      or the `Field Calculator` from the table view. 
    - Check/Set MaxPS to 6.25 for all ORI, and 15 for all DTM/DSM
    - Add masks for nodata = 0 and nodata = 1 for the ori images
    - Add no data masks to the dtm and dsm if needed (typically only along border).
11. Update Overviews
    - If you made a copy, fix the paths of the writable copy of the overviews
      - **Not required** toolbox will create necessary folders (paths to existing
         overviews need to be valid)
      - right click, `Remove` -> `Reset Relative Path`
      - right click, `Modify` -> `Repair...` and replace the X drive path to the
        overviews to the writable copy.
    - Define Overviews
      - **Do not** use `Optimize` -> `Define Overviews...` in the context menu
      - Use `Optimize` -> `Build Overviews...` in the context menu with the
        following options:
      - Define Missing Overview Tiles (optional): ON
      - Generate Overviews (optional): OFF
      - Generate Missing Overview Images Only (optional): ON
      - Generate Stale Overview Images Only (optional): ON
      - The second two will be grayed out, when the second option is off,
        but I think they still apply.
    - Build Overviews for new overviews
      - Use `Optimize` -> `Build Overviews...` in the context menu with the
        following options:
      - Query Definition (optional): `Category = 3`
      - Define Missing Overview Tiles (optional): OFF
      - Generate Overviews (optional): ON
      - Generate Missing Overview Images Only (optional): ON
      - Generate Stale Overview Images Only (optional): ON
    - Use ArcMap to find the OBJECTID of the overviews at a higher level than the new
      ones, in the same area as the new tiles.  These overviews exist but will need to
      be updated.  Close ArcMap and update them with following:
      - Use `Optimize` -> `Build Overviews...` in the context menu with the
        following options:
      - Query Definition (optional): `OBJECTID in (xx, yy, ... zz)` (replace `xx`,
        etc with the overview needing updating)
      - Define Missing Overview Tiles (optional): OFF
      - Generate Overviews (optional): ON
      - Generate Missing Overview Images Only (optional): OFF
      - Generate Stale Overview Images Only (optional): OFF
    - You cannot Define and Build overviews in one step,  because despite the options
      to only updated the stale and new it will recreate all.
12. Test
13. Update Metadata
14. Update the PDS
    - Copy to the new gdb and new overview files to the X drive
    - Fix the overview paths:
      - right click, `Remove` -> `Reset Relative Path`
      - right click, `Modify` -> `Repair...` and replace the 
        path to the writable overviews with the X drive path.
