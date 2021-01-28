# -*- coding: utf-8 -*-
"""
Remove all the files in the list of old stats files.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from io import open
import os

root_dir = r"X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR"
for line in open("old_style_stats.txt", "r", encoding="utf-8"):
    filename = line.strip()
    filepath = os.path.join(root_dir, filename)
    os.remove(filepath)
