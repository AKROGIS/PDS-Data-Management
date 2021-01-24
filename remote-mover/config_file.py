# -*- coding: utf-8 -*-
"""
A collection of configuration properties.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Path to the moves database.
# Should be a Pipe (|)-delimited data file
# with the following header:
#   timestamp|old_workspace_path|old_workspace_type|old_dataset_name|old_dataset_type|
#   new_workspace_path|new_workspace_type|new_dataset_name|new_dataset_type|
#   replace_workspace_path|replace_workspace_type|replace_dataset_name|
#   replace_dataset_type|new_theme_manager_path|Notes
moves_db = r'X:\GIS\ThemeMgr\DataMoves.csv'

# Reference (last run) timestamp
ref_timestamp = None

# Remote server X drive path: UNC path or symbolic link to location where moves are to occur.
remote_server = None

# Time stamp and log file name.
name = None