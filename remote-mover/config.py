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

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        moves_db=None,
        ref_timestamp=None,
        remote_server=None,
        check_only=None,
    ):
        logger.debug("Initializing Config...")
        self.__moves_db = moves_db if moves_db is not None else config_file.MOVES_DB
        self.__ref_timestamp = (
            ref_timestamp if ref_timestamp is not None else config_file.REF_TIMESTAMP
        )
        self.__remote_server = (
            remote_server if remote_server is not None else config_file.REMOTE_SERVER
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
    def remote_server(self):
        """Path to remote server; UNC or symbolic link."""
        return self.__remote_server

    @property
    def check_only(self):
        """Check-only/test mode."""
        return self.__check_only

    def __str__(self):
        text = (
            "<moves_db: {0}, ref_timestamp: {1}, remote_server: {2}, check_only: {3}>"
        )
        text = text.format(
            self.moves_db,
            self.ref_timestamp,
            self.remote_server,
            self.check_only,
        )
        return text
