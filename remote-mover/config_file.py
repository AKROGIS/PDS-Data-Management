# -*- coding: utf-8 -*-
"""
A collection of configuration properties.

WARNING: This file, while intended to be edited by the user, is part of the
source code of this application.  If edited incorrectly the application may
crash or misbehave in unexpected ways.

ALWAYS TEST AFTER MAKING CHANGES TO THIS FILE.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Path to the moves database.
# Should be a Pipe (|)-delimited data file
# with the following header:
#   timestamp|old_workspace_path|old_workspace_type|old_dataset_name|old_dataset_type|
#   new_workspace_path|new_workspace_type|new_dataset_name|new_dataset_type|
#   replace_workspace_path|replace_workspace_type|replace_dataset_name|
#   replace_dataset_type|new_theme_manager_path|Notes
MOVES_DB = r"X:\GIS\ThemeMgr\DataMoves.csv"

# Reference (last run) timestamp
REF_TIMESTAMP = None

# Remote server X drive path: UNC path or symbolic link to location where moves are to occur.
REMOTE_SERVER = None

# Time stamp and log file name.
NAME = None
