# -*- coding: utf-8 -*-
"""
Writes a list of spot photos found in the file system
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from io import open
import os

with open(r"data\build_spot_orthometric.csv", "w", encoding="utf-8") as fh:
    for d, _, fs in os.walk(r"X:\Extras\AKR\Statewide\Imagery\SDMI_SPOT5"):
        for f in fs:
            fl = f.lower()
            # if fl.endswith('_rgb.tif'):
            # if fl.endswith('_cir.tif'):
            # if fl.endswith('_pan.tif'):
            # if fl.startswith('ellipsoidal.') and fl.endswith('.tif'):
            if fl.startswith("sdmi.dem.orthometric.") and fl.endswith(".tif"):
                fh.write(os.path.join(d, f) + "\n")
