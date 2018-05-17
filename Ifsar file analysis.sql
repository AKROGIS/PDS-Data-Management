/****** Script for SelectTopNRows command from SSMS  ******/
SELECT TOP (1000) [folder]
      ,[filename]
      ,[ext]
      ,[size]
      ,[kind]
      ,[edge]
      ,[cell]
      ,[lat]
      ,[lon]
  FROM [reorg].[dbo].[ifsar_tif_new_x_supp2]

-- list of type count(*)
select kind, count(*) from [reorg].[dbo].[ifsar_tif_new_x_supp2] group by kind order by count(*)

-- list of images with a non-standard name; legacy ori, and 90m dem for report
select * from [reorg].[dbo].[ifsar_tif_new_x_supp2] where lat = 0 order by folder, filename

-- list of images with a non-standard kind; dems for NGA 30 cells
select * from [reorg].[dbo].[ifsar_tif_new_x_supp2] where kind is null order by kind, size, folder, filename

-- list legacy tiles
--   Why are so many ORI imgages the exact same size; because they are uncompressed and they have the same number of rows/columns
select * from [reorg].[dbo].[ifsar_tif_new_x_supp2] where legacy = 'Y' order by kind, size, folder, filename

-- list nga tiles
select * from [reorg].[dbo].[ifsar_tif_new_x_supp2] where nga = 'Y' order by kind, size, folder, filename

-- list of edge matched tiles
select * from [reorg].[dbo].[ifsar_tif_new_x_supp2] where edge = 'Y' order by cell, kind, lat, lon

-- list of cells
select distinct cell from  [reorg].[dbo].[ifsar_tif_new_x_supp2] where cell > 0 and legacy = 'N' and nga = 'N' and edge = 'N' order by cell

-- list of all useful images
select * from [reorg].[dbo].[ifsar_tif_new_x_supp2] where lat <> 0 and kind is not null and legacy = 'N' and nga = 'N' and edge = 'N' order by cell, lat, lon, folder, filename

-- tiles with old cell number; mapping old to new is pretty random; should use a mapping table to fix
select * from ifsar_tif_new_x_supp2 where cell < 39 and cell > 0  and lat < 69.5 order by cell

-- list of tiles (by lat/lon) that do not have 3 tiles 
select cell, lat, lon, count(*) from [reorg].[dbo].[ifsar_tif_new_x_supp2] where lat > 0 and edge = 'N' and legacy = 'N' and nga = 'N' and kind is not null group by cell, lat, lon order by count(*), cell, lat, lon
select cell, lat, lon, count(*) from [reorg].[dbo].[ifsar_tif_new_x_supp2] where lat > 0 and edge = 'N' and legacy = 'N' and nga = 'N'  and kind is not null and kind <> 'ori_sup' group by cell, lat, lon having count(*) <> 3 order by count(*), cell, lat, lon

-- overlapping tiles
select kind, edge, lat, lon, count(*) from  [reorg].[dbo].[ifsar_tif_new_x_supp2] group by kind, edge, lat, lon having count(*) > 1 order by count(*) desc, kind
select kind, edge, min(cell)as cell, lat, lon, count(*) as num from  [reorg].[dbo].[ifsar_tif_new_x_supp2] where lat > 0 and kind <> 'ori_sup' group by kind, edge, lat, lon having count(*) > 1 order by count(*) desc, kind, max(cell)


-- GLBA tile are not duplicates.  overlapping tiles are split, and each pair has no-data in the matches data area
--- files in FEDI_Data\Glacier_Bay but not 2014_IFSAR\Upper_SE_Glacier_Bay
select g1.* from (select * from ifsar_tif_new_x_supp2 where folder like '%FEDI_Data\Glacier_Bay%') as g1
  left join (select * from ifsar_tif_new_x_supp2 where folder like '%2014_IFSAR\Upper_SE_Glacier_Bay%') as g2
  on g1.cell = g2.cell and g1.lat = g2.lat and g1.lon = g2.lon and g1.kind = g2.kind
  where g2.folder is null and g1.kind = 'dtm' order by cell, lat, lon, kind
--- files in FEDI_Data\Glacier_Bay but not 2014_IFSAR\Upper_SE_Glacier_Bay
select g1.* from (select * from ifsar_tif_new_x_supp2 where folder like '%2014_IFSAR\Upper_SE_Glacier_Bay%') as g1
  left join (select * from ifsar_tif_new_x_supp2 where folder like '%FEDI_Data\Glacier_Bay%') as g2
  on g1.cell = g2.cell and g1.lat = g2.lat and g1.lon = g2.lon and g1.kind = g2.kind
  where g2.folder is null and g1.kind = 'dtm' order by cell, lat, lon, kind
--- files in both FEDI_Data\Glacier_Bay and 2014_IFSAR\Upper_SE_Glacier_Bay
select * from (select * from ifsar_tif_new_x_supp2 where folder like '%FEDI_Data\Glacier_Bay%') as g1
  left join (select * from ifsar_tif_new_x_supp2 where folder like '%2014_IFSAR\Upper_SE_Glacier_Bay%') as g2
  on g1.cell = g2.cell and g1.lat = g2.lat and g1.lon = g2.lon and g1.kind = g2.kind
  where g2.folder is not null and g1.kind = 'dtm' order by g1.cell, g1.lat, g1.lon, g1.kind
   
