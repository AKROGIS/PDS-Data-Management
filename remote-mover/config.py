# -*- coding: utf-8 -*-
"""
A project specific configuration class

This class has hard coded configuration properties that have built in
defaults that con be overridden by importing `config_file.py`

This class was written for Python 2.7 and 3.6.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import config_file

logger = logging.getLogger(__name__)


class Config(object):
    """
    A collection of readonly properties that are initialized at application startup, and passed
    to the various objects and functions to avoid reliance on global variables.
    """

    def __init__(
        self,
        moves_db=None,
        ref_timestamp=None,
        mount_point=None,
        check_only=None,
    ):
        logger.debug("Initializing Config...")
        self.__moves_db = moves_db if moves_db is not None else config_file.MOVES_DB
        self.__ref_timestamp = ref_timestamp
        self.__mount_point = (
            mount_point if mount_point is not None else config_file.MOUNT_POINT
        )
        self.__check_only = check_only
        logger.debug("Initialized Config: %s", self)

    @property
    def moves_db(self):
        """Moves db path (required, see format elsewhere, | delimited)."""

        return self.__moves_db

    @property
    def ref_timestamp(self):
        """A reference timestamp for the last run (date and time, UTC)."""
        return self.__ref_timestamp

    @property
    def mount_point(self):
        """Path to mount point (a folder of junction points to remote servers)."""
        return self.__mount_point

    @property
    def check_only(self):
        """Check-only/test mode."""
        return self.__check_only

    def __str__(self):
        text = "<moves_db: {0}, ref_timestamp: {1}, mount_point: {2}, check_only: {3}>"
        text = text.format(
            self.moves_db,
            self.ref_timestamp,
            self.mount_point,
            self.check_only,
        )
        return text
