-- Mosaic Datasets in Theme Manager (163)
SELECT workspace_Path, Data_Source
  FROM [Scratch].[dbo].[TM_20171030]
where [Data_Set_Type] = 'MosaicDataset'

-- X-drive Mosaic datasets referenced in TM (155)
SELECT gdb, item
  FROM [Scratch].[dbo].[IMAGES_X] as i
  group by gdb, item
  order by gdb, item

-- X-drive Mosaic datasets referenced in TM (117)
SELECT gdb, item --, folder
  FROM [Scratch].[dbo].[IMAGES_X] as i
  left join [Scratch].[dbo].[TM_20171030] as t
  on t.workspace_Path = i.gdb and t.Data_Source = i.item
  where t.workspace_Path is not NULL
  group by gdb, item --, folder
  order by gdb, item --, folder

-- Mosaic Rasters in TM that are not in the X drive (26) All Reference Mosaics?
SELECT workspace_Path, Data_Source
  FROM [Scratch].[dbo].[TM_20171030] as t
  left join [Scratch].[dbo].[IMAGES_X] as i
  on t.workspace_Path = i.gdb and t.Data_Source = i.item
  where [Data_Set_Type] = 'MosaicDataset'
  and i.gdb is null

-- Image Folders in X-drive IKONOS Mosaic datasets referenced in TM (51)
SELECT gdb, item, folder
  FROM [Scratch].[dbo].[IMAGES_X] as i
  left join [Scratch].[dbo].[TM_20171030] as t
  on t.workspace_Path = i.gdb and t.Data_Source = i.item
  where gdb like '%IKONOS%' and t.workspace_Path is not Null
  group by gdb, item, folder
  order by gdb, item, folder

-- Mosaic datasets on X drive not referenced by TM (38)
SELECT gdb, item, folder
  FROM [Scratch].[dbo].[IMAGES_X] as i
  left join [Scratch].[dbo].[TM_20171030] as t
  on t.workspace_Path = i.gdb and t.Data_Source = i.item
  where t.workspace_Path is Null
  and gdb like '%IKONOS%'
  group by gdb, item, folder
  order by folder,gdb, item

-- Mosaic datasets on AIS (services)
SELECT gdb, item, folder
  FROM [Scratch].[dbo].[IMAGES_Z]
  where gdb like '%IKONOS%'
  group by gdb, item, folder
  order by folder,gdb, item

-- Image Folders in Mosaics on AIS (services)
SELECT gdb, item, folder
  FROM [Scratch].[dbo].[IMAGES_Z]
  where folder like '\\inpakrovmais\Data\%' and folder not like '%.Overviews'
  group by gdb, item, folder
  order by folder,gdb, item

-- Match mosaics on dist and ais
  SELECT X.gdb, X.Item, Z.gdb
  FROM (SELECT gdb, item
  FROM [Scratch].[dbo].[IMAGES_Z]
  group by gdb, item) AS Z
JOIN
  (SELECT gdb, item
  FROM [Scratch].[dbo].[IMAGES_X]
  group by gdb, item) AS X
  ON X.item = z.item
  order by X.item --, X.folder

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
  select * from mosaics_20171121 where contents = 'Mixed' or errors is not null

  SELECT folder FROM mosaic_images group by folder order by folder
  SELECT folder FROM mosaic_images where folder not like '%.Overviews%' group by folder order by folder

  select count(*) from mosaic_images

  SELECT fgdb from mosaics_20171121 group by fgdb order by fgdb

  --All mossics not moved to new Mosaics folder
  select m.fgdb, d.internal from (select fgdb from [mosaics_20171121] group by fgdb having fgdb like 'X:%') as m
  left join moves_dist as d on m.fgdb = 'X:\' + d.original
  where d.internal is null or d.internal not like 'Mosaics%'
  union
  select m.fgdb, d.internal from (select fgdb from [mosaics_20171121] group by fgdb having fgdb like 'Z:%') as m
  left join moves_ais as d on m.fgdb = 'Z:\' + d.original
  where d.internal is null or d.internal not like 'Mosaics%'

  -- SPOT5
  select * from mosaic_images where folder like '%SPOT5%' order by ext, folder -- All Paths
  select ext, count(*) from mosaic_images where folder like '%SPOT5%' group by ext -- All Paths
  select * from mosaic_images where folder like '%\SDMI\SPOT5\%' order by ext, folder  -- paths on dist (or X)
  select ext, count(*) from mosaic_images where folder like '%\SDMI\SPOT5\%' group by ext  -- paths on dist (or X)
  -- SPOT5 paths not on dist (or X)  -- just overviews and some wierd self reference X:\Albers\base\Imagery\SPOT5\SDMI.gdb\AMD_SPOT5_CIR1_CAT
  select * from mosaic_images where folder like '%SPOT5%' and folder not like '%\SDMI\SPOT5\%' order by ext, folder
  select * from mosaic_images where folder like '%SPOT5%' and folder not like '%\SDMI\SPOT5\%' and folder not like '%.Overviews%' order by ext, folder


  -- IFSAR
  select * from mosaic_images where folder like '%IFSAR%' order by ext, folder -- All Paths
  select ext, count(*) from mosaic_images where folder like '%IFSAR%' group by ext -- All Paths
  select * from mosaic_images where folder like '%\SDMI\IFSAR\%' order by ext, folder  -- paths on dist (or X)
  select ext, count(*) from mosaic_images where folder like '%\SDMI\IFSAR\%' group by ext  -- paths on dist (or X)
  -- IFSAR paths not on dist (or X)  -- just overviews others referencing the mosaic (on Z and on X)
  select * from mosaic_images where folder like '%IFSAR%' and folder not like '%\SDMI\IFSAR\%' order by ext, folder
  select * from mosaic_images where folder like '%IFSAR%' and folder not like '%\SDMI\IFSAR\%' and folder not like '%\Mosaics\%' and folder not like '%.Overviews%' order by ext, folder


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
order by (x.size - z.size)/(1.0 * x.size)

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
