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

WARNING - The timestamp filtering doesn't work in general. A timestamp may be
added to the moves database that is before the saved last run time, or it may
be after now, in case it will be found again on the next run.
However, both of those case should never happen if the timestamp is always the
time that the record is added (and changes do not occur while this is script is
run).
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import csv
import datetime
import logging
import logging.config
import os
import sys

import config_file
import config_logger
import date_limited

# Set up the global logging object.
logging.config.dictConfig(config_logger.config)
# logging.raiseExceptions = False # Ignore errors in the logging system
logger = logging.getLogger("main")
logger.info("Logging Started")


# pylint: disable=too-many-locals
def read_csv_map(csv_path, since):
    """
    Read the moves database at csv_path.

    Moves database in file at csv_path contains timestamped move information.
    See https://github.com/AKROGIS/MapFixer for the format of the moves
    database.

    since is a datetime object. Only moves with a timestamp greater than since
    are returned.

    Return a list of moves as string tuples (source, destination) that have
    a timestamp greater than since.  The list may be empty.

    Any exceptions (IOErrors, invalid moves database, etc) are returned to the
    caller.
    """

    logger.debug("read_csv_map(%s, %s)", csv_path, since)

    # CSV file assumptions that may change if moves database is reformatted.
    delimiter = "|"
    timestamp_index = 0
    source_index = 1
    destination_index = 5
    # to convert datetime.datetime to string with strftime()
    timestamp_format = "%Y-%m-%d %H:%M:%S"

    # Return value
    records = []

    # short circuit if the moves database has not been edited since the last run.
    database_modtime = datetime.datetime.fromtimestamp(os.path.getmtime(csv_path))
    if database_modtime < since:
        logger.info("Moves database has not been modified since last run.")
        return None

    logger.info("Opening moves database at %s", csv_path)
    # Open file for Python 2 and Python 3 compatible CSV reading
    if sys.version_info[0] < 3:
        logger.debug("Opening in binary mode for Python 2")
        csv_file = open(csv_path, "rb")
    else:
        logger.debug("Opening as UTF-8 encoded unicode for Python 3")
        csv_file = open(csv_path, "r", encoding="utf-8", newline="")

    since_timestamp = since.strftime(timestamp_format)
    logger.info("Filtering on moves with timestamp > '%s'", since_timestamp)

    count = 0
    with csv_file as in_file:
        if sys.version_info[0] < 3:
            delimiter = delimiter.encode("utf-8")
        csv_reader = csv.reader(in_file, delimiter=delimiter)
        header = next(csv_reader)
        logger.debug(
            "Header fields[%d,%d,%d] = %s, %s, %s",
            timestamp_index,
            source_index,
            destination_index,
            header[timestamp_index],
            header[source_index],
            header[destination_index],
        )
        for row in csv_reader:
            timestamp = row[timestamp_index]
            source = row[source_index]
            destination = row[destination_index]
            if sys.version_info[0] < 3:
                timestamp = timestamp.decode("utf-8")
                source = source.decode("utf-8")
                destination = destination.decode("utf-8")

            count += 1
            if since_timestamp < timestamp:
                logger.debug("Found move (%s, %s, %s)", timestamp, source, destination)
                records.append((source, destination))

    logger.info("Found %d moves (out of %d total).", len(records), count)
    return records


def move_on_mounts(moves, mount_path, dry_run=True):
    """
    Make folder moves on all servers under mount_path.

    moves is a list of string tuples (source, destination) relative
    to mount_path/server{i}.

    mount_path is a file system path, either absolute or relative to the CWD.

    If dry_run is True, moves are logged, but not executed.  Moves are only
    executed if dry_run is False.

    All moves should be tried (assume moves has already been filtered).
    If a move fails, log the problem and continue.
    A move should fail if the source does not exist, or the destination exists.

    Nothing is returned.
    """
    logger.debug("Listing files in %s", mount_path)
    for server in os.listdir(mount_path):
        server_path = os.path.join(mount_path, server)
        if os.path.isfile(server_path):
            logger.debug("Skipping %s", server)
            continue
        move_on_server(moves, server_path, dry_run=dry_run)


def move_on_server(moves, server_path, dry_run=True):
    """
    Make folder moves on a single remote server.

    moves is a list of string tuples (source, destination) relative
    to server_path.

    server_path is a junction point, UNC, or equivalent, either absolute or
    relative to the CWD.

    If dry_run is True, moves are logged, but not executed.  Moves are only
    executed if dry_run is False.

    All moves should be tried (assume moves has already been filtered).
    If a move fails, log the problem and continue.
    A move should fail if the source does not exist, or the destination exists.

    Nothing is returned.
    """

    logger.debug("move_on_server(%s, %s, %s)", moves, server_path, dry_run)

    if not moves:
        logger.debug("No moves, returning early.")
        return

    if dry_run:
        logger.info("Doing a dry run; no folders will be moved.")

    for (source, destination) in moves:
        source_path = os.path.join(server_path, source)
        destination_path = os.path.join(server_path, destination)
        # do checks for logging, and to skip attempt when we know it will fail.
        logger.info("Move: %s => %s", source_path, destination_path)
        if not os.path.exists(source_path):
            logger.info("Skipping move, source does not exists.")
            continue
        # It is possible that the source_path is created between now and the
        # move below, but that is so unlikely as to not be worth considering.
        # if it happens, we can re-run, or robocopy will fix it the hard way.
        if os.path.exists(destination_path):
            logger.info("Skipping move, destination exists.")
            continue
        if not dry_run:
            try:
                # create any needed sub folders
                dest_folder = os.path.dirname(destination_path)
                if not os.path.exists(dest_folder):
                    logger.info("Creating destination folder %s", dest_folder)
                    os.makedirs(dest_folder)
                # Python 3.3+: If dst exists, the operation will fail with an
                # OSError subclass.
                # Python 2.7:  On Windows, if dst already exists, OSError will be
                # raised.  On Unix behavior may deviate is dst is a file.
                os.rename(source_path, destination_path)
                logger.info("Move succeeded.")
            except OSError as ex:
                logger.error("Move failed.")
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

    # Finally we are ready to start!
    if args.database is None:
        logger.error("Must specify moves database.")
    if args.mount_point is None and args.remote_server is None:
        logger.error("Must specify a mount point or remote server.")
    if args.database is not None and (
        args.mount_point is not None or args.remote_server is not None
    ):
        # wrapper for read_csv_map() to meet specification of timestamped_operation()
        def timed_csv_read(since):
            # I want to catch all exceptions for the logger, and to return T/F.
            # pylint: disable=broad-except
            moves = None
            try:
                moves = read_csv_map(args.database, since)
            except Exception as ex:
                logger.error("Unable to read moves database (%s)", args.database)
                logger.exception(ex)
                moves = None
            if moves is None:
                return False
            try:
                if args.remote_server is None:
                    move_on_mounts(moves, args.mount_point, args.dry_run)
                else:
                    move_on_server(moves, args.remote_server, args.dry_run)
            except Exception as ex:
                logger.error("Unable to rename/move folders.")
                logger.exception(ex)
                return False
            if args.dry_run:
                logger.info("Not updating the timestamp on a dry run")
                return False
            else:
                return True

        date_limited.timestamped_operation(
            timed_csv_read, timestamp_override=args.since
        )

    logger.info("Done!")
    logging.shutdown()


if __name__ == "__main__":
    main()
