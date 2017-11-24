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
    mosaics = arcpy.ListDatasets('*', 'Mosaic')
    contents = 'JustMosaics'
    if mosaics:
        all_items = arcpy.ListDatasets('*')
        if len(mosaics) != len(all_items):
            contents = 'Mixed'
    for item in mosaics:
        mosaic = os.path.join(gdb, item)
        try:
            ref = arcpy.Describe(mosaic).referenced
        except AttributeError as ex:
            print('{},{},{},{},{}'.format(gdb, item, contents, 'NA', ex))
            continue
        if ref:
            print('{0},{1},{2},{3},'.format(gdb, item, contents, ref))
            continue
        out_table = os.path.join(temp_folder, '{}.dbf'.format(item))
        # exports all paths and path types
        try:
            arcpy.ExportMosaicDatasetPaths_management(mosaic, out_table)
        except arcpy.ExecuteError as ex:
            print('{},{},{},{},{}'.format(gdb, item, contents, ref, ex))
            continue
        print('{},{},{},{},'.format(gdb, item, contents, ref))
        with arcpy.da.SearchCursor(out_table, ["Path","SourceOID"]) as cursor:
            for row in cursor:
                path = row[0]
                sid = row[1]
                folder, name = os.path.split(path)
                name, ext = os.path.splitext(name)
                size = -1
                try:
                    size = os.path.getsize(path)
                except os.error:
                    pass
                if outputter is not None:
                    outputter([gdb, item, folder, name, ext, sid, size])
                else:
                    results.append([gdb, item, folder, name, ext, sid, size])
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

            put_in_csv(['fgdb', 'mosaic', 'folder', 'filename', 'extension', 'sourceoid', 'size'])
            check_folder(folder, put_in_csv)


if __name__ == '__main__':
    main('Z:\\', 'data/images_z.csv')
    main('X:\\', 'data/images_x.csv')
