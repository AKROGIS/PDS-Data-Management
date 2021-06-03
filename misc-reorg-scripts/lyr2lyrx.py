# -*- coding: utf-8 -*-
"""
Convert layer files from ArcGIS 10.x `*.lyr` to ArcGIS Pro `*.lyrx`

An input folder is searched recursively, and a mirror folder structure will be
created in the output folder with every `*.lyr` file replaced with the equivalent
`*.lyrx` file.

Requires arcpy from ArcGIS Pro and Python 3.6+
This script will not work with arcpy from ArcGIS 10.x
"""

import shutil
import os

import arcpy.mp


class Config(object):
    """Namespace for configuration parameters. Edit as needed."""

    # pylint: disable=useless-object-inheritance,too-few-public-methods

    # Input folder - Where in the file system to start recursively looking
    # for layer (*.lyr) files.
    input_folder = r"X:\GIS\ThemeMgr"

    # Output folder - Where in the file system to start recursively writing
    # the new layer (`*.lyrx`) files.  If None or empty, then output_folder
    # is set to the input_folder
    output_folder = r"C:\tmp\ThemeMgrPro"


def is_old_layer_file(file_name):
    """Return True if file_name is an ArcGIS 10.x layer (`*.lyr`) file."""

    return file_name.lower().endswith(".lyr")


def convert(old_root, new_root):
    """Convert old layer files in old_root to new layer files in new_root

    new_root can be None or equivalent in which it will be the same as old_root

    If new_root is not equal to old_root, and new_root exists, existing content
    may cause this script to fail.
    """

    if not new_root:
        new_root = old_root
    if not os.path.exists(new_root):
        os.mkdir(new_root)
    for folder, folder_names, file_names in os.walk(old_root):
        new_folder = folder.replace(old_root, new_root)
        for folder_name in folder_names:
            if new_folder != folder:
                os.mkdir(os.path.join(new_folder, folder_name))
        for file_name in file_names:
            old_path = os.path.join(folder, file_name)
            new_path = os.path.join(new_folder, file_name)
            if is_old_layer_file(file_name):
                new_path = new_path + "x"
                # print(f"Converting {old_path} to {new_path}")
                try:
                    layer_file = arcpy.mp.LayerFile(old_path)
                    layer_file.saveACopy(new_path)
                except RuntimeError as ex:
                    print(f"{ex} {old_path}")
            else:
                if old_path != new_path:
                    shutil.copy(old_path, new_path)


if __name__ == "__main__":
    convert(Config.input_folder, Config.output_folder)
