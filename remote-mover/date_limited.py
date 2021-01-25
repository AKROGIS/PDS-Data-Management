# -*- coding: utf-8 -*-
"""
Functions for running an operation with a persisted "last time run" timestamp.

timestamped_operation() is the only "public" method.  The others exist
to support it, however the other functions could be used on their own in some
use cases.

These functions were written for Python 2.7 and 3.6.
Non standard modules:
  dateutil (in function parse_timestamp) pip install python-dateutil
  only required if the timestamp_override is provided as a string.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
from io import open
import logging
import sys


logger = logging.getLogger(__name__)


def timestamped_operation(operation, utc=False, prefix=None, timestamp_override=None):
    """
    Calls operation with a single datetime object parameter.

    The datetime object is either derived from either
    * the timestamp_override, which can be a string or a datetime object.
      If it is a string it is parsed with the 3rd party dateutils module.
    * or a timestamp file called `prefix.timestamp` or just `timestamp` if
      prefix is None. The timestamp file is formatted as a single row of comma
      separated integers: year,month,day,hour,minute,second,microsecond.

    operation is only executed (and the timestamp updated) if a valid datetime
    can be found.

    Since the timestamp file does not encode the timestamp, the user needs to
    specify if it is UTC (utc=True), or local (default).

    operation must return a boolean to indicate if the timestamp file should
    be updated with the time the operation started.

    Since most interesting user functions do not meet the calling and return
    requirements of operation, it is incumbent on the user to wrap their
    interesting function in wrapper function (or lambda) that matches operation.

    This method has no return value.
    """

    logger.debug("timestamped_operation(op, %s, %s, %s)", utc, prefix, timestamp_override)

    last_run_time = get_last_run_time(prefix, timestamp_override)

    if last_run_time is None:
        logger.warning("The 'last run time` could not be determined.")
        return
    logger.debug("Using last run time of: %s", last_run_time)

    this_run_time = get_this_run_time(utc)
    if operation(last_run_time):
        save_last_run_time(this_run_time, prefix)


def get_this_run_time(utc):
    """Return the current time in UTC (utc=True) or local."""

    logger.debug("get_this_run_time(%s)", utc)

    if utc:
        return datetime.datetime.utcnow()
    return datetime.datetime.now()


def get_last_run_time(prefix=None, timestamp_override=None):
    """Get the datetime of the last run from the override or the persistance file."""

    logger.debug("get_last_run_time(%s, %s)", prefix, timestamp_override)

    if isinstance(timestamp_override, datetime.datetime):
        return timestamp_override

    if sys.version_info[0] < 3:
        # pylint: disable=undefined-variable
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

    logger.debug("get_last_run_time_from_file(%s)", prefix)

    if prefix is None:
        name = "timestamp"
    else:
        name = "{0}.timestamp".format(prefix)
    logger.debug("timestamp filename: %s", name)
    try:
        with open(name, "r", encoding="utf8") as in_file:
            for line in in_file:
                return datetime.datetime(*[int(i) for i in line.split(",")])
    except (IOError, ValueError, TypeError) as ex:
        logger.error("Unable to open the timestamp file: %s", name)
        logger.exception(ex)
        return None


def save_last_run_time(since, prefix=None):
    """Save the datetime `since` in the persistance file."""

    logger.debug("save_last_run_time(%s, %s)", since, prefix)

    if prefix is None:
        name = "timestamp"
    else:
        name = "{0}.timestamp".format(prefix)
    logger.debug("save_last_run_time (%s) in %s", since, name)
    try:
        with open(name, "w", encoding="utf8") as out_file:
            time = "{0},{1},{2},{3},{4},{5},{6}".format(
                since.year,
                since.month,
                since.day,
                since.hour,
                since.minute,
                since.second,
                since.microsecond,
            )
            out_file.write(time)
    except (IOError, ValueError, TypeError) as ex:
        logger.error("Unable to update the timestamp file: %s", name)
        logger.exception(ex)


def parse_timestamp(timestamp):
    """Create a datetime from a command line timestamp string.

    Requires the optional module dateutil.  pip install python-dateutil
    """

    logger.debug("parse_timestamp(%s)", timestamp)

    try:
        # pylint: disable=import-outside-toplevel
        # I ony want to import this non-standard module if it is needed.
        import dateutil.parser
    except ImportError:
        logger.error(
            "dateutil.parser module is required for the SINCE option."
            "install with pip install python-dateutil"
        )
        return None
    try:
        return dateutil.parser.parse(timestamp)
    except (ValueError, OverflowError) as ex:
        logger.error('Unable to parse "%s" as a valid timestamp', timestamp)
        logger.exception(ex)
        return None
