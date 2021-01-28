# -*- coding: utf-8 -*-
"""
Print out the full path when longer than a given number of characters.

Useful for finding paths that will exceed 256 characters
if a folder is moved deeper into the file system
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os


def long_paths(start=".", max_length=200):
    for root, folders, files in os.walk(start):
        for name in files:
            path = os.path.join(root, name)
            path_length = len(path)
            if max_length < path_length:
                print(path_length, path)
        skip_folders = []
        for name in folders:
            path = os.path.join(root, name)
            path_length = len(path)
            if max_length < path_length:
                print(path_length, path, "all files below")
                skip_folders.append(name)
        for name in skip_folders:
            folders.remove(name)


if __name__ == "__main__":
    long_paths(r"Y:\Extras\Statewide\DEM\SDMI_IFSAR", 240)
