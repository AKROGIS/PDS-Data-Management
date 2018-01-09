from __future__ import absolute_import, division, print_function, unicode_literals
from config import Config
import logging
import logging.config
import config_logger
import time
import os
import csv
import date_limited

logging.config.dictConfig(config_logger.config)
# logging.raiseExceptions = False # Ignore errors in the logging system
logger = logging.getLogger('main')
logger.info("Logging Started")

def read_csv_map(csvpath):
    logger.info('Opening moves database')
    records = []
    with open(csvpath, 'rb') as fh:
        # ignore the first record (header)
        fh.readline()
        logger.info('Iterating moves database')
        for row in csv.reader(fh, delimiter ='|'):
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
    for row in moves_data: 
        move_timestamp,old_workspace_path,old_workspace_type,old_dataset_name,old_dataset_type,new_workspace_path,new_workspace_type,new_dataset_name,new_dataset_type = row
        old_workspace_path_c = os.path.join(config.remote_server,old_workspace_path)
        new_workspace_path_c = os.path.join(config.remote_server,new_workspace_path)

        if (move_timestamp is None or config.ref_timestamp is None or move_timestamp > config.ref_timestamp) and \
        old_workspace_path <> new_workspace_path and \
        new_workspace_path is not None and \
        old_workspace_path is not None and \
        os.path.exists(old_workspace_path_c) and \
        not os.path.exists(new_workspace_path_c) and \
        new_workspace_type is None and \
        old_workspace_type is None and \
        old_dataset_name is None:
            try:
                # find parent (lost child?)
                new_workspace_path_parent_c = os.path.abspath(os.path.join(new_workspace_path_c, os.pardir))
                # if parent folder does not exist create necessary folder structure through parent folder
                if not os.path.exists(new_workspace_path_parent_c):
                    os.makedirs(new_workspace_path_parent_c)
                    logger.info('Created %s',new_workspace_path_parent_c)
                # move: rename folder
                os.rename(old_workspace_path_c,new_workspace_path_c)
                logger.info('Success: moved %s to %s',old_workspace_path_c,new_workspace_path_c)
            except BaseException as err:
                logger.error('ERROR: %s %s',err.message, err.args)

def main():
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

    config = Config(moves_db = args.moves_db,
                    ref_timestamp = args.ref_timestamp,
                    remote_server = args.remote_server,
                    name = args.name)

    # Finally we are ready to start!

    if args.moves_db is None:
        logger.error('No moves database specified.')
        exit
    if args.remote_server is None:
        logger.error('No server path specified.')
        exit

    moves_data = read_csv_map(moves_db)

    # operation_params = {moves_data, remote_server}
    # date_limited.timestamped_operation(mover, operation_params, prefix=name, timestamp_override=args.since)
    mover(moves_data, config)

    logger.info('Done!')
    logging.shutdown()


if __name__ == '__main__':
    main()
