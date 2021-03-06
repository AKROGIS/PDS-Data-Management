# -*- coding: utf-8 -*-
"""
Checks the file used to fix the PDS
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import os

import csv23


old_x = r"\\INPAKROVMDIST\gisdata"
new_x = r"\\INPAKROVMDIST\gisdata2"
csv_path = r"data\PDS Fixes - X.csv"

unique_themes = set([])
with csv23.open(csv_path, "r") as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)  # ignore the header
    line = 1
    for row in csv_reader:
        row = csv23.fix(row)
        line += 1
        # check that time stamp is valid and increasing
        old_workspace = None if len(row[1].strip()) == 0 else row[1]
        old_datasource = None if len(row[3].strip()) == 0 else row[3]
        new_workspace = None if len(row[5].strip()) == 0 else row[5]
        if old_workspace is None:
            print("old workspace is missing from line {}".format(line))
        if new_workspace is None:
            print("new workspace is missing from line {}".format(line))
        if old_workspace is None or new_workspace is None:
            continue
        old_path = os.path.join(old_x, old_workspace)
        new_path = os.path.join(new_x, new_workspace)
        if old_datasource is not None:
            old_path = os.path.join(old_path, old_datasource)
            new_path = os.path.join(new_path, old_datasource)
        if not os.path.exists(old_path):
            print("line:{}, old path {} does not exist".format(line, old_path))
        if not os.path.exists(new_path):
            print("line:{}, new path {} does not exist".format(line, new_path))
        if not os.path.exists(old_path) or not os.path.exists(new_path):
            continue
        if old_datasource is not None:
            if not os.path.isfile(old_path):
                print("line:{}, old datasource {} is not a file".format(line, old_path))
            if not os.path.isfile(new_path):
                print("line:{}, new datasource {} is not a file".format(line, new_path))
        else:
            if old_workspace.lower().endswith(
                ".mdb"
            ) and new_workspace.lower().endswith(".mdb"):
                continue
            if not os.path.isdir(old_path):
                print(
                    "line:{}, old workspace {} is not a directory".format(
                        line, old_path
                    )
                )
            if not os.path.isdir(new_path):
                print(
                    "line:{}, new workspace {} is not a directory".format(
                        line, new_path
                    )
                )
