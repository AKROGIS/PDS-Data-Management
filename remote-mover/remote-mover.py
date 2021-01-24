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
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import logging
import logging.config
import os
import time

from config import Config
import config_logger
import date_limited

logging.config.dictConfig(config_logger.config)
# logging.raiseExceptions = False # Ignore errors in the logging system
logger = logging.getLogger('main')
logger.info("Logging Started")

def read_csv_map(csvpath):
    """Read the moves database at csvpath."""
    
    logger.info('Opening moves database')
    records = []
    with open(csvpath, 'rb') as fh:
        # ignore the first record (header)
        fh.readline()
        logger.info('Iterating moves database')
        for row in csv.reader(fh, delimiter=str(u'|').encode('utf-8')):
            unicode_row = [unicode(item, 'utf-8') if item else None for item in row]
            move_timestamp = unicode_row[0]
            old_workspace_path = unicode_row[1]
            old_workspace_type = unicode_row[2]
            old_dataset_name = unicode_row[3]
            old_dataset_type = unicode_row[4]
            new_workspace_path = unicode_row[5]
            new_workspace_type = unicode_row[6]
            new_dataset_name = unicode_row[7]
            new_dataset_type = unicode_row[8]
            records.append((move_timestamp,old_workspace_path,old_workspace_type,old_dataset_name,old_dataset_type,new_workspace_path,new_workspace_type,new_dataset_name,new_dataset_type))
    logger.info('Returning moves data.')
    return records

def mover(moves_data, config):
    """Move data on remote servers."""

    logger.info('Begin searching moves database.')
    if config.check_only:
        logger.info('Running in check_only mode.')

    for row in moves_data:
        move_timestamp,old_workspace_path,old_workspace_type,old_dataset_name,old_dataset_type,new_workspace_path,new_workspace_type,new_dataset_name,new_dataset_type = row
        old_workspace_path_c = os.path.join(config.remote_server,old_workspace_path)
        new_workspace_path_c = os.path.join(config.remote_server,new_workspace_path)

        # may want to break out compound if statement for better logging/feedback to users?
        if (move_timestamp is None or config.ref_timestamp is None or move_timestamp >= config.ref_timestamp) and \
        old_workspace_path <> new_workspace_path and \
        new_workspace_path is not None and \
        old_workspace_path is not None and \
        os.path.exists(old_workspace_path_c) and \
        not os.path.exists(new_workspace_path_c) and \
        new_workspace_type is None and \
        old_workspace_type is None and \
        old_dataset_name is None:
            if config.check_only:
                logger.info('Match found for %s to %s',old_workspace_path_c,new_workspace_path_c)
            else:
                try:
                    # find parent (lost child?)
                    new_workspace_path_parent_c = os.path.abspath(os.path.join(new_workspace_path_c, os.pardir))
                    # if parent folder does not exist create necessary folder structure through parent folder
                    if not os.path.exists(new_workspace_path_parent_c):
                        os.makedirs(new_workspace_path_parent_c)
                        logger.info('Created %s',new_workspace_path_parent_c)
                    # move: rename folder - note, need to copy to parent, but report folder to folder as result
                    os.rename(old_workspace_path_c,new_workspace_path_c)
                    logger.info('Success: moved %s to %s',old_workspace_path_c,new_workspace_path_c)
                except BaseException as err:
                    logger.error('ERROR: %s %s',err.message, err.args)

def main():
    """Parse the command line option and set the configuration"""

    logger.info('Starting...')

    logger.debug("Get default configuration parameters from a configuration file.")
    try:
        import config_file
    except ImportError as err:
        logger.warning("Unable to load the config file: %s", err)

        class ConfigFile:
            def __init__(self):
                self.moves_db = None
                self.ref_timestamp = None
                self.remote_server = None
                self.log_file = None
                self.check_only = None
        config_file = ConfigFile()

    logger.debug("Get configuration overrides from the command line.")
    import argparse
    parser = argparse.ArgumentParser('Moves (renames) folders on a remote server. ')
    parser.add_argument('-d', '--database', default=config_file.moves_db,
                        help=('The location of the moves database. '
                              'See config file or default file for format. '
                              'The default is {0}').format(config_file.moves_db))
    parser.add_argument('-s', '--server', default=config_file.remote_server,
                        help=('Path to server location where moves are to occur. '
                              'The default is {0}').format(config_file.remote_server))
    parser.add_argument('-t', '--timestamp', default=config_file.ref_timestamp,
                        help=('The reference (last run) timestamp. '
                              'No timestamp will consider all valid moves from database. '
                              'The default is {0}').format(config_file.ref_timestamp))
    parser.add_argument('-n', '--name', default=config_file.name,
                        help=('The short name for the time stamp and log files. '
                              'The default is {0}').format(config_file.name))
    parser.add_argument('--check_only', action='store_true', help='Check/test mode - log only, will not move folders. ')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show informational messages. ')
    parser.add_argument('--debug', action='store_true', help='Show extensive debugging messages. ')

    args = parser.parse_args()

    if args.verbose:
        logger.parent.handlers[0].setLevel(logging.INFO)
        logger.parent.handlers[1].setLevel(logging.INFO)
        logger.info("Started logging at INFO level")   
    if args.debug:
        logger.parent.handlers[0].setLevel(logging.DEBUG)
        logger.parent.handlers[1].setLevel(logging.DEBUG)
        logger.debug("Started logging at DEBUG level")        

    # Log the command line arguments
    logger.debug("Command line argument %s", args)

    config = Config(moves_db = args.database,
                    remote_server = args.server,
                    ref_timestamp = args.timestamp,
                    name = args.name,
                    check_only = args.check_only)

    # Finally we are ready to start!
    if config.moves_db is None or config.remote_server is None:
        logger.error('Must specify moves database and remote server paths.')
    else:
        moves_data = read_csv_map(config.moves_db)
        mover(moves_data, config)

    logger.info('Done!')
    logging.shutdown()


if __name__ == '__main__':
    main()
