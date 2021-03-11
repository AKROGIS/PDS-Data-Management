# -*- coding: utf-8 -*-
"""
Find Microsoft Access databases, and try to describe as a Personal Geodatabase

Pro can find the Access database, but it cannot list the contents.

uses arcpy
 ListDatasets, ListFeatureClasses, ListFiles, ListRasters, ListTables, and ListWorkspaces
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os.path

import walk_workspaces


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


def find_pgdb(root):
    """Find all the personal geodatabases below root"""
    for folder, _, file_names in os.walk(root):
        for file_name in file_names:
            if is_access_file(file_name):
                path = os.path.join(folder, file_name)
                print(path)
                if is_pgdb(file_name):
                    walk_workspaces.inspect_workspace(0, path, False)


if __name__ == "__main__":
    find_pgdb(Config.start_folder)
