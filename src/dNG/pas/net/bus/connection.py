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
from dNG.pas.data.dbus.message import Message
from dNG.pas.net.server.handler import Handler
from dNG.pas.runtime.io_exception import IOException

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

	def _thread_run(self):
	#
		"""
Active conversation

:since: v0.1.00
		"""

		# pylint: disable=broad-except

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._thread_run()- (#echo(__LINE__)#)", self, context = "pas_bus")

		data = Binary.BYTES_TYPE()

		while (self.socket is not None):
		#
			try:
			#
				data += self.get_data(16)
				request_message_size = 0

				try: request_message_size = Message.get_marshaled_message_size(data)
				except IOException: pass

				if (request_message_size > 0 and len(data) >= request_message_size):
				#
					request_message_data = data[:request_message_size]

					self._set_data(data[request_message_size:])
					data = Binary.BYTES_TYPE()

					request = BusRequest(self, request_message_data)

					if (request.is_close_requested()): self.stop()
					else: request.execute()
				#
			#
			except Exception as handled_exception:
			#
				if (self.log_handler is not None): self.log_handler.error("#echo(__FILEPATH__)# -Connection._thread_run()- reporting: Error {1!r} occurred", self, handled_exception, context = "pas_bus")
			#
		#
	#
#

##j## EOF