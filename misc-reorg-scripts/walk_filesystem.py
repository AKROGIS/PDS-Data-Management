# -*- coding: utf-8 -*-
"""
walk file system
*.mxd - list data frames, and all layers recursively (flag any missing data sources)
*.lyr - list all layers recursively  (flag any missing data sources)
*.gdb
*.mdb - list all datasets
*.shp - list
*.gdb/mosaic - list all photo workspaces  (flag any missing data sources)

use arcpy
 ListDatasets, ListFeatureClasses, ListFiles, ListRasters, ListTables, and ListWorkspaces
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os.path

import walk_workspaces

# pylint: disable=missing-function-docstring


class Config(object):
    """Namespace for configuration parameters. Edit as needed."""

    # pylint: disable=useless-object-inheritance,too-few-public-methods

    # Start folder - Where in the file system to start recursively looking
    # for workspaces.
    start_folder = r"C:\tmp"


def is_access_file(name):
    return os.path.splitext(name)[1].lower() in [".mdb", ".accdb"]


def is_pgdb(name):
    return os.path.splitext(name)[1].lower() in [".mdb"]


def is_fgdb(name):
    return os.path.splitext(name)[1].lower() in [".gdb"]


def walk_fs(root):
    """Find all the personal geodatabases below root"""
    for path, folders, file_names in os.walk(root):
        for folder in folders:
            if is_fgdb(folder):
                folders.remove(folder)
                fgdb = os.path.join(path, folder)
                print(fgdb)
                walk_workspaces.inspect_workspace(0, fgdb, False)
        for file_name in file_names:
            if is_pgdb(file_name):
                fgdb = os.path.join(path, file_name)
                print(fgdb)
                walk_workspaces.inspect_workspace(0, fgdb, False)


if __name__ == "__main__":
    walk_fs(Config.start_folder)
