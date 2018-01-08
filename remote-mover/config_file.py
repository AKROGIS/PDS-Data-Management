"""
A collection of configuration properties.
"""

"""
Pipe (|)-delimited moves data file
Format: timestamp|old_workspace_path|old_workspace_type|old_dataset_name|old_dataset_type|new_workspace_path|new_workspace_type|new_dataset_name|new_dataset_type|replace_workspace_path|replace_workspace_type|replace_dataset_name|replace_dataset_type|new_theme_manager_path|Notes
"""
moves_db = 'X:\GIS\ThemeMgr\DataMoves.csv'

"""
Location of reference (last run) timestamp file
"""
ref_timestamp = None

"""
Remote server X drive path: UNC path or symbolic link to location where moves are to occur
"""
remote_server = None

"""
Time stamp and log file name
"""
name = None