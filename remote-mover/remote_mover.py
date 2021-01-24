# -*- coding: utf-8 -*-
"""
Efficiently move data on remote servers to mimic the PDS.

This script will look for changes to the X drive's Permanent Data Set (PDS) by
querying a "moves database" for additions since the last time it was run.
When possible, it will replicate filesystem changes on the remote park servers
to minimize the work that robocopy needs to do.  For example, if a folder name
is changed, robocopy will only detect that the folder with the old name is gone
and delete it, and then create new folder by copying it over the network.
Since we are recording many file system changes in a "moves database",
we can avoid needlessly copying gigabytes of data over the network by simply
directing the remote server to rename the folder as appropriate.

This script is intended to be run as a scheduled task.  It should be
set up to finish before the robocopy process starts.

This tool was written for Python 2.7 and 3.6.

THIS SCRIPT IS NOT FINISHED AND DOES NOT WORK CORRECTLY
  - TODO: date_limited is not used
  - TODO: date_limited file reading/writing is not 2.7/3.6 compatible.
  - TODO: doesn't get a path to the remote server
  - TODO: CSV file reading is not both 2.7/3x compatible
 """

from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import csv
import logging
import logging.config
import os

from config import Config
import config_file
import config_logger
import date_limited

# Set up the global logging object.
logging.config.dictConfig(config_logger.config)
# logging.raiseExceptions = False # Ignore errors in the logging system
logger = logging.getLogger("main")
logger.info("Logging Started")


def read_csv_map(csvpath):
    """Read the moves database at csvpath."""

    logger.info("Opening moves database")
    records = []
    # FIXME: Crashes with no logging if file doesn't exist or cant be opened
    with open(csvpath, "rb") as in_file:
        # ignore the first record (header)
        in_file.readline()
        logger.info("Iterating moves database")
        for row in csv.reader(in_file, delimiter=str("|").encode("utf-8")):
            unicode_row = [unicode(item, "utf-8") if item else None for item in row]
            move_timestamp = unicode_row[0]
            old_workspace_path = unicode_row[1]
            old_workspace_type = unicode_row[2]
            old_dataset_name = unicode_row[3]
            old_dataset_type = unicode_row[4]
            new_workspace_path = unicode_row[5]
            new_workspace_type = unicode_row[6]
            new_dataset_name = unicode_row[7]
            new_dataset_type = unicode_row[8]
            records.append(
                (
                    move_timestamp,
                    old_workspace_path,
                    old_workspace_type,
                    old_dataset_name,
                    old_dataset_type,
                    new_workspace_path,
                    new_workspace_type,
                    new_dataset_name,
                    new_dataset_type,
                )
            )
    logger.info("Returning moves data.")
    return records


def mover(moves_data, config):
    """Move data on remote servers."""

    logger.info("Begin searching moves database.")
    if config.check_only:
        logger.info("Running in check_only mode.")

    for row in moves_data:
        (
            move_timestamp,
            old_workspace_path,
            old_workspace_type,
            old_dataset_name,
            _,
            new_workspace_path,
            new_workspace_type,
            _,
            _,
        ) = row
        old_workspace_path_c = os.path.join(config.remote_server, old_workspace_path)
        new_workspace_path_c = os.path.join(config.remote_server, new_workspace_path)

        # TODO: break out compound if statement for better logging/feedback to users
        if (
            (
                move_timestamp is None
                or config.ref_timestamp is None
                or move_timestamp >= config.ref_timestamp
            )
            and old_workspace_path != new_workspace_path
            and new_workspace_path is not None
            and old_workspace_path is not None
            and os.path.exists(old_workspace_path_c)
            and not os.path.exists(new_workspace_path_c)
            and new_workspace_type is None
            and old_workspace_type is None
            and old_dataset_name is None
        ):
            if config.check_only:
                logger.info(
                    "Match found for %s to %s",
                    old_workspace_path_c,
                    new_workspace_path_c,
                )
            else:
                try:
                    # find parent (lost child?)
                    new_workspace_path_parent_c = os.path.abspath(
                        os.path.join(new_workspace_path_c, os.pardir)
                    )
                    # if parent folder does not exist create necessary folder
                    # structure through parent folder
                    if not os.path.exists(new_workspace_path_parent_c):
                        os.makedirs(new_workspace_path_parent_c)
                        logger.info("Created %s", new_workspace_path_parent_c)
                    # move: rename folder - note, need to copy to parent,
                    # but report folder to folder as result
                    os.rename(old_workspace_path_c, new_workspace_path_c)
                    logger.info(
                        "Success: moved %s to %s",
                        old_workspace_path_c,
                        new_workspace_path_c,
                    )
                except IOError as ex:
                    logger.exception(ex)


def main():
    """Parse the command line options and set the configuration"""

    logger.info("Starting...")

    logger.debug("Get configuration overrides from the command line.")

    parser = argparse.ArgumentParser("Moves (renames) folders on a remote server.")
    parser.add_argument(
        "-d",
        "--database",
        default=config_file.MOVES_DB,
        help=(
            "The location of the moves database. "
            "See config file or default file for format. "
            "The default is {0}."
        ).format(config_file.MOVES_DB),
    )
    parser.add_argument(
        "-s",
        "--server",
        default=config_file.REMOTE_SERVER,
        help=(
            "Path to server location where moves are to occur. The default is {0}."
        ).format(config_file.REMOTE_SERVER),
    )
    parser.add_argument(
        "-t",
        "--timestamp",
        help=(
            "An override for the 'last time run' timestamp. "
            "If not provided, then the 'timestamp' file is used. "
            "No processing will occur if no valid timestamp can be determined."
        ),
    )
    parser.add_argument(
        "--check_only",
        action="store_true",
        help="Check/test mode. Will print but do the moves.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show informational messages."
    )
    parser.add_argument(
        "--debug", action="store_true", help="Show extensive debugging messages."
    )

    args = parser.parse_args()

    if args.verbose:
        logger.parent.handlers[0].setLevel(logging.INFO)
        logger.parent.handlers[1].setLevel(logging.INFO)
        logger.info("Started logging at INFO level.")
    if args.debug:
        logger.parent.handlers[0].setLevel(logging.DEBUG)
        logger.parent.handlers[1].setLevel(logging.DEBUG)
        logger.debug("Started logging at DEBUG level.")

    # Log the command line arguments
    logger.debug("Command line argument %s.", args)

    config = Config(
        moves_db=args.database,
        remote_server=args.server,
        ref_timestamp=args.timestamp,
        check_only=args.check_only,
    )

    # Finally we are ready to start!
    if config.moves_db is None:
        logger.error("Must specify moves database.")
    if config.remote_server is None:
        logger.error("Must specify a remote server path.")
    if config.moves_db is not None and config.remote_server is not None:
        moves_data = read_csv_map(config.moves_db)
        mover(moves_data, config)

    logger.info("Done!")
    logging.shutdown()


if __name__ == "__main__":
    main()
