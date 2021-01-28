# -*- coding: utf-8 -*-
"""
Remove all the files in the list of old stats files.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from io import open
import os
for line in open('old_style_stats.txt','r'):
   filename = os.path.join('X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR',line.strip())
   os.remove(filename)
