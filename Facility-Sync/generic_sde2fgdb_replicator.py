# -*- coding: utf-8 -*-
"""
A generic tool to export an esri SDE database to a file geodatabase.

This tool is designed to be run as a scheduled task.
Since it is generic, it applies no special filters or transformations on the
data sets it exports.

This tool was tested with ArcGIS 10.6.1 and Pro 2.5.1
Non-standard modules:
  Relies on the esri `arcpy` module installed with ArcGIS.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import logging
import logging.handlers
import os
import shutil
import sys
import time

import arcpy

# pylint: disable=broad-except
# arcpy does not document the exceptions thrown, so we catch them all.
# all exceptions will be logged.


def get_database_items(workspace):
    """Returns a list of feature classes in the workspace."""
    log = logging.getLogger("script_log")
    arcpy.env.workspace = workspace
    feature_classes = []
    log.info("Compiling a list of items in %s.", workspace)
    for dir_path, _, filenames in arcpy.da.Walk(workspace, datatype="Any", type="Any"):
        for filename in filenames:
            feature_classes.append(os.path.join(dir_path, filename))
    count = len(feature_classes)
    log.info("There are a total of %i items in the database", count)
    return feature_classes


def replicate_database(db_connection, target_gdb):
    """Replicates the SDE database at `db_connection` to the FGDB at the path `target_gdb`."""
    log = logging.getLogger("script_log")

    if arcpy.Exists(db_connection):
        cnt_sde = len(get_database_items(db_connection))
        log.info(
            "Geodatabase being copied: %s -- Feature Count: %s", db_connection, cnt_sde
        )
        if arcpy.Exists(target_gdb):
            cnt_gdb = len(get_database_items(target_gdb))
            log.info(
                "Old Target Geodatabase: %s -- Feature Count: %s", target_gdb, cnt_gdb
            )
            try:
                shutil.rmtree(target_gdb)
                log.info("Deleted Old %s", os.path.split(target_gdb)[-1])
            except Exception as ex:
                log.error(ex)

        (gdb_path, gdb_name) = os.path.split(target_gdb)
        log.info("Now Creating New %s", gdb_name)
        arcpy.CreateFileGDB_management(gdb_path, gdb_name)

        arcpy.env.workspace = db_connection

        try:
            datasets = [arcpy.Describe(a).name for a in arcpy.ListDatasets()]
        except Exception as ex:
            datasets = []
            log.error(ex)
        try:
            feature_classes = [
                arcpy.Describe(a).name for a in arcpy.ListFeatureClasses()
            ]
        except Exception as ex:
            feature_classes = []
            log.error(ex)
        try:
            tables = [arcpy.Describe(a).name for a in arcpy.ListTables()]
        except Exception as ex:
            tables = []
            log.error(ex)

        # Compiles a list of the previous three lists to iterate over
        all_db_data = datasets + feature_classes + tables

        for source_path in all_db_data:
            target_name = source_path.split(".")[-1]
            target_path = os.path.join(target_gdb, target_name)
            if not arcpy.Exists(target_path):
                try:
                    log.info("Attempting to Copy %s to %s", target_name, target_path)
                    arcpy.Copy_management(source_path, target_path)
                    log.info("Finished copying %s to %s", target_name, target_path)
                except Exception as ex:
                    log.error("Unable to copy %s to %s", target_name, target_path)
                    log.error(ex)
            else:
                log.warning("%s already exists....skipping.....", target_name)

        cnt_gdb = len(get_database_items(target_gdb))
        log.info(
            "Completed replication of %s -- Feature Count: %s", db_connection, cnt_gdb
        )

    else:
        log.warning(
            "%s does not exist or is not supported! \
            Please check the database path and try again.",
            db_connection,
        )


def format_time(seconds):
    """Formats seconds as an ISO time string `hh:mm:ss`."""
    minutes, seconds_rem = divmod(seconds, 60)
    if minutes >= 60:
        hours, minutes_rem = divmod(minutes, 60)
        return "%02d:%02d:%02d" % (hours, minutes_rem, seconds_rem)
    return "00:%02d:%02d" % (minutes, seconds_rem)


def main():
    """Configure the logger and set configuration for the replications."""

    start_time = time.time()  # seconds for timing
    now = datetime.datetime.now()  # datetime for log file name

    ############################### user variables #################################
    # Change these variables to the location of the database being copied, the target
    # database location and where you want the log to be stored.

    log_path = (
        ""  # No path will put it in the current directory (likely the script directory)
    )
    target_gdb = r"c:\tmp\fmss\akr_facility_new.gdb"  # must be a full path
    db_connection = (
        r"X:\GIS\SDE Connection Files\inpakrovmais.akr_facilities.akr_reader_web.sde"
    )

    ############################### logging items ###################################
    # Get the global logging object.
    log = logging.getLogger("script_log")

    log.setLevel(logging.INFO)

    log_name = os.path.join(log_path, (now.strftime("%Y-%m-%d_%H-%M.log")))

    handler1 = logging.FileHandler(log_name)
    handler2 = logging.StreamHandler()

    formatter = logging.Formatter(
        "[%(levelname)s] [%(asctime)s] [%(lineno)d] - %(message)s",
        "%m/%d/%Y %I:%M:%S %p",
    )

    handler1.setFormatter(formatter)
    handler2.setFormatter(formatter)

    handler1.setLevel(logging.INFO)
    handler2.setLevel(logging.INFO)

    log.addHandler(handler1)
    log.addHandler(handler2)

    log.info("Script: %s", os.path.basename(sys.argv[0]))

    try:
        replicate_database(db_connection, target_gdb)
    except Exception as ex:
        log.exception(ex)

    total_time = format_time((time.time() - start_time))
    log.info("--------------------------------------------------")
    log.info("Script Completed After: %s", total_time)
    log.info("--------------------------------------------------")


if __name__ == "__main__":
    main()
