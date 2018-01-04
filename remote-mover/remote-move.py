from __future__ import absolute_import, division, print_function, unicode_literals
import time
import os
import csv
import logging

"""

	Read server reference timestamp
Read csv, | delimeter
X:\GIS\ThemeMgr\DataMoves.csv
For each row in csv
"""

# ????!?!?!?!! old_workspace_path = r'c:\users\phoeffler\desktop\akr\one\kid'
old_workspace_path = r'c:/users/phoeffler/desktop/akr/one/kid'
new_workspace_path = r"c:/users/phoeffler/desktop/akr/three/four/kid"

new_workspace_path_parent = os.path.abspath(os.path.join(new_workspace_path, os.pardir))

if timestamp > reference_timestamp and \
   old_workspace_path <> new_workspace_path and \
   new_workspace_path is not null and \
   old_workspace_path is not null and \
   os.path.exists(old_workspace_path) and \
   not os.path.exists(new_workspace_path) and \
   new_workspace_type is null and \
   old_workspace_type is null and \
   old_dataset_name is null:
    try:
        # if parent folder does not exist create necessary folder structure through parent folder
        if not os.path.exists(new_workspace_path_parent):
            os.makedirs(new_workspace_path_parent)

        # move: rename folder
        os.rename(old_workspace_path,new_workspace_path)
    except:
        pass
        # log exception
    
    # log successful move

"""
If no errors logged:
    Update server reference timepstamp

Aggregator: logging, config file and arguments
"""
