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
   - Either replace or append to the table `ifsar_tif_new_x_supp2` in the
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
9. Add new rasters to Mosaic
   - Copy `\Mosaics\Statewide\DEMs\SDMI_IFSAR.gdb` and Overviews to
     an editable location (`C:\tmp`) a portable HD copy of the X drive
     mounted as `X:` is the most fool proof.
   - Edit and run the script `pds-reorg/organize_ifsar.py` for each
     mosaic dataset.
11. Update Overviews
12. Test
10. Update Metadata


