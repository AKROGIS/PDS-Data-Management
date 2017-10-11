"""
Compares Theme Manager against file system and reports on
1) Themes (layer files) in TM database that are not in the TM filesystem
2) Themes (layer files) in TM filesystem that are not in the TM database
"""
from __future__ import absolute_import, division, print_function, unicode_literals
from io import open  # for python2/3 compatibility
import csv
import os

tm_filesystem = r"X:\GIS\ThemeMgr"
tm_database = r"data\tm.csv"

unique_themes = set([])
with open(tm_database, 'rb') as f:
    for row in csv.reader(f):
        theme = row[4]
        unique_themes.add(theme)

print("Missing Themes:")
for theme in unique_themes:
    if theme and not os.path.exists(theme):
        print('  ' + theme)

print("Extra Themes:")
for root, dirs, files in os.walk(tm_filesystem):
    for name in files:
        base, ext = os.path.splitext(name)
        if ext.lower() != '.xml':
            filepath = os.path.join(root, name)
            if filepath not in unique_themes:
                print('  ' + filepath)
