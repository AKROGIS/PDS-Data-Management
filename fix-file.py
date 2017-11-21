"""
Uses the folder mapping file that Stephanie created to fix broken links in mxd and lyr files
"""

from __future__ import absolute_import, division, print_function, unicode_literals
import os
import csv
import logging
import arcpy

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def find_replacement(old_path, replace_map):
    """
    Returns the new_path to the resource at old_path, given a map of old_paths to new_paths

    The old_path can be partial prefixes or complete file paths
    Assume mapping does not have absolute paths (no drive or leading backslash)
    Assume old_path is an absolute path (with drive letter)
    Examples:
    given old_path (with drive and leading separator removed) = a/b/c.d
      if map has a -> Z, returns Z/b/c.d
      else if map has a/b -> X/Y/Z, returns X/Y/Z/c.d
      else if map has a/b/c.d -> W/e.f, returns W/e.f
      else returns None

    replace_map is a dict {old_path: new_path}
    """
    # remove drive letter
    _, path = os.path.splitdrive(old_path)

    # remove leading path.sep (otherwise split() result[0] == '')
    if path.startswith(os.path.sep):
        path = path[1:]
    path_parts = path.split(os.path.sep)
    tried_root = None
    for part in path_parts:
        if tried_root is None:
            tried_root = part
        else:
            tried_root = os.path.join(tried_root, part)
        try:
            return replace_map[tried_root]
        except KeyError:
            continue
    return None


def check_and_fix_file(path, replace_map, fix='check'):
    """
    Fix broken datasources in an mxd or layer file

    Currently only fixes File-based data that is moved to a different folder
    TODO: support other layer based datasource changes:
    Eventually I would like to support fixing more of the scenarios listed here:
    http://desktop.arcgis.com/en/arcmap/latest/analyze/arcpy-mapping/updatingandfixingdatasources.htm

    in particular:
    doc.replaceDataSource(workspace_path, workspace_type, {dataset_name}, {validate})  # lyr only

    But I need more information than is currently captured in the mappings file
    old workspace path and dataset name, to identify the layer needing repair,
    new workspace path, if not provided, get it from layer.workspacePath
    new dataset name if the datset name has changed (if not provided, the name remains unchanged)
    new workspace type; required.  Can I get the workspace type from the layer if not provided (not changing)?
       maybe with describe(workspace).workspaceProgID -> remap to strings required for import
     """
    if not os.path.isfile(path):
        logger.warning("%s is not found, or not a file", path)
        return

    _, extension = os.path.splitext(path)
    ext = extension.lower()
    if ext == ".mxd":
        try:
            doc = arcpy.mapping.MapDocument(path)
        except Exception as ex:
            logger.error('arcpy was unable to open %s', path)
            return
    elif ext == ".lyr":
        try:
            doc = arcpy.mapping.Layer(path)
        except Exception as ex:
            logger.error('arcpy was unable to open %s', path)
            return
    else:
        logger.warning("%s is not an .mxd or .lyr file", path)
        return

    save_required = False
    try:
        broken_layers = arcpy.mapping.ListBrokenDataSources(doc)
    except Exception as ex:
        logger.error('arcpy was unable to list the broken data sources in %s', path)
        return

    if not broken_layers:
        logger.info("%s has no broken data sources", path)
        return

    for layer in broken_layers:
        logger.warning('Layer %s in %s is broken', layer.name, path)
        if not layer.supports('WORKSPACEPATH'):
            logger.error('Layer %s in %s is broken, but does not have a workspace.  Skipping', layer.name, path)
            continue

        if fix == 'check':
            continue

        workspace = layer.workspacePath
        new_workspace = find_replacement(workspace, replace_map)
        if new_workspace is None:
            logger.error('Unable to find replacement for %s in %s.  Skipping', workspace, path)
            continue

        if fix == 'find-fix':
            logger.warn('Replace %s with %s in %s', workspace, new_workspace , path)
            continue

        try:
            layer.findAndReplaceWorkspacePath(workspace, new_workspace, False)
            save_required = True
        except Exception as ex:
            logger.error('Unable to repair layer  %s in %s, problem: %s', layer.name, path, ex)

    if save_required:
        try:
            doc.save()
            logger.info("%s has been repaired and saved", path)
        except Exception as ex:
            logger.error('arcpy was unable to save the repaired document %s', path)


def find_and_fix_all(start, extension, replace_map, fix='check'):
    """
    Find and fix all files with `extension' below start in the file system

    Broken datasources in a file are repaired by using the old -> new mappings in replace_map
    """
    extension_lowercase = extension.lower()
    if not extension_lowercase.startswith('.'):
        extension_lowercase = '.' + extension_lowercase
    for root, _, files in os.walk(start):
        for name in files:
            ext = os.path.splitext(name)[1].lower()
            if ext == extension_lowercase:
                old_path = os.path.join(root, name)
                logger.debug(old_path)
                check_and_fix_file(old_path, replace_map, fix=fix)


def read_csv_map(csvpath):
    mappings = {}
    with open(csvpath, 'rb') as fh:
        # ignore the first record (header)
        fh.readline()
        for row in csv.reader(fh):
            unicode_row = [unicode(item, 'utf-8') if item else None for item in row]
            old_path = unicode_row[0]
            new_path = unicode_row[2] if unicode_row[1] is None else unicode_row[1]
            mappings[old_path] = new_path
    return mappings


def main(fix='check'):
    if fix not in ['check', 'find-fix', 'fix']:
        fix = 'check'
    replace_map = None
    if fix in ['find-fix', 'fix']:
        replace_map = read_csv_map(r'data\PDS Moves - inpakrovmdist%5Cgisdata.csv')
    find_and_fix_all(r'X:\GIS\ThemeMgr', '.lyr', replace_map, fix=fix)


if __name__ == '__main__':
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.WARN)
    # fix is one of 'check', 'find-fix', 'fix'
    #   check just prints broken layers (fastest)
    #   find-fix does a 'check', and find/prints the fix
    #   fix does a 'find-fix' and then repairs and overwrites the layer files (slowest)
    #   the default is 'check'
    main(fix='check')
