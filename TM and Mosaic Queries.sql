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
