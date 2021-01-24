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
            "See https://github.com/AKROGIS/MapFixer for format. "
            "The default is {0}."
        ).format(config_file.MOVES_DB),
    )
    parser.add_argument(
        "-m",
        "--mount_point",
        default=config_file.MOUNT_POINT,
        help=(
            "Path to a folder of server junction points. The default is {0}. "
            "The moves will occur on each server in MOUNT_POINT. "
            "Ignored if --remote_server is provided. "
            "One of --mount_point or --remote_server must be provided."
        ).format(config_file.MOUNT_POINT),
    )
    parser.add_argument(
        "-r",
        "--remote_server",
        help=(
            "Path to the remote server where the moves are to occur. "
            "This can be a UNC or local junction point, so long as the "
            "contents below the path match the X-Drive paths in the "
            "moves database. There is no default. "
            "If provided --mount_point will be ignored. "
            "One of --mount_point or --remote_server must be provided."
        ),
    )
    parser.add_argument(
        "-s",
        "--since",
        help=(
            "A date/time override for the timestamp file. "
            "All of the moves in the database since SINCE will be made. "
            "If not provided, then the 'timestamp' file is used. "
            "No processing will occur if no valid timestamp can be determined."
        ),
    )
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help=(
            "Check/test mode. Will do everything except move files. "
            "See the log file, or set verbose mode, to see the moves that "
            "would have been made."
        ),
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
        mount_point=args.mount_point,
        ref_timestamp=args.since,
        check_only=args.dry_run,
    )

    # Finally we are ready to start!
    if config.moves_db is None:
        logger.error("Must specify moves database.")
    if config.mount_point is None and args.remote_server is None:
        logger.error("Must specify a mount point or remote server.")
    if config.moves_db is not None and (
        config.mount_point is not None or args.remote_server is not None
    ):

        # pylint: disable=broad-except
        # I want to catch all exceptions for the logger.
        try:
            # TODO: read moves with date_limited.timestamped_operation()
            moves_data = read_csv_map(config.moves_db)
        except Exception as ex:
            logger.error("Unable to read moves database (%s)", config.moves_db)
            logger.exception(ex)
            moves_data = None
        if moves_data is not None:
            try:
                # FIXME: call with a single server or a mount point
                mover(moves_data, config)
            except Exception as ex:
                logger.error("Unable to rename/move folders.")
                logger.exception(ex)

    logger.info("Done!")
    logging.shutdown()


if __name__ == "__main__":
    main()
