-- Theme (typically layer file) paths not in the theme manager folder
SELECT Data_Path, count(*) FROM [reorg].[dbo].[THEMEMANAGER_20171207] where data_path not like 'X:\GIS\ThemeMgr\%' 
and data_path not like 'X:\ESRI_Data\%' group by data_path order by data_path

-- bad/unknown workspace paths 
SELECT Workspace_Path, count(*) FROM [reorg].[dbo].[THEMEMANAGER_20171207]
where Workspace_Path not like 'X:\AKR\%' and Workspace_Path not like 'X:\Extras\%' 
 and Workspace_Path not like 'X:\%_Data\%' and Workspace_Path not like 'X:\Mosaics\%' 
 and Workspace_Path not like 'X:\GIS\%'  and Workspace_Path not like 'X:\Trash\%' 
group by Workspace_Path order by Workspace_Path

-- check the datasource path starts with workspacepath
select * from [THEMEMANAGER_20171207] where data_source_path not like workspace_path + '%'

-- Themes with bad workspace path
select * from [reorg].[dbo].[THEMEMANAGER_20171207] AS tm
where Workspace_Path in (SELECT Workspace_Path FROM [reorg].[dbo].[THEMEMANAGER_20171207]
where Workspace_Path not like 'X:\AKR\%' and Workspace_Path not like 'X:\Extras\%' 
 and Workspace_Path not like 'X:\%_Data\%' and Workspace_Path not like 'X:\Mosaics\%' 
 and Workspace_Path not like 'X:\GIS\%'  and Workspace_Path not like 'X:\Trash\%' 
group by Workspace_Path) order by category, theme
