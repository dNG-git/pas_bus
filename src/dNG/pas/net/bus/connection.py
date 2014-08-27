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

from dNG.pas.controller.bus_request import BusRequest
from dNG.pas.data.binary import Binary
from dNG.pas.net.server.handler import Handler

class Connection(Handler):
#
	"""
"Connection" is an opened conversation with a running IPC aware application.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: bus
:since;      v0.1.01
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def get_data(self, size, force_size = False):
	#
		"""
Returns data read from the socket.

:param size: Bytes to read
:param force_size: True to wait for data until the given size has been
                   received.

:return: (bytes) Data received
:since:  v0.1.00
		"""

		return Binary.str(Handler.get_data(self, size, force_size))
	#

	def _set_data(self, data):
	#
		"""
Sets data returned next time "get_data()" is called. It is placed in front of
the data buffer.

:param data: Data to be buffered

:since: v0.1.00
		"""

		Handler._set_data(self, Binary.utf8_bytes(data))
	#

	def _thread_run(self):
	#
		"""
Active conversation

:since: v0.1.00
		"""

		# pylint: disable=broad-except

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._thread_run()- (#echo(__LINE__)#)", self, context = "pas_bus")
		request = BusRequest(self)

		while (request.is_received() and (not request.is_close_requested())):
		#
			try:
			#
				request.execute()
				request = BusRequest(self)
			#
			except Exception as handled_exception:
			#
				if (self.log_handler != None): self.log_handler.error("#echo(__FILEPATH__)# -Connection._thread_run()- reporting: Error {1!r} occurred", self, handled_exception, context = "pas_bus")
				request = BusRequest()
			#
		#
	#
#

##j## EOF