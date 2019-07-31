# -*- coding: utf-8 -*-

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?pas;bus

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;mpl2
----------------------------------------------------------------------------
#echo(pasBusVersion)#
#echo(__FILEPATH__)#
"""

from math import floor
from time import time
import os

class CliMixin(object):
    """
The "CliMixin" adds typical methods for an IPC aware CLI application.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: bus
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    def __init__(self):
        """
Constructor __init__(CliMixin)

:since: v1.0.0
        """

        self._time_started_value = None
        """
Timestamp of service initialization
        """
    #

    @property
    def _time_started(self):
        """
Returns the time (timestamp) this service had been initialized.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (int) Unix timestamp
:since:  v1.0.0
        """

        return self._time_started_value
    #

    @_time_started.setter
    def _time_started(self, timestamp):
        """
Sets the time (timestamp) this service had been initialized.

:param timestamp: UNIX timestamp

:since: v1.0.0
        """

        self._time_started_value = int(timestamp)
    #

    def get_os_pid(self, params = None, last_return = None):
        """
Returns the OS process ID.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (int) OS process ID; -1 if unknown or unsupported
:since:  v1.0.0
        """

        pid = (os.getpid() if (hasattr(os, "getpid")) else -1)
        if (pid == 0): pid = -1

        return pid
    #

    def get_time_started(self, params = None, last_return = None):
        """
Returns the time (timestamp) this service had been initialized.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (int) Unix timestamp
:since:  v1.0.0
        """

        return self._time_started
    #

    def get_uptime(self, params = None, last_return = None):
        """
Returns the time in seconds since this service had been initialized.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (int) Uptime in seconds
:since:  v1.0.0
        """

        return int(floor(time() - self._time_started_value))
    #
#
