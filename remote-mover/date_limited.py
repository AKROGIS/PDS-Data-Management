# -*- coding: utf-8 -*-
"""
Functions for persisting timestamps to control behavior of a script.

These can be used to record the last successful run of a script, so
that we can look for changes since then.

These functions were written for Python 2.7 and 3.6.
Non standard modules:
  dateutil (in function parse_timestamp) pip install python-dateutil
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import logging
import sys

logger = logging.getLogger(__name__)


def timestamped_operation(operation, args, prefix=None, timestamp_override=None):
    """Executes operation with the args parameter augmented with since = last_run time."""

    this_run_time = get_this_run_time()
    last_run_time = get_last_run_time(prefix, timestamp_override)

    if last_run_time is None:
        logger.warning("No last_run_time was provided or found.")
        return
    logger.debug("Using last run time of: %s", last_run_time)

    args["since"] = last_run_time
    if operation(args):
        save_last_run_time(this_run_time, prefix)


def get_this_run_time():
    """Return the current time in UTC."""

    return datetime.datetime.utcnow()


def get_last_run_time(prefix=None, timestamp_override=None):
    """Get the datetime of the last run from the override or the persistance file."""

    if isinstance(timestamp_override, datetime.datetime):
        return timestamp_override

    if sys.version_info[0] < 3:
        is_string = isinstance(timestamp_override, basestring)
    else:
        is_string = isinstance(timestamp_override, str)
    if is_string:
        last_run_time = parse_timestamp(timestamp_override)
        logger.debug("Using the command line timestamp override %s", last_run_time)
        return last_run_time

    if timestamp_override is None:
        return get_last_run_time_from_file(prefix)

    logger.debug(
        "Timestamp override is an unexpected type %s", type(timestamp_override)
    )
    return None


def get_last_run_time_from_file(prefix=None):
    """Get the datetime of the last run from the persistance file."""

    if prefix is None:
        name = "timestamp"
    else:
        name = "{0}.timestamp".format(prefix)
    logger.debug("get_last_run_time for %s", name)
    try:
        with open(name, "r") as in_file:
            for line in in_file:
                return datetime.datetime(*[int(i) for i in line.split(",")])
    except (IOError, ValueError, TypeError) as ex:
        logger.error("Unable to open the timestamp file: %s", name)
        logger.exception(ex)
        return None


def save_last_run_time(since, prefix=None):
    """Save the datetime `since` in the persistance file."""

    if prefix is None:
        name = "timestamp"
    else:
        name = "{0}.timestamp".format(prefix)
    logger.debug("save_last_run_time (%s) in %s", since, name)
    try:
        with open(name, "w") as out_file:
            time = "{0},{1},{2},{3},{4},{5},{6}".format(
                since.year,
                since.month,
                since.day,
                since.hour,
                since.minute,
                since.second,
                since.microsecond,
            )
            out_file.write(time.encode("utf8"))
    except (IOError, ValueError, TypeError) as ex:
        logger.error("Unable to update the timestamp file: %s", name)
        logger.exception(ex)


def parse_timestamp(timestamp):
    """Create a datetime from a command line timestamp string.

    Requires the optional module dateutil.  pip install python-dateutil
    """

    logger.debug("Attempting to parse the command line timestamp %s", timestamp)
    try:
        # pylint: disable=import-outside-toplevel
        # I ony want to import this non-standard module if it is needed.
        import dateutil.parser
    except ImportError:
        logger.error(
            "dateutil.parser module is required for the TIMESTAMP option."
            "install with pip install python-dateutil"
        )
        return None
    try:
        return dateutil.parser.parse(timestamp)
    except (ValueError, OverflowError) as ex:
        logger.error('Unable to parse "%s" as a valid timestamp', timestamp)
        logger.exception(ex)
        return None
