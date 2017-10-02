from __future__ import absolute_import, division, print_function, unicode_literals
import os
import logging
import arcpy

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def fix_file(path, replace_map):
    broken_layers = []
    doc = None
    if os.path.isfile(path):
        basename, extension = os.path.splitext(path)
        ext = extension.lower()
        if ext == ".mxd":
            doc = arcpy.mapping.MapDocument(path)
        elif ext == ".lyr":
            doc = arcpy.mapping.Layer(path)
        if doc is None:
            logger.warning("%s is not an .mxd or .lyr file", path)
    else:
        logger.warning("%s is not found, or not a file", path)
    if doc is not None:
        broken_layers = arcpy.mapping.ListBrokenDataSources(doc)
        if len(broken_layers) == 0:
            logger.info("%s has no broken data sources", path)
        for layer in broken_layers:
            if layer.supports('DATASOURCE'):
                data_source = layer.dataSource
            else:
                logger.error('A broken layer that does not have a datasource')

            # workspace type must be the same
            doc.findAndReplaceWorkspacePath(bad_path, new_path, False)  # lyr
            doc.findAndReplaceWorkspacePaths(bad_path, new_path, False)  # mxd
            # can change data source name and type
            doc.replaceDataSource(workspace_path, workspace_type, {dataset_name}, {validate})  # lyr only
            # replace the workspace type for multiple datasources, but not datasource names
            doc.replaceWorkspaces (old_workspace_path, old_workspace_type, new_workspace_path, new_workspace_type, {validate})  # mxd only

        doc.save()  # lyr or mxd