# -*- coding: utf-8 -*-
##j## BOF

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

class BusMixin(object):
#
	"""
The "BusMixin" adds typical methods for an IPC aware loader.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: bus
:since:      v0.3.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def __init__(self):
	#
		"""
Constructor __init__(BusMixin)

:since: v0.3.00
		"""

		self.time_started = None
		"""
Timestamp of service initialisation
		"""
	#

	def get_os_pid(self, params = None, last_return = None):
	#
		"""
Returns the OS process ID.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (int) OS process ID; -1 if unknown or unsupported
:since:  v0.3.00
		"""

		pid = (os.getpid() if (hasattr(os, "getpid")) else -1)
		if (pid == 0): pid = -1

		return pid
	#

	def get_time_started(self, params = None, last_return = None):
	#
		"""
Returns the time (timestamp) this service had been initialized.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (int) Unix timestamp
:since:  v0.3.00
		"""

		return self.time_started
	#

	def get_uptime(self, params = None, last_return = None):
	#
		"""
Returns the time in seconds since this service had been initialized.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (int) Uptime in seconds
:since:  v0.3.00
		"""

		return int(floor(time() - self.time_started))
	#

	def _set_time_started(self, timestamp):
	#
		"""
Sets the time (timestamp) this service had been initialized.

:param timestamp: UNIX timestamp

:since: v0.3.00
		"""

		self.time_started = int(timestamp)
	#
#

##j## EOF