-- Mosaic Datasets in Theme Manager (163)
SELECT workspace_Path, Data_Source
  FROM ThemeManager_20171030
where [Data_Set_Type] = 'MosaicDataset'

-- X-drive Mosaic datasets referenced in TM (155)
SELECT fgdb, mosaic
  FROM mosaic_images_20171121 as i
  group by fgdb, mosaic
  order by fgdb, mosaic

-- X-drive Mosaic datasets referenced in TM (117)
SELECT fgdb, mosaic --, folder
  FROM mosaic_images_20171121 as i
  left join ThemeManager_20171030 as t
  on t.workspace_Path = i.fgdb and t.Data_Source = i.mosaic
  where t.workspace_Path is not NULL
  group by fgdb, mosaic --, folder
  order by fgdb, mosaic --, folder

-- Mosaic Rasters in TM that are not in the X drive (26) All Reference Mosaics?
SELECT workspace_Path, Data_Source
  FROM ThemeManager_20171030 as t
  left join mosaic_images_20171121 as i
  on t.workspace_Path = i.fgdb and t.Data_Source = i.mosaic
  where [Data_Set_Type] = 'MosaicDataset'
  and i.fgdb is null

-- Image Folders in X-drive IKONOS Mosaic datasets referenced in TM (51)
SELECT fgdb, mosaic, folder
  FROM mosaic_images_20171121 as i
  left join ThemeManager_20171030 as t
  on t.workspace_Path = i.fgdb and t.Data_Source = i.mosaic
  where fgdb like '%IKONOS%' and t.workspace_Path is not Null
  group by fgdb, mosaic, folder
  order by fgdb, mosaic, folder

-- Mosaic datasets on X drive not referenced by TM (38)
SELECT fgdb, mosaic, folder
  FROM mosaic_images_20171121 as i
  left join ThemeManager_20171030 as t
  on t.workspace_Path = i.fgdb and t.Data_Source = i.mosaic
  where t.workspace_Path is Null
  and fgdb like '%IKONOS%'
  group by fgdb, mosaic, folder
  order by folder, fgdb, mosaic

-- Mosaic datasets on AIS (services)
SELECT fgdb, mosaic, folder
  FROM mosaic_images_20171121
  where fgdb like '%IKONOS%'
  group by fgdb, mosaic, folder
  order by folder, fgdb, mosaic

-- Image Folders in Mosaics on AIS (services)
SELECT fgdb, mosaic, folder
  FROM mosaic_images_20171121
  where folder like '\\inpakrovmais\Data\%' and folder not like '%.Overviews'
  group by fgdb, mosaic, folder
  order by folder, fgdb, mosaic

-- Match mosaics on dist and ais
  SELECT X.fgdb, X.mosaic, Z.fgdb
  FROM (SELECT fgdb, mosaic
  FROM mosaic_images_20171121
  group by fgdb, mosaic) AS Z
JOIN
  (SELECT fgdb, mosaic
  FROM mosaic_images_20171121
  group by fgdb, mosaic) AS X
  ON X.mosaic = z.mosaic
  order by X.mosaic --, X.folder

  -- TIFF Image folders (except overviews) feeding mosaics
  select * from
  	(SELECT folder from mosaic_images
  	where (size > -1 or left(folder, 4) = '.gdb') and left(folder, 8) <> 'X:\SDMI\'
  	and folder not like '%.Overviews' and folder not like '\\inpakrovmdist\GISData\SDMI\%'
  	group by folder
  	union
  	select 'X:\SDMI\IFSAR\' as folder
  	union
  	select 'X:\SDMI\SPOT5\' as folder) as folder
  order by folder


  --  Raster Mosaics with issues
  select * from mosaics_20171130 where contents = 'Mixed' or errors is not null

  SELECT folder FROM mosaic_images group by folder order by folder
  SELECT folder FROM mosaic_images where folder not like '%.Overviews%' group by folder order by folder

  select count(*) from mosaic_images

  SELECT fgdb from mosaics_20171130 group by fgdb order by fgdb

  --All mossics not moved to new Mosaics folder
  select m.fgdb from (select fgdb from mosaics_20171130 group by fgdb having fgdb like 'X:%') as m
  left join moves_dist as d on m.fgdb = 'X:\' + d.original
  where d.internal is null or d.internal not like 'Mosaics%'
  union
  select m.fgdb from (select fgdb from mosaics_20171130 group by fgdb having fgdb like 'Z:%') as m
  left join moves_ais as d on m.fgdb = 'Z:\' + d.original
  where d.internal is null or d.internal not like 'Mosaics%'
  order by m.fgdb

  -- SPOT5
  select * from mosaic_images where folder like '%SPOT5%' order by extension, folder -- All Paths
  select extension, count(*) from mosaic_images where folder like '%SPOT5%' group by extension -- All Paths
  select * from mosaic_images where folder like '%\SDMI\SPOT5\%' order by extension, folder  -- paths on dist (or X)
  select extension, count(*) from mosaic_images where folder like '%\SDMI\SPOT5\%' group by extension  -- paths on dist (or X)
  -- SPOT5 paths not on dist (or X)  -- just overviews and some wierd self reference X:\Albers\base\Imagery\SPOT5\SDMI.gdb\AMD_SPOT5_CIR1_CAT
  select * from mosaic_images where folder like '%SPOT5%' and folder not like '%\SDMI\SPOT5\%' order by extension, folder
  select * from mosaic_images where folder like '%SPOT5%' and folder not like '%\SDMI\SPOT5\%' and folder not like '%.Overviews%' order by extension, folder


  -- IFSAR
  select * from mosaic_images where folder like '%IFSAR%' order by extension, folder -- All Paths
  select extension, count(*) from mosaic_images where folder like '%IFSAR%' group by extension -- All Paths
  select * from mosaic_images where folder like '%\SDMI\IFSAR\%' order by extension, folder  -- paths on dist (or X)
  select extension, count(*) from mosaic_images where folder like '%\SDMI\IFSAR\%' group by extension  -- paths on dist (or X)
  -- IFSAR paths not on dist (or X)  -- just overviews others referencing the mosaic (on Z and on X)
  select * from mosaic_images where folder like '%IFSAR%' and folder not like '%\SDMI\IFSAR\%' order by extension, folder
  select * from mosaic_images where folder like '%IFSAR%' and folder not like '%\SDMI\IFSAR\%' and folder not like '%\Mosaics\%' and folder not like '%.Overviews%' order by extension, folder


  -- Find Matches in Lake Clark IKONOS folders on X/Z

  -- nothing on x is in z
  SELECT *
  from lacl_Ikonos_tif_x as x
  left join lacl_Ikonos_tif_z as z
  -- on x.filename = z.filename and x.size = z.size  -- nothing
  on x.size = z.size  -- one match

  -- nothing on z is in z
  SELECT *
  from lacl_Ikonos_tif_z as z
  left join lacl_Ikonos_tif_x as x
  -- on x.filename = z.filename and x.size = z.size  -- nothing
  on x.size = z.size  -- one match

  select sum(size)/1024/1024/1024 from lacl_Ikonos_tif_x  --564 GB
  select sum(size)/1024/1024/1024 from lacl_Ikonos_tif_z  --509 GB


  -- Find Matches in SPOT5

  -- 13 images on x are not on z
  SELECT *
  from spot_tif_x as x
  left join spot_tif_z as z
  on x.filename = z.filename and x.size = z.size
  --where z.folder is not null  -- 17295 matches found
  where z.folder is null  -- 13 not found on Z
  --where x.folder = 'X:\SDMI\SPOT5\SPOT5.SDMI.ORTHO.20110517.0970_1228' -- 3 => Z:\SPOT5\SDMI.ORTHO.2010\SPOT5.SDMI.ORTHO.2010.0970_1228
  --where x.folder = 'X:\SDMI\SPOT5\SPOT5.SDMI.ORTHO.20110517.0998_1232' -- 3 => Z:\SPOT5\SDMI.ORTHO.2010\SPOT5.SDMI.ORTHO.2010.0998_1232
  --where x.folder = 'X:\SDMI\SPOT5\SPOT5.SDMI.ORTHO.20111206.1036_1226' -- 3 => Z:\SPOT5\SDMI.ORTHO.2010\SPOT5.SDMI.ORTHO.2010.1036_1226
  --where x.folder = 'X:\SDMI\SPOT5\SPOT5.SDMI.ORTHO.20111206.1050_1224' -- 3 => Z:\SPOT5\SDMI.ORTHO.2010\SPOT5.SDMI.ORTHO.2010.1050_1224
  --where x.folder = 'X:\SDMI\SPOT5\SPOT5.SDMI.ORTHO.20111206.1044_1224' -- 1 => Z:\SPOT5\SDMI.ORTHO.2010\SPOT5.SDMI.ORTHO.2010.1044_1224

  -- everything on z is in x (except 150 (2 unique) control point images)
  SELECT *
  from spot_tif_z as z
  left join spot_tif_x as x
  on x.filename = z.filename and x.size = z.size
  where z.filename not like 'GCP%'
  --and x.folder is not null  -- 17445 found - 150 (like GCP%) that are dups = 17295 matches found
  and x.folder is null  -- 0 not found

  -- find dups
  select filename, size, count(*) from spot_tif_x group by filename, size having count(*) > 1  --none
  select filename, size, count(*) from spot_tif_z group by filename, size having count(*) > 1  --2*75 = 150

  select * from spot_tif_z where filename like 'GCP%'

  -- SPOT% Mosaic repair mapping
  select m.fgdb, m.mosaic, m.folder, 
         replace(z.folder, 'Z:\SPOT5', 'X:\Extras\AKR\Statewide\Imagery\SDMI_SPOT5') as new_folder
  from mosaic_images as m
  left join SPOT_TIF_Z as z
  on m.filename = z.filename and m.size = z.size
 where m.folder like '%SPOT5%' and z.folder is not null --and mosaic = 'SPOT5_CIR'
 group by m.fgdb, m.mosaic, m.folder,
         replace(z.folder, 'Z:\SPOT5', 'X:\Extras\AKR\Statewide\Imagery\SDMI_SPOT5')
order by m.folder

   -- SPOT5 overview Mosaic repair mapping
  select fgdb, mosaic, folder, 
         replace(folder, 'X:\Albers\base\Imagery\SPOT5\SDMI.Overviews', 'X:\Mosaics\Statewide\Imagery\SDMI_SPOT5.Overviews') as new_folder
  from mosaic_images
 where folder like '%SPOT5%' and folder like '%.Overviews%'
 group by fgdb, mosaic, folder, 
         replace(folder, 'X:\Albers\base\Imagery\SPOT5\SDMI.Overviews', 'X:\Mosaics\Statewide\Imagery\SDMI_SPOT5.Overviews')

-- IFSAR Mosaic repair mapping: SIZE EQUAL
  select m.fgdb, m.mosaic, m.folder + '\' + m.filename as old_name, 
         replace(z.folder, 'Z:\IFSAR', 'X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR') + '\' + z.filename as new_name
  from mosaic_images as m
  left join IFSAR_TIF_Z as z
  on m.filename = z.filename and m.size = z.size
 where m.folder like '%IFSAR%' and z.folder is not null

-- IFSAR Mosaic repair mapping: SIZE NOT EQUAL
  select m.fgdb, m.mosaic, m.folder + '\' + m.filename as old_name, 
         replace(z.folder, 'Z:\IFSAR', 'X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR') + '\' + z.filename as new_name
  from mosaic_images as m
  left join IFSAR_TIF_Z as z
  on m.filename = z.filename and m.size != z.size
 where m.folder like '%IFSAR%' and z.folder is not null

 -- IFSAR overview Mosaic repair mapping: SIZE EQUAL
  select m.fgdb, m.mosaic, m.folder + '\' + m.filename as old_name, 
         replace(z.folder, 'Z:\IFSAR', 'X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR') + '\' + z.filename as new_name
  from mosaic_images as m
  left join IFSAR_TIF_Z as z
  on m.filename = z.filename and m.size = z.size
 where m.folder like '%IFSAR%' and m.folder like '%.Overviews%'

-- IFSAR overview Mosaic repair mapping: SIZE NOT EQUAL
  select m.fgdb, m.mosaic, m.folder + '\' + m.filename as old_name, 
         replace(z.folder, 'Z:\IFSAR', 'X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR') + '\' + z.filename as new_name
  from mosaic_images as m
  left join IFSAR_TIF_Z as z
  on m.filename = z.filename and m.size != z.size
 where m.folder like '%IFSAR%' and m.folder like '%.Overviews%'



-- Find Matches in IFSAR

-- 3137 images on x are not on z (oh boy.. sigh..)
-- all (10030) are found if I only check the name, and not the size.
SELECT *, (x.size - z.size)/(1.0 * x.size)
from ifsar_tif_x as x
left join ifsar_tif_z as z
--on x.filename = z.filename and x.size = z.size
--on x.size = z.size
on x.filename = z.filename
where z.folder is not null  -- 6773 matches found by name and size; 10030 by only name
--where z.folder is null  -- 3137 not found on Z by name and size; 0 not found by only name
--where x.folder like 'X:\SDMI\IFSAR\2012\%' -- => Z:\IFSAR\FEDI_Data\Copper_River\USGS_15_Tiles\*
--order by x.folder
order by Z.filename, (x.size - z.size)/(1.0 * x.size)

-- 5472 images on Z are not on X
SELECT *
from ifsar_tif_z as z
left join ifsar_tif_x as x
on x.filename = z.filename and x.size = z.size
--where x.folder is not null  -- 6773 matches found
where x.folder is null  -- 5472 not found

-- find dups
select filename, size, count(*) from ifsar_tif_x group by filename, size having count(*) > 1  --none
select filename, size, count(*) from ifsar_tif_z group by filename, size having count(*) > 1  --49*2 + 1*8 = 57 extras
select filename, count(*) from ifsar_tif_x group by filename having count(*) > 1  --none
select filename, count(*) from ifsar_tif_z group by filename having count(*) > 1  --176*2 + 1*8

select * from ifsar_tif_z where filename not like 'DTM%' and filename not like 'DSM%' and filename not like 'ORI%'
select * from ifsar_tif_x where filename = 'ak_90m_16bit_ellip_gf9_nonul'  -- 8 in z, 0 in x


-- Get mosaic repair data; does not work on IFSAR and SPOT5
SELECT
   i.fgdb as old_fgdb, i.mosaic,
   i.folder as old_folder,
   Coalesce('X:\' + d.internal, 'X:\' + a.internal) as new_fgdb,
   Replace(Replace(Coalesce(Replace(folder, d2.original, d2.new), Replace(folder, a2.original, a2.new)), '\\inpakrovmdist\gisdata\', 'X:\'), '\\inpakrovmais\data\', 'X:\') as new_folder
FROM
   (select fgdb, mosaic, folder from mosaic_images
    where folder not like '%SDMI\SPOT5%' AND folder not like '%SDMI\IFSAR%'
	group by fgdb, mosaic, folder) as i
LEFT JOIN moves_dist as d
   ON 'X:\' + d.original = i.fgdb
LEFT JOIN moves_ais as a
   ON 'Z:\' + a.original = i.fgdb
LEFT JOIN
   (select original, Coalesce(internal, external1, external2) as new from moves_dist) as d2
   ON i.folder like 'X:\' + d2.original + '%' OR i.folder like '\\inpakrovmdist\gisdata\' + d2.original +'%'
LEFT JOIN
   (select original, Coalesce(internal, external1, external2) as new from moves_ais) as a2
   ON i.folder like 'X:\' + a2.original + '%' OR i.folder like '\\inpakrovmdist\gisdata\' + a2.original +'%' OR i.folder like '\\inpakrovmais\data\' + a2.original +'%'

--where i.fgdb like 'Z:\%'
--where Coalesce('X:\' + d.internal, 'X:\' + a.internal) is null
order by new_fgdb, new_folder

-- What are the possible starting points for fgdbs in mosaic images
select distinct left(fgdb,10) as sp from mosaic_images order by sp -- X:\ or Z:\

-- What are the possible starting points for images in fgdbs in mosaic images
select distinct left(folder,14) as sp from mosaic_images order by sp  -- X:\ or Z:\

-- Show me which mosaics have unusual paths to imagery
select * from mosaic_images where folder like 'X:\Local\%' or folder like 'X:\GLBA_Local\%' or folder like 'C:\%' or folder like 'E:\%' or folder like 'P:\%' or folder like '\\inpakrovmgis\%'
select fgdb, mosaic, folder from mosaic_images where folder like '\\inpakrovmais\%' group by fgdb, mosaic, folder

-- Get mosaic repair data (revised for new X paths); does not work on IFSAR and SPOT5
SELECT
   Null as old_fgdb,
   --i.fgdb as old_fgdb,
   i.mosaic,
   i.folder as old_folder,
   i.fgdb as new_fgdb,
   --Coalesce('X:\' + d.internal, 'X:\' + a.internal) as new_fgdb,
   Replace(Replace(Coalesce(Replace(folder, d2.original, d2.new), Replace(folder, a2.original, a2.new)), '\\inpakrovmdist\gisdata\', 'X:\'), '\\inpakrovmais\data\', 'X:\') as new_folder
FROM
   (select fgdb, mosaic, folder from mosaic_images
    where folder not like '%SDMI\SPOT5%' AND folder not like '%SDMI\IFSAR%'
	group by fgdb, mosaic, folder) as i
LEFT JOIN moves_dist as d
   ON 'X:\' + d.original = i.fgdb
LEFT JOIN moves_ais as a
   ON 'Z:\' + a.original = i.fgdb
LEFT JOIN
   (select original, Coalesce(internal, external1, external2) as new from moves_dist) as d2
   ON i.folder like 'X:\' + d2.original + '%' OR i.folder like '\\inpakrovmdist\gisdata\' + d2.original +'%'
LEFT JOIN
   (select original, Coalesce(internal, external1, external2) as new from moves_ais) as a2
   ON i.folder like 'X:\' + a2.original + '%' OR i.folder like '\\inpakrovmdist\gisdata\' + a2.original +'%' OR i.folder like '\\inpakrovmais\data\' + a2.original +'%'

--where i.fgdb like 'Z:\%'
--where Coalesce('X:\' + d.internal, 'X:\' + a.internal) is null
order by new_fgdb, new_folder



--- *********************************************
--- * Checks for final build of IFSAR/SPOT based on paths on new x (copy of ais/data)
--- *********************************************
SELECT * FROM [reorg].[dbo].[SPOT_TIF_x] where filename like '%cir'

SELECT *
  from spot_tif_x as x
  left join spot_tif_z as z
  on x.filename = z.filename and x.size = z.size
  --where z.folder is not null  -- 17295 matches found
  where z.folder is null  -- 13 not found on Z


select folder from spot_tif_z where filename like '%1044_1224%'

select m.fgdb, m.mosaic, m.folder + '\' + m.filename as old_name, 
         replace(z.folder, 'Z:\IFSAR', 'X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR') + '\' + z.filename as new_name
  from mosaic_images as m
  left join IFSAR_TIF_Z as z
  on m.filename = z.filename and m.size = z.size
 where m.folder like '%IFSAR%' and z.folder is not null and mosaic = 'ORI'

 --Compare DTM files
select * from mosaic_images where fgdb = 'X:\Mosaics\Statewide\DEMs\DEM_IFSAR.gdb' and mosaic = 'DTM'
   and folder not like '%.Overviews' order by filename  -- 3381 images (3044 unique)  that all start with 'DTM_'
select folder,filename, count(*) from mosaic_images where fgdb = 'X:\Mosaics\Statewide\DEMs\DEM_IFSAR.gdb' and mosaic = 'DTM'
   and folder not like '%.Overviews' group by folder,filename having count(*) > 1  -- 337 dups
select * from ifsar_tif_Z where filename like 'DTM_%'  -- 3208 Images
select * from ifsar_tif_X where filename like 'DTM_%'  -- 3124 Images

 --Compare DSM files
select * from mosaic_images where fgdb = 'X:\Mosaics\Statewide\DEMs\DEM_IFSAR.gdb' and mosaic = 'DSM'
    and folder not like '%.Overviews' order by filename  -- 3045 images that all start with 'DSM_'
select folder,filename, count(*) from mosaic_images where fgdb = 'X:\Mosaics\Statewide\DEMs\DEM_IFSAR.gdb' and mosaic = 'DSM'
    and folder not like '%.Overviews' group by folder,filename having count(*) > 1  -- No dups
select * from ifsar_tif_Z where filename like 'DSM_%'  -- 3208 Images
select * from ifsar_tif_X where filename like 'DSM_%'  -- 3125 Images

 --Compare ORI files
select * from mosaic_images where fgdb = 'X:\Mosaics\Statewide\Imagery\ORI_IFSAR.gdb' and mosaic = 'ORI'
    and folder not like '%.Overviews' order by len(filename)  -- 2708 images that all start with 'ORI_' only one ends with '_sup1'
select * from mosaic_images where fgdb = 'X:\Mosaics\Statewide\Imagery\ORI_IFSAR.gdb' and mosaic = 'ORI_SUP'
    and folder not like '%.Overviews' order by filename  -- 841 images (3549 total) that all start with 'ORI_' and end with '_sup%'
select folder,filename, count(*) from mosaic_images where fgdb = 'X:\Mosaics\Statewide\Imagery\ORI_IFSAR.gdb' and mosaic = 'ORI_SUP'
    and folder not like '%.Overviews' group by folder,filename having count(*) > 1  -- No dups
select * from ifsar_tif_Z where filename like 'ORI_%'  -- 4146 Images
select * from ifsar_tif_X where filename like 'ORI_%'  -- 3629 Images

select count(*) from ifsar_tif_Z  -- 12245
select * from ifsar_tif_Z where filename not like 'ORI_%' and  filename not like 'DSM_%' and  filename not like 'DTM_%' order by filename -- 1683 (not used)
select 4146+3208+3208+1683  -- 10562 + 1683 = 12245
select sum(size)/1024/1024/1024 from ifsar_tif_Z where filename not like 'ORI_%' and  filename not like 'DSM_%' and  filename not like 'DTM_%' -- 111 GB in unused tif images
select * from ifsar_tif_Z where filename not like 'ORI_%' and  filename not like 'DSM_%' and  filename not like 'DTM_%' and filename like '%ORI'  --1286
select * from ifsar_tif_Z where filename not like 'ORI_%' and  filename not like 'DSM_%' and  filename not like 'DTM_%' and (filename like '%_dem' or filename like '%_dtm') --363
select * from ifsar_tif_Z where filename not like 'ORI_%' and  filename not like 'DSM_%' and  filename not like 'DTM_%' and filename not like '%_dem' and filename not like '%_dtm' and filename not like '%ORI' --34

select replace(folder,'Z:\IFSAR', 'X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR') + '\' + filename + ext from ifsar_tif_Z where filename like 'DTM_%' -- 3208
select replace(folder,'Z:\IFSAR', 'X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR') + '\' + filename + ext from ifsar_tif_Z where filename like 'DSM_%' -- 3208
select replace(folder,'Z:\IFSAR', 'X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR') + '\' + filename + ext from ifsar_tif_Z where filename like 'ORI_%' and filename not like '%_sup%'  -- 3141
select replace(folder,'Z:\IFSAR', 'X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR') + '\' + filename + ext from ifsar_tif_Z where filename like 'ORI_%sup%' -- 1005

select replace(folder,'Z:\IFSAR', 'X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR') + '\' + filename + ext from ifsar_tif_Z where filename not like 'ORI_%' and  filename not like 'DSM_%' and  filename not like 'DTM_%' and filename like '%ORI'  --1286

select replace(folder,'Z:\IFSAR', 'X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR') + '\' + filename + ext from ifsar_tif_Z where filename not like 'ORI_%' and  filename not like 'DSM_%' and  filename not like 'DTM_%' and (filename like '%_dem' or filename like '%_dtm') --363


