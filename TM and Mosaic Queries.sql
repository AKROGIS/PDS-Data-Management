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
