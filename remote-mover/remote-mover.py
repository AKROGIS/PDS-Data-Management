from __future__ import absolute_import, division, print_function, unicode_literals
from config import Config
import logging
import logging.config
import config_logger
import time
import os
import csv

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
            timestamp = unicode_row[0]
            old_workspace_path = unicode_row[1]
            old_workspace_type = unicode_row[2]
            old_dataset_name = unicode_row[3]
            old_dataset_type = unicode_row[4]
            new_workspace_path = unicode_row[5]
            new_workspace_type = unicode_row[6]
            new_dataset_name = unicode_row[7]
            new_dataset_type = unicode_row[8]
            records.append((old_workspace_path,old_workspace_type,old_dataset_name,old_dataset_type,new_workspace_path,new_workspace_type,new_dataset_name,new_dataset_type))
    logger.info('Returning moves data.')
    return records

def aggregate_data_sources(config):
    if config.is_incremental:
        logger.info('Doing incremental update for Owner:%s DataType:%s SubType:%s',
                    config.owner_name, config.data_type_name, config.sub_type)
        data_types = DataType.incremental_data_types(config)
    else:
        logger.info('Doing full update')
        data_types = DataType.all_data_types(config)
    for data_type in data_types:
        logger.info('Aggregating %s', data_type.name)
        if config.is_incremental:
            aggregate_table = data_type.most_recent_staging_table
            if aggregate_table is None:
                logger.warning("No %s aggregation table to update. Doing full aggregation", data_type.name)
                incremental_load = False
                aggregate_table = data_type.create_aggregate_table()
                ready_for_aggregation = aggregate_table is not None
            else:
                incremental_load = True
                ready_for_aggregation = data_type.clear_aggregate_table(aggregate_table)
        else:
            incremental_load = False
            aggregate_table = data_type.create_aggregate_table()
            ready_for_aggregation = aggregate_table is not None

        if not ready_for_aggregation:
            logger.warning("Aggregation table not successfully created or cleared.  Skipping data load.")
        else:
            for data_source in DataSource.data_sources_to_aggregate(config=config,
                                                                    data_type=data_type,
                                                                    full_load_override=(not incremental_load)):
                data_source.aggregate(aggregate_table)
            if not incremental_load:
                data_type.add_objectid_and_indexes(aggregate_table)
                data_type.update_views(aggregate_table)

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
                        help=('The reference (last run) timestamp file location. '
                              'No timestamp will consider all valid moves from database. '
                              'The default is {0}').format(config_file.ref_timestamp))
    parser.add_argument('-l', '--logfile', default=config_file.log_file,
                        help=('The log file location. '
                              'The default is {0}').format(config_file.log_file))
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

    config = Config(db,
                    moves_db = args.moves_db,
                    ref_timestamp = args.ref_timestamp,
                    remote_server = args.remote_server,
                    log_file = args.log_file)

    # Finally we are ready to start!

    if args.moves_db is None:
        logger.error('No moves database specified.')
        exit
    else if args.remote_server is None:
        logger.error('No server path specified.')
        exit

    moves_data = read_csv_map(moves_db)

    mover(moves_data)

    logger.info('Done!')
    logging.shutdown()


if __name__ == '__main__':
    main()
