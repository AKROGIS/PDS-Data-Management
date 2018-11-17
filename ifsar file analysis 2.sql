-- Counts by kind
select kind, count(*) from ifsar_tif_new_x_supp2 where skip = 'N' group by kind
select kind, count(*) from [reorg].[dbo].[ifsar_tif_new_x_supp2] where cell is not null and lat > 0 and nga = 'N'
and legacy = 'N' and edge = 'N' group by kind order by count(*)

-- dtm files with no cell # (explains difference in two counts above)
select folder, kind, cell, lat  from [reorg].[dbo].[ifsar_tif_new_x_supp2] where kind = 'dtm' and cell is null order by kind, cell, lat

-- dtm tiles in a cell (should always be 16)
select cell, count(*) as cnt from  [reorg].[dbo].[ifsar_tif_new_x_supp2] where kind = 'dtm' and skip = 'N' group by cell having count(*) <> 16 order by cell

-- dups:
-- expect 26 dtm, dsm, ori in GLBA (lat in (58..59.3) and lon in (135.15 .. 136.45, 138.15 .. 138.45)
select kind, edge, lat, lon, count(*) from  [reorg].[dbo].[ifsar_tif_new_x_supp2] where skip = 'N' and kind = 'dtm' group by kind, edge, lat, lon having count(*) > 1 order by count(*), kind, lon
select kind, edge, lat, lon, count(*) from  [reorg].[dbo].[ifsar_tif_new_x_supp2] where skip = 'N' and kind = 'dtm' group by kind, edge, lat, lon having count(*) > 1 order by count(*), kind
-- 
select * from [reorg].[dbo].[ifsar_tif_new_x_supp2] where lat >= 58 and lat <= 59.3 and lon >= 135.15 and lon <= 138.45
select cell, count(*) from [reorg].[dbo].[ifsar_tif_new_x_supp2] where lat >= 58 and lat <= 59.3 and lon >= 135.15 and lon <= 138.45 group by cell


-- remove old aux files to delete: 3283 (1425 dtm, 1426 dsm, 388 ori, 44 ori_sup)
--select kind, count(*) from ifsar_tif_new_x_supp2 where aux_old = 1 and skip = 'N' group by kind
-- skip unused NGA, edge etc (315)
select folder + '\' + filename + '.aux' from ifsar_tif_new_x_supp2 where aux_old = 1 and skip = 'N' --and kind = 'ori_sup'
-- folders with aux files (FEDI_Data, Intermap_Data, and EdgeMatched)
select left(folder, len(folder)-24), count(*) as cnt from ifsar_tif_new_x_supp2 where aux_old = 1 and skip = 'N' group by left(folder, len(folder)-24)
select left(folder, len(folder)-10), count(*) as cnt from ifsar_tif_new_x_supp2 where aux_old = 1 and skip = 'N' group by left(folder, len(folder)-10)

-- add new style stats file: 8474 (1974 dtm, 1969 dsm, 3106 ori, 1425 ori_sup)
--select kind, count(*) from ifsar_tif_new_x_supp2 where aux = 0 and skip = 'N' group by kind
-- skip unused NGA, legacy, edge, etc (1650)
select folder + '\' + filename + '.tif' from ifsar_tif_new_x_supp2 where aux = 0 and skip = 'N' -- and kind = 'dtm'

-- Save space on skipped files? 269 old stats files, 8 old pyramids, and 0 new pyramids 
select count(*) from ifsar_tif_new_x_supp2 where aux_old = 1 and skip = 'Y'
select count(*) from ifsar_tif_new_x_supp2 where rrd = 1 and skip = 'Y'
select count(*) from ifsar_tif_new_x_supp2 where ovr = 1 and skip = 'Y'
select folder from ifsar_tif_new_x_supp2 where skip = 'Y' and rrd = 1
select folder from ifsar_tif_new_x_supp2 where skip = 'Y' and (aux_old = 1 or rrd = 1 or ovr = 1)

select folder from ifsar_tif_new_x_supp2 where folder like '%Diagram%'

select folder from ifsar_tif_new_x_supp2 where filename = 'ak_90m_16bit_ellip_gf9_nonul'

-- Can we delete any of the used folders?
select distinct folder from ifsar_tif_new_x_supp2 where skip <> 'N' -- 476
select distinct folder from ifsar_tif_new_x_supp2 where skip = 'E' -- 65 replaced by edge matched
select distinct folder from ifsar_tif_new_x_supp2 where skip = 'Y' and nga = 'Y'  -- 363 NGA
select distinct folder from ifsar_tif_new_x_supp2 where skip = 'Y' and legacy = 'Y'  -- 40 Legacy
select distinct folder from ifsar_tif_new_x_supp2 where skip = 'Y' and nga = 'N' and legacy = 'N' -- 8 diagram DEMs

select * from ifsar_tif_new_x_supp2 where folder like 'X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR\GINA_CIAP%' and (legacy = 'N' or skip <> 'Y')