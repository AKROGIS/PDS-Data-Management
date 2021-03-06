-- Specify tiles to skip (do not belong in mosaic)
-- ================================================
--   This is now done in the python processing.
--   alter table ifsar_tif_all add skip char not null default 'N'

-- skip legacy, nga, and unknown kinds
select * from ifsar_tif_all where skip <> 'Y' and (kind is null or legacy = 'Y' or nga = 'Y')
--   update ifsar_tif_all set skip = 'Y' where skip <> 'Y' and (kind is null or legacy = 'Y' or nga = 'Y')

-- skip dups for disk4
select * from ifsar_tif_all where skip <> 'D' and folder like '%disk4%'
--   update ifsar_tif_all set skip = 'D' where skip <> 'D' and folder like '%disk4%'

-- skip dups for summer_2016_lot1
select * from ifsar_tif_all where skip <> 'O' and folder like '%5dec2017\summer_2016_lot1%'
--   update ifsar_tif_all set skip = 'O' where skip <> 'O' and folder like '%5dec2017\summer_2016_lot1%'

-- skip dups for cell 150
select * from ifsar_tif_all where skip <> 'O' and cell = 150 and folder like '%Summer_2016_Lot4_Cell_150%'
--   update ifsar_tif_all set skip = 'O' where skip <> 'O' and cell = 150 and folder like '%Summer_2016_Lot4_Cell_150%'

-- skip edges
   select en.*, ey.* from (select * from ifsar_tif_all where edge = 'Y') as ey
   join (select * from ifsar_tif_all where skip <> 'E' and edge = 'N') as en
   on ey.lat = en.lat and ey.lon = en.lon and ey.kind = en.kind
/*
   update en set skip = 'E' from (select * from ifsar_tif_all where edge = 'Y') as ey
   join (select * from ifsar_tif_all where skip <> 'E' and edge = 'N') as en
   on ey.lat = en.lat and ey.lon = en.lon and ey.kind = en.kind
*/

-- Special Adjustments for X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR\2019_IFSAR\Summer_2017_Lot10to22
-- 1) cell is not populated for some edge matched tiles
select * FROM ifsar_tif_2019c where cell is null and folder like '%248_2%'
update ifsar_tif_2019c set cell = 248 where cell is null and folder like '%248_2%'
-- three versions of tile 248:61:153.15 1) no edge match, 2) edge match on only east edge, 3) edge match on only south edge
-- the no edge match was skipped with normal processing. We have to manually skip the only south edge (shorter) to avoid overlapping tiles
select * FROM ifsar_tif_2019c where edge = 'Y' and cell = 248 and lat = 61 and lon = 153.15 and folder like '%248_2%'
update ifsar_tif_2019c set skip = 'E' where edge = 'Y' and cell = 248 and lat = 61 and lon = 153.15 and folder like '%248_2%'
-- Add new data to the base table

-- Add to the 
INSERT INTO ifsar_tif_all SELECT * FROM ifsar_tif_2019c


-- Check list of tiles skipped and not skipped
select skip, kind, count(*) from ifsar_tif_all where skip <> 'N' group by skip, kind order by skip, kind
select * from ifsar_tif_all where skip <> 'N' order by skip, kind, legacy, nga
select kind, count(*) from ifsar_tif_all where skip = 'N' group by kind

-- list of type count(*)
select kind, count(*) from ifsar_tif_all group by kind order by count(*) 
select kind, count(*) from ifsar_tif_all where cell is not null and lat > 0 group by kind order by count(*)
select kind, count(*) from ifsar_tif_all where cell is not null and lat > 0 and nga = 'N' and legacy = 'N' and edge = 'N' group by kind order by count(*)

-- list of images with a non-standard name; legacy ori, and 90m dem for report
--   1312 Legacy ORI (all) and 8 resampled NED (all)
select * from ifsar_tif_all where lat = 0 order by folder, filename

-- list of images with a non-standard kind
--    347 = dems for NGA 30 cells (339), and resampled ned (8) for diagrams
select * from ifsar_tif_all where kind is null order by kind, size, folder, filename

-- list legacy tiles
--   1312 ori; dsm/dtm are *.bil)
--   Why are so many ORI imgages the exact same size; because they are uncompressed and they have the same number of rows/columns
select * from ifsar_tif_all where legacy = 'Y' order by kind, size, folder, filename

-- list nga tiles (24 dtm and 339 dem (kind = null))
select * from ifsar_tif_all where nga = 'Y' order by kind, size, folder, filename

-- list of edge matched tiles (65 dsm and 65 dtm)
select * from ifsar_tif_all where edge = 'Y' order by kind, lat, lon

-- Tiles that are replaced by edge matched tiles
select en.filename, en.folder, ey.filename, ey.folder from (select * from ifsar_tif_all where edge = 'Y') as ey
left join (select * from ifsar_tif_all where edge = 'N') as en
on ey.lat = en.lat and ey.lon = en.lon and ey.kind = en.kind

-- list of cells
select distinct cell from  ifsar_tif_all where cell > 0 and legacy = 'N' and nga = 'N' and edge = 'N' order by cell

-- list of all useful images
select * from ifsar_tif_all where lat <> 0 and kind is not null and legacy = 'N' and nga = 'N' and edge = 'N' order by cell, lat, lon, folder, filename

-- tiles with old cell number; mapping old to new is pretty random; should use a mapping table to fix
select * from ifsar_tif_all where cell < 39 and cell > 0  and lat < 69.5 order by cell

-- list of tiles (by lat/lon) that do not have 3 tiles 
select cell, lat, lon, count(*) from ifsar_tif_all where lat > 0 and edge = 'N' and legacy = 'N' and nga = 'N' and kind is not null group by cell, lat, lon order by count(*), cell, lat, lon
select cell, lat, lon, count(*) from ifsar_tif_all where lat > 0 and edge = 'N' and legacy = 'N' and nga = 'N'  and kind is not null and kind <> 'ori_sup' group by cell, lat, lon having count(*) <> 3 order by count(*), cell, lat, lon

-- overlapping tiles
select kind, edge, lat, lon, count(*) from  ifsar_tif_all group by kind, edge, lat, lon having count(*) > 1 order by count(*) desc, kind
select kind, edge, min(cell)as cell, lat, lon, count(*) as num from  ifsar_tif_all where lat > 0 and kind <> 'ori_sup' group by kind, edge, lat, lon having count(*) > 1 order by count(*) desc, kind, max(cell)

-- GLBA tile are not duplicates.  overlapping tiles are split, and each pair has no-data in the matches data area
--- files in FEDI_Data\Glacier_Bay but not 2014_IFSAR\Upper_SE_Glacier_Bay
select g1.* from (select * from ifsar_tif_all where folder like '%FEDI_Data\Glacier_Bay%') as g1
  left join (select * from ifsar_tif_all where folder like '%2014_IFSAR\Upper_SE_Glacier_Bay%') as g2
  on g1.cell = g2.cell and g1.lat = g2.lat and g1.lon = g2.lon and g1.kind = g2.kind
  where g2.folder is null and g1.kind = 'dtm' order by cell, lat, lon, kind
--- files in FEDI_Data\Glacier_Bay but not 2014_IFSAR\Upper_SE_Glacier_Bay
select g1.* from (select * from ifsar_tif_all where folder like '%2014_IFSAR\Upper_SE_Glacier_Bay%') as g1
  left join (select * from ifsar_tif_all where folder like '%FEDI_Data\Glacier_Bay%') as g2
  on g1.cell = g2.cell and g1.lat = g2.lat and g1.lon = g2.lon and g1.kind = g2.kind
  where g2.folder is null and g1.kind = 'dtm' order by cell, lat, lon, kind
--- files in both FEDI_Data\Glacier_Bay and 2014_IFSAR\Upper_SE_Glacier_Bay
select g1.cell, g1.filename, g1.folder, g2.folder from (select * from ifsar_tif_all where folder like '%FEDI_Data\Glacier_Bay%') as g1
  left join (select * from ifsar_tif_all where folder like '%2014_IFSAR\Upper_SE_Glacier_Bay%') as g2
  on g1.cell = g2.cell and g1.lat = g2.lat and g1.lon = g2.lon and g1.kind = g2.kind
  where g2.folder is not null and g1.kind = 'dtm' order by g1.cell, g1.lat, g1.lon, g1.kind

-- DTM without DSM
--  Just a few NGA 30 tiles (24), and the edge matched tiles (65) are organized differently 
select * from (select * from [ifsar_tif_all] where kind = 'dtm') as f1
left join (select * from [ifsar_tif_all] where kind = 'dsm') as f2 on
f1.folder = f2.folder
where f2.folder is null and f1.edge = 'N' and f1.NGA = 'N'

-- DTM without ORI
--  Just a few NGA 30 tiles (24), and no edge matching (65) on the ORIs
select * from (select * from [ifsar_tif_all] where kind = 'dtm') as f1
left join (select * from [ifsar_tif_all] where kind = 'ori') as f2 on
f1.folder = f2.folder
where f2.folder is null and f1.edge = 'N' and f1.NGA = 'N'

-- DSM without DTM
--   Just edge matched tiles (65), which are organized differently
select * from (select * from [ifsar_tif_all] where kind = 'dsm') as f1
left join (select * from [ifsar_tif_all] where kind = 'dtm') as f2 on
f1.folder = f2.folder
where f2.folder is null and f1.edge = 'N'

-- DSM without ORI
--   no edge matching (65) on the ORIs
select * from (select * from [ifsar_tif_all] where kind = 'dsm') as f1
left join (select * from [ifsar_tif_all] where kind = 'ori') as f2 on
f1.folder = f2.folder
where f2.folder is null and f1.edge = 'N'

-- ORI without DTM
--  1312 Legacy tiles have ORI as *.tif, but not DTM/DSM as *.bil files
select * from (select * from [ifsar_tif_all] where kind = 'ori') as f1
left join (select * from [ifsar_tif_all] where kind = 'dtm') as f2 on
f1.folder = f2.folder
where f2.folder is null and f1.legacy = 'N'

-- Dups - should only be the half/half tiles in GLBA (6@319, 4@321, 4@322, 3@338, 9@339)
select cell, lat, lon, count(*) from ifsar_tif_all where skip = 'N' and kind <> 'ori_sup' group by cell, lat, lon having count(*) <> 3 order by count(*), cell, lat, lon

--  Summary of side car files
select kind, count(*) as total, sum(tfw) as tfw, sum(xml) as xml, sum(html) as html, sum(txt) as txt, 
       sum(tif_xml) as tif_xml, sum(ovr) as ovr, sum(aux) as aux, sum(rrd) as rrd, sum(aux_old) as aux_old, sum(crc) as crc  
from ifsar_tif_all where skip = 'N' group by kind order by kind


-- remove old aux files to delete: 3283 (1425 dtm, 1426 dsm, 388 ori, 44 ori_sup)
---------------------------------
select folder + '\' + filename + '.aux' from ifsar_tif_all where aux_old = 1 and skip = 'N'
-- which kinds of files have aux files?
select kind, count(*) from ifsar_tif_all where aux_old = 1 and skip = 'N' group by kind
-- Which skipped files have aux (315)
select folder + '\' + filename + '.aux' from ifsar_tif_all where aux_old = 1 and skip <> 'N'
-- list folders with aux files (FEDI_Data, Intermap_Data, and EdgeMatched)
select left(folder, len(folder)-24), count(*) as cnt from ifsar_tif_all where aux_old = 1 and skip = 'N' group by left(folder, len(folder)-24)


-- dtm for mosaic without stats (434)
select filename, folder from ifsar_tif_all where skip = 'N' and aux = 0 and aux_old = 0 and kind = 'dtm'

-- verify ovr/rrd and aux/aux_old are exclusive
--   48 FEDI ORI and 1 intermap DSM have old style and new style stats.
select * from ifsar_tif_all where (ovr = 1 and rrd = 1) or (aux = 1 and aux_old = 1)


select folder + '\' + filename + ext as path from ifsar_tif_all where kind = 'dtm' and skip = 'N' and aux_old = 0 and aux = 1 order by cell, lat, lon

select folder + '\' + filename + ext as path from ifsar_tif_all where skip <> 'N' and aux_old = 1 order by cell, lat, lon

select * from ifsar_tif_all where rrd = 1 and tif_xml = 1

select folder + '\' + filename + ext as path from ifsar_tif_all where skip = 'O'

-- List of Summer_2016_Lot1 to be replaced
select old.folder + '\' + old.filename + old.ext as old_path , new.folder + '\' + new.filename + new.ext as new_path
from (select * from ifsar_tif_all where kind in ('DSM','DTM') and folder like '%Summer_2016_Lot1%' and skip = 'O') as old
join (select * from ifsar_tif_all where kind in ('DSM','DTM') and folder like '%Summer_2016_Lot1%' and skip = 'N') as new
on old.kind = new.kind and old.lat = new.lat and old.lon = new.lon

select * from ifsar_tif_all where cell = 319



-- EXPORT Lists
-- ============

--   3649 each dtm/dsm/ori before 2019
--   288 each dtm/dsm/ori in 2019 part1; 24 each in 2019 part 2; 200 each in 2019 part 3
select folder + '\' + filename + ext as path from ifsar_tif_all where kind = 'dtm' and skip = 'N' order by cell, lat, lon
select folder + '\' + filename + ext as path from ifsar_tif_all where kind = 'dsm' and skip = 'N' order by cell, lat, lon
select folder + '\' + filename + ext as path from ifsar_tif_all where kind = 'ori' and skip = 'N' order by cell, lat, lon
select folder + '\' + filename + ext as path from ifsar_tif_all where kind = 'ori_sup' and skip = 'N' and filename like '%_sup1' order by cell, lat, lon
select folder + '\' + filename + ext as path from ifsar_tif_all where kind = 'ori_sup' and skip = 'N' and filename like '%_sup2'  order by cell, lat, lon
select folder + '\' + filename + ext as path from ifsar_tif_all where kind = 'ori_sup' and skip = 'N' and filename like '%_sup3'  order by cell, lat, lon
