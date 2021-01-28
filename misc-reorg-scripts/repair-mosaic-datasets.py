# -*- coding: utf-8 -*-
"""
Replaces old raster paths with new paths in a raster mosaic dataset.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import csv
from io import open
import logging
import os
import tempfile

import arcpy

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def check_folder(folder, outputter, replace_map, runas):
    if os.path.splitext(folder)[1].upper() == '.GDB':
        check_gdb(folder, outputter, replace_map, runas)
    else:
        for root, dirs, files in os.walk(folder):
            for name in dirs:
                if os.path.splitext(name)[1].upper() == '.GDB':
                    check_gdb(os.path.join(root, name), outputter, replace_map, runas)

def check_gdb(gdb, outputter, replace_map, runas):
    arcpy.env.workspace = gdb
    results = []

    # list of mosaic datasets in current gdb
    mosaics = arcpy.ListDatasets('*', 'Mosaic')

    for item in mosaics:
        #full path to mosaic
        mosaic = os.path.join(gdb, item)
        # writes mosaic-dataset-named dbf file to temp dir
        if mosaic not in replace_map:
            logger.warning('%s NOT in database', mosaic)
            # print('Mosaic %s not in database', mosaic)
        else:
            logger.info('%s found in database', mosaic)
            paths_list = replace_map[mosaic]
            paths = ''
            for item in paths_list:
                old_path, new_path = item
                if (old_path == 'NULL') or (new_path == 'NULL'):
                    logger.warning('%s check paths (NULL)', mosaic)
                else:
                    paths = paths + old_path + ' ' + new_path + ';'
            if runas == 'fix':
                try:
                    # print(mosaic, paths)
                    mosaic_repair(mosaic, paths)
                    logger.info('%s repair succeeded', mosaic)
                except arcpy.ExecuteError as ex:
                    logger.error('%s with paths %s repair error: %s', mosaic, paths, ex)
            if runas =='find-fix':
                # adding non-null path pairs into log file to show found fixes for current mosaic; could return to csv
                logger.info('Found non-null path pairs (old new;): %s', paths)
    return results

def mosaic_repair(mdname, paths, query='#'):

    arcpy.RepairMosaicDatasetPaths_management(mdname, paths, query)


def check_arcgis_ver():
    # ArcGIS version can be critical, check with user, prompt to continue
    logger.info('Running ArcGIS version %s - mosaic datasets are not backwards compatible, ensure users are at this version or higher.' % (arcpy.GetInstallInfo()['Version']))
    raw_input('Press Enter to continue...')

def printer(row):
    print(row)

def read_csv_map(csvpath):
    mappings = {}
    with open(csvpath, 'rb') as fh:
        # ignore the first record (header)
        fh.readline()
        for row in csv.reader(fh):
            unicode_row = [unicode(item, 'utf-8') if item else None for item in row]
            old_fgdb = unicode_row[0]
            mosaic = unicode_row[1]
            old_path = unicode_row[2]
            new_fgdb = unicode_row[3]
            new_path = unicode_row[4]
            new_fgdb_mosaic = os.path.join(new_fgdb, mosaic)
            if new_fgdb_mosaic not in mappings:
                mappings[new_fgdb_mosaic]=[]
            mappings[new_fgdb_mosaic].append((old_path,new_path))
    return mappings

def main(mosaic_datasets_root,csv_file,runas):

    if runas not in ['check', 'find-fix', 'fix']:
        runas = 'check'

    logger.info('########################################################')
    logger.info('Run %s %s', time.strftime("%H:%M:%S"), time.strftime("%d/%m/%Y"))

    check_arcgis_ver()
    # print('Running in %s mode at %s' % (runas, mosaic_datasets_root))
    logger.info('Running in %s mode at %s' % (runas, mosaic_datasets_root))

    replace_map = None
    if runas in ['find-fix', 'fix']:
        replace_map = read_csv_map(r'data\sql_moves_201712061100.csv')
        # print(replace_map)
        # update if returning output
        check_folder(mosaic_datasets_root, printer, replace_map, runas)
    # else for check ?

    # bye.
    logger.info('Ended %s %s', time.strftime("%H:%M:%S"), time.strftime("%d/%m/%Y"))
    logger.info('########################################################')


if __name__ == '__main__':
    logger.addHandler(logging.StreamHandler())
    logger.addHandler(logging.FileHandler(r"data\repair-mosaic-datasets.log"))
    logger.setLevel(logging.INFO)
    # runas is one of 'check', 'find-fix', 'fix'
    #   check just prints mosaic datasets with broken paths (fastest)
    #   find-fix does a 'check', and find/prints the fix
    #   fix does a 'find-fix' and then repairs and overwrites the layer files (slowest)
    #   the default is 'check'
    main('X:\Mosaics\BELA',csv_file='data/repair-mosaic-dataset.csv',runas='find-fix')

