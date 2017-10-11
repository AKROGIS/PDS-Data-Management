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
import tempfile
# import shutil


def check_gdb(gdb, outputter=None):
    # print(gdb)
    arcpy.env.workspace = gdb
    results = []
    # make folder for temp files.
    # I cant use a real temp file because to get a name, I must create it,
    # and arcpy.Export..() doesn't like the file existing even with arcpy.env.overwriteOutput = True
    temp_folder = tempfile.mkdtemp(prefix='mosaic_paths')
    for item in arcpy.ListDatasets('*', 'Mosaic'):
        print('{0},{1}'.format(gdb, item))
        mosaic = os.path.join(gdb, item)
        out_table = os.path.join(temp_folder, '{}.dbf'.format(item))
        # exports all paths and path types
        arcpy.ExportMosaicDatasetPaths_management(mosaic, out_table)
        with arcpy.da.SearchCursor(out_table, "Path") as cursor:
            for row in cursor:
                path = row[0]
                folder, name = os.path.split(path)
                name, ext = os.path.splitext(name)
                size = -1
                try:
                    size = os.path.getsize(path)
                except os.error:
                    pass
                if outputter is not None:
                    outputter([gdb, item, folder, name, ext, size])
                else:
                    results.append([gdb, item, folder, name, ext, size])
        os.remove(out_table)  # need to make sure locks are gone before removing folder
    # shutil.rmtree(temp_folder)  # fails due to a race condition with an ArcGIS lock
    return results


def printer(row):
    print(row)


def check_folder(folder, outputter=None):
    if os.path.splitext(folder)[1].upper() == '.GDB':
        check_gdb(folder, outputter)
    else:
        for root, dirs, files in os.walk(folder):
            for name in dirs:
                if os.path.splitext(name)[1].upper() == '.GDB':
                    check_gdb(os.path.join(root, name), outputter)


def main(folder, csv_file=None):
    if csv_file is None:
        check_folder(folder, printer)
    else:
        import csv
        with open(csv_file, 'w') as f:
            csv_writer = csv.writer(f)

            def put_in_csv(row):
                csv_writer.writerow(row)

            put_in_csv(['gdb', 'item', 'folder', 'name', 'ext', 'size'])
            check_folder(folder, put_in_csv)


if __name__ == '__main__':
    main(r'Z:\IServer\Mosaics\ANIA', 'data/images.csv')
