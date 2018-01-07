from __future__ import absolute_import, division, print_function, unicode_literals
import datetime
import logging

logger = logging.getLogger(__name__)


def timestamped_operation(operation, args, prefix=None, timestamp_override=None):
    # Get current time to save as last run time we are successful; Do everything in UTC
    this_run_time = get_this_run_time()
    last_run_time = get_last_run_time(prefix, timestamp_override)

    if last_run_time is None:
        logger.warning("No last_run_time was provided or found.")
        return
    logger.debug("Using last run time of: %s", last_run_time)

    args['since'] = last_run_time
    if operation(args):
        save_last_run_time(this_run_time, prefix)


def get_this_run_time():
    return datetime.datetime.utcnow()


def get_last_run_time(prefix=None, timestamp_override=None):
    if type(timestamp_override) is datetime.datetime:
        return timestamp_override

    elif isinstance(timestamp_override, (str, unicode)):
        last_run_time = parse_timestamp(timestamp_override)
        logger.debug("Using the command line timestamp override %s", last_run_time)
        return last_run_time

    elif timestamp_override is None:
        return get_last_run_time_from_file(prefix)

    logger.debug("Timestamp override is an unexpected type %s", type(timestamp_override))
    return None


def get_last_run_time_from_file(prefix=None):
    if prefix is None:
        name = 'timestamp'
    else:
        name = '{0}.timestamp'.format(prefix)
    logger.debug("get_last_run_time for %s", name)
    try:
        with open(name, 'r') as f:
            for line in f:
                return datetime.datetime(*[int(i) for i in line.split(',')])
    except (IOError, ValueError, TypeError) as ex:
        logger.error("Unable to open the timestamp file: %s (%s)", name, ex.message)
        return None


def save_last_run_time(since, prefix=None):
    if prefix is None:
        name = 'timestamp'
    else:
        name = '{0}.timestamp'.format(prefix)
    logger.debug("save_last_run_time (%s) in %s", since, name)
    try:
        with open(name, 'w') as f:
            t = '{0},{1},{2},{3},{4},{5},{6}'.format(
                since.year, since.month, since.day, since.hour,
                since.minute, since.second, since.microsecond)
            f.write(t.encode('utf8'))
    except (IOError, ValueError, TypeError) as ex:
        logger.error("Unable to update the timestamp file: %s (%s)", name, ex.message)
        return None


def parse_timestamp(timestamp):
    logger.debug("Attempting to parse the command line timestamp %s", timestamp)
    try:
        # noinspection PyUnresolvedReferences
        import dateutil.parser
    except ImportError:
        logger.error('dateutil.parser module is required for the SINCE option.'
                     'install with pip install python-dateutil')
        return None
    try:
        return dateutil.parser.parse(timestamp)
    except (ValueError, OverflowError) as ex:
        logger.error('Unable to parse "%s" as a valid timestamp, %s', timestamp, ex.message)
        return None
