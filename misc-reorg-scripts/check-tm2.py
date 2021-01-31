# -*- coding: utf-8 -*-
"""
Checks the Theme Manager database and reports on
1) All the workspaces (folder, fgdb, mdb, etc) that are in the database
2) Any workspaces that are in the database, but not in the filesystem
3) Any features in the database, that are not found in the workspace
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import os

import arcpy

import csv23


csv_path = r"data\tm.csv"

data = {}
with csv23.open(csv_path, "r") as csv_file:
    csv_reader = csv.reader(csv_file)
    # next(csv_reader) # ignore the header
    for row in csv_reader:
        row = csv23.fix(row)
        theme = row[1] + "/" + row[2]
        workspace = row[9]
        feature = row[10] if row[10] and row[10].lower().endswith(".dwg") else row[12]
        if workspace not in data:
            data[workspace] = (set([]), [])
        data[workspace][0].add(theme)
        data[workspace][1].append((feature, theme))


print("Workspace in Theme Manager:")
found = []
for workspace in data:
    if workspace and os.path.exists(workspace):
        found.append(workspace)
for workspace in sorted(found):
    print("  " + workspace)


print("\nMissing Workspace:")
for workspace in sorted(data.keys()):
    if workspace and not os.path.exists(workspace):
        print("  " + workspace)
        for theme in data[workspace][0]:
            print("    " + theme)


print("\nMissing Feature in found Workspace:")
for workspace in data:
    if workspace and os.path.exists(workspace):
        for feature, theme in data[workspace][1]:
            path = os.path.join(workspace, feature)
            if not arcpy.Exists(path):
                print("  " + path)
                print("    " + theme)
