"""
walk file system finding geodatabases
if there is a raster mosaic dataset in the gdb, then list it and all
the images it references

use arcpy
 ListDatasets, ListFeatureClasses, ListFiles, ListRasters, ListTables, and ListWorkspaces
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import arcpy
import os


def check_gdb(gdb):
    # print(gdb)
    arcpy.env.workspace = gdb
    for item in arcpy.ListDatasets('*', 'Mosaic'):
        print('{0},{1}'.format(gdb, item))
        mosaic = os.path.join(gdb, item)
        # exports all paths and path types
        out_table = 'c:/tmp/junk/' + item + '.dbf'
        arcpy.ExportMosaicDatasetPaths_management(mosaic, out_table)


def main(folder):
    if os.path.splitext(folder)[1].upper() == '.GDB':
        check_gdb(folder)
    else:
        for root, dirs, files in os.walk(folder):
            for name in dirs:
                if os.path.splitext(name)[1].upper() == '.GDB':
                    check_gdb(os.path.join(root, name))


if __name__ == '__main__':
    main(r'Z:\IServer\Mosaics\ANIA')
