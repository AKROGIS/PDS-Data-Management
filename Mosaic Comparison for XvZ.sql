
-- Mosaics in both dist and ais
select 'X:\' + d.original as dist_name, 'Z:\' + a.original as ais_name, 'X:\' + d.internal as new_name from moves_ais as a
join moves_dist as d on d.internal = a.internal
where d.internal like '%.gdb'

-- File and byte count for each fgdb
select fgdb, count(*) as files, sum(size) as bytes from  mosaic_images group by fgdb

-- File and byte count for each mosaic
select fgdb, mosaic, count(*) as files, sum(size) as bytes from  mosaic_images group by fgdb, mosaic


-- Check that mosaics in both ais and dist have same number of files and bytes (ignore overviews)
select new_name, c1.files as x_files, c2.files as z_files, c1.bytes as x_bytes, c2.bytes as z_bytes, dist_name as x_name, ais_name as z_name from
	(select 'X:\' + d.original as dist_name, 'Z:\' + a.original as ais_name, 'X:\' + d.internal as new_name from moves_ais as a
	join moves_dist as d on d.internal = a.internal
	where d.internal like '%.gdb') as dups
left join
	(select fgdb, count(*) as files, sum(size) as bytes from  mosaic_images where folder not like '%.Overviews' group by fgdb) as c1
	on dist_name = c1.fgdb
left join
	(select fgdb, count(*) as files, sum(size) as bytes from  mosaic_images where folder not like '%.Overviews' group by fgdb) as c2
	on ais_name = c2.fgdb
where c1.files <> c2.files or c1.bytes <> c2.bytes


-- Check that mosaics in both ais and dist have same number of files and bytes (ignore overviews)
-- check that extension is not null removes raster folders, which have a bogus size; note that this may miss real errors
select new_name, c1.files as x_files, c2.files as z_files, c1.bytes as x_bytes, c2.bytes as z_bytes, dist_name as x_name, ais_name as z_name from
	(select 'X:\' + d.original as dist_name, 'Z:\' + a.original as ais_name, 'X:\' + d.internal as new_name from moves_ais as a
	join moves_dist as d on d.internal = a.internal
	where d.internal like '%.gdb') as dups
left join
	(select fgdb, count(*) as files, sum(size) as bytes from  mosaic_images where folder not like '%.Overviews' and ext is not null group by fgdb) as c1
	on dist_name = c1.fgdb
left join
	(select fgdb, count(*) as files, sum(size) as bytes from  mosaic_images where folder not like '%.Overviews' and ext is not null group by fgdb) as c2
	on ais_name = c2.fgdb
where c1.files <> c2.files or c1.bytes <> c2.bytes



-- Compare X:\Mosaics\BELA\IKONOS.gdb
-- difference is in the single DEM file used for ortho rectification
-- Why is \\inpakrovmais\Data\NED\aknedm_rs30 slightly smaller (8192) than X:\DEM\NED_30mRS\aknedm_rs30 (16384)
-- The folder "size" is bogus.  The folder contents on X and Z are identical
select * from
	(select * from mosaic_images where fgdb = 'X:\IKONOS\BELA\IKONOS.gdb') as i1
left join
	(select * from mosaic_images where fgdb = 'Z:\IServer\Mosaics\BELA\IKONOS.gdb') as i2
on i1.filename = i2.filename and i1.size = i2.size
where i2.filename is null
and i1.folder not like '%.Overviews'
UNION
select * from
	(select * from mosaic_images where fgdb = 'Z:\IServer\Mosaics\BELA\IKONOS.gdb') as i1
left join
	(select * from mosaic_images where fgdb = 'X:\IKONOS\BELA\IKONOS.gdb') as i2
on i1.filename = i2.filename and i1.size = i2.size
where i2.filename is null
and i1.folder not like '%.Overviews'

-- Compare X:\Mosaics\CAKR\IKONOS.gdb
-- difference is in the single DEM file used for ortho rectification
-- Why is \\inpakrovmais\Data\NED\aknedm_rs30 slightly smaller (8192) than X:\DEM\NED_30mRS\aknedm_rs30 (16384)
-- The folder "size" is bogus.  The folder contents on X and Z are identical
select * from
	(select * from mosaic_images where fgdb = 'X:\IKONOS\CAKR\IKONOS.gdb') as i1
left join
	(select * from mosaic_images where fgdb = 'Z:\IServer\Mosaics\CAKR\IKONOS.gdb') as i2
on i1.filename = i2.filename and i1.size = i2.size
where i2.filename is null
and i1.folder not like '%.Overviews'
UNION
select * from
	(select * from mosaic_images where fgdb = 'Z:\IServer\Mosaics\CAKR\IKONOS.gdb') as i1
left join
	(select * from mosaic_images where fgdb = 'X:\IKONOS\CAKR\IKONOS.gdb') as i2
on i1.filename = i2.filename and i1.size = i2.size
where i2.filename is null
and i1.folder not like '%.Overviews'

-- Compare X:\Mosaics\KLGO\QuickBird.gdb
-- difference is in 6 images which have a folder but no name or extension; the folder "size" is different, but not the content
-- and a filename with a differnet size that is no longer part of the mosaic
-- deemed equivalent
select * from
	(select * from mosaic_images where fgdb = 'X:\Albers\UTM8\klgo\Imagery\QuickBird.gdb') as i1
left join
	(select * from mosaic_images where fgdb = 'Z:\IServer\Mosaics\KLGO\QuickBirdWARP.gdb') as i2
on i1.filename = i2.filename and i1.size = i2.size
where i2.filename is null
and i1.folder not like '%.Overviews'
UNION
select * from
	(select * from mosaic_images where fgdb = 'Z:\IServer\Mosaics\KLGO\QuickBirdWARP.gdb') as i1
left join
	(select * from mosaic_images where fgdb = 'X:\Albers\UTM8\klgo\Imagery\QuickBird.gdb') as i2
on i1.filename = i2.filename and i1.size = i2.size
where i2.filename is null
and i1.folder not like '%.Overviews'

-- Compare X:\Mosaics\Statewide\Imagery\Landsat8OLI_2013.gdb
-- One image is different size; however the image has a sourceid = -1 (no longer in the mosaic), so ignore
select * from
	(select * from mosaic_images where fgdb = 'X:\Albers\base\Imagery\Landsat8OLI\L8_2013.gdb') as i1
left join
	(select * from mosaic_images where fgdb = 'Z:\IServer\Mosaics\L8OLI\L8_2013.gdb') as i2
on i1.filename = i2.filename and i1.size = i2.size
where i2.filename is null
and i1.folder not like '%.Overviews'
UNION
select * from
	(select * from mosaic_images where fgdb = 'Z:\IServer\Mosaics\L8OLI\L8_2013.gdb') as i1
left join
	(select * from mosaic_images where fgdb = 'X:\Albers\base\Imagery\Landsat8OLI\L8_2013.gdb') as i2
on i1.filename = i2.filename and i1.size = i2.size
where i2.filename is null
and i1.folder not like '%.Overviews'


-- Compare X:\Mosaics\DENA\IKONOS.gdb
-- Z drive version has only geoeyeOrtho which references inpakrovmgis\data, so all files are zero size
-- New x drive version is based on old X drive version.
select * from
	(select * from mosaic_images where fgdb = 'X:\IKONOS\DENA\IKONOS.gdb') as i1
left join
	(select * from mosaic_images where fgdb = 'Z:\IServer\Mosaics\DENA\IKONOS.gdb') as i2
on i1.filename = i2.filename and i1.size = i2.size
where i2.filename is null
and i1.folder not like '%.Overviews'
UNION
select * from
	(select * from mosaic_images where fgdb = 'Z:\IServer\Mosaics\DENA\IKONOS.gdb') as i1
left join
	(select * from mosaic_images where fgdb = 'X:\IKONOS\DENA\IKONOS.gdb') as i2
on i1.filename = i2.filename and i1.size = i2.size
where i2.filename is null
and i1.folder not like '%.Overviews'


-- Compare X:\Mosaics\Statewide\Imagery\IFSAR_ORI.gdb
-- Z drive is a subset of the X drive.  No files in Z drive not in X drive
select * from
	(select * from mosaic_images where fgdb = 'X:\DEM\SDMI\IFSAR_ORI.gdb') as i1
left join
	(select * from mosaic_images where fgdb = 'Z:\IServer\Mosaics\AK\IFSAR_ORI.gdb') as i2
on i1.filename = i2.filename and i1.size = i2.size
where i2.filename is null
and i1.folder not like '%.Overviews'
UNION
select * from
	(select * from mosaic_images where fgdb = 'Z:\IServer\Mosaics\AK\IFSAR_ORI.gdb') as i1
left join
	(select * from mosaic_images where fgdb = 'X:\DEM\SDMI\IFSAR_ORI.gdb') as i2
on i1.filename = i2.filename and i1.size = i2.size
where i2.filename is null
and i1.folder not like '%.Overviews'

-- Compare X:\Mosaics\KATM\IKONOS_HRS.gdb
-- difference is in the single DEM file used for ortho rectification
-- Why is \\inpakrovmais\Data\DEM\HRS_KATM\KATM20m.tif slightly smaller (47226904) than X:\DEM\SPOT\KATM\KATM20m.tif (47268062)
select * from
	(select * from mosaic_images where fgdb = 'X:\IKONOS\KATM\IKONOS_HRS.gdb') as i1
left join
	(select * from mosaic_images where fgdb = 'Z:\IServer\Mosaics\KATM\IKONOS_HRS.gdb') as i2
on i1.filename = i2.filename and i1.size = i2.size
where i2.filename is null
and i1.folder not like '%.Overviews'
UNION
select * from
	(select * from mosaic_images where fgdb = 'Z:\IServer\Mosaics\KATM\IKONOS_HRS.gdb') as i1
left join
	(select * from mosaic_images where fgdb = 'X:\IKONOS\KATM\IKONOS_HRS.gdb') as i2
on i1.filename = i2.filename and i1.size = i2.size
where i2.filename is null
and i1.folder not like '%.Overviews'

-- Compare X:\Mosaics\Statewide\DEMs\IFSARDEM.gdb
-- Z drive is a subset of the X drive.  No files in Z drive not in X drive
select * from
	(select * from mosaic_images where fgdb = 'X:\DEM\SDMI\IFSARDEM.gdb') as i1
left join
	(select * from mosaic_images where fgdb = 'Z:\IServer\Mosaics\AK\IFSARDEM.gdb') as i2
on i1.filename = i2.filename and i1.size = i2.size
where i2.filename is null
and i1.folder not like '%.Overviews'
UNION
select * from
	(select * from mosaic_images where fgdb = 'Z:\IServer\Mosaics\AK\IFSARDEM.gdb') as i1
left join
	(select * from mosaic_images where fgdb = 'X:\DEM\SDMI\IFSARDEM.gdb') as i2
on i1.filename = i2.filename and i1.size = i2.size
where i2.filename is null
and i1.folder not like '%.Overviews'

-- Compare X:\Mosaics\Statewide\Imagery\SDMI_SPOT5.gdb
-- X drive version has two additional mosaics not on Z.  No files in Z drive mosaic not in X drive
select * from
	(select * from mosaic_images where fgdb = 'X:\Albers\base\Imagery\SPOT5\SDMI.gdb') as i1
left join
	(select * from mosaic_images where fgdb = 'Z:\IServer\Mosaics\AK\SDMI.gdb') as i2
on i1.filename = i2.filename and i1.size = i2.size
where i2.filename is null
and i1.folder not like '%.Overviews'
UNION
select * from
	(select * from mosaic_images where fgdb = 'Z:\IServer\Mosaics\AK\SDMI.gdb') as i1
left join
	(select * from mosaic_images where fgdb = 'X:\Albers\base\Imagery\SPOT5\SDMI.gdb') as i2
on i1.filename = i2.filename and i1.size = i2.size
where i2.filename is null
and i1.folder not like '%.Overviews'

-- Compare X:\Mosaics\KLGO\WorldView1.gdb
-- Very subtle differences in file names *7821010_03* => *5896010_01*
-- and some small diffs in file sizes for xml and jpg browse images only
select * from
	(select * from mosaic_images where fgdb = 'X:\Albers\UTM8\klgo\Imagery\WorldView1.gdb') as i1
left join
	(select * from mosaic_images where fgdb = 'Z:\IServer\Mosaics\KLGO\WorldView1.gdb') as i2
on i1.filename = i2.filename and i1.size = i2.size
where i2.filename is null
and i1.folder not like '%.Overviews'
UNION
select * from
	(select * from mosaic_images where fgdb = 'Z:\IServer\Mosaics\KLGO\WorldView1.gdb') as i1
left join
	(select * from mosaic_images where fgdb = 'X:\Albers\UTM8\klgo\Imagery\WorldView1.gdb') as i2
on i1.filename = i2.filename and i1.size = i2.size
where i2.filename is null
and i1.folder not like '%.Overviews'
