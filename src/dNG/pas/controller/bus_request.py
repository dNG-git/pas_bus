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

from dNG.data.json_resource import JsonResource
from dNG.pas.plugins.hook import Hook
from dNG.pas.runtime.io_exception import IOException
from dNG.pas.runtime.type_exception import TypeException
from .abstract_request import AbstractRequest
from .bus_response import BusResponse

class BusRequest(AbstractRequest):
#
	"""
"BusRequest" implements an IPC request.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: bus
:since:      v0.1.01
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def __init__(self, handler = None):
	#
		"""
Constructor __init__(BusRequest)

:param handler: IPC client handler

:since: v0.1.01
		"""

		AbstractRequest.__init__(self)

		self.handler = handler
		"""
IPC handler to read the request from.
		"""

		if (self.handler is not None):
		#
			self.parameters = self._get_parameters()
			self.init()
		#
	#

	def execute(self):
	#
		"""
Executes the incoming request.

:since: v0.1.01
		"""

		# pylint: disable=broad-except,star-args

		method = self.get_parameter("method")
		response = self._init_response()

		try:
		#
			params = self.get_parameter("params", { })

			if (self.log_handler is not None): self.log_handler.debug("{0!r} will call {1!s}", self, method, context = "pas_bus")
			if (type(params) != dict): raise TypeException("Parameters given are not provided as dict")
			result = Hook.call(method, **params)

			if (self.log_handler is not None): self.log_handler.debug("{0!r} {1}", self, ("got nothing to return" if (result is None) else "is returning an result"), context = "pas_bus")

			response.set_result(result)
		#
		except Exception as handled_exception:
		#
			if (self.log_handler is not None): self.log_handler.error(handled_exception, context = "pas_bus")
			response.handle_exception(None, handled_exception)
		#

		if (method != "dNG.pas.Status.stop"): self._respond(response)
	#

	def _get_parameters(self):
	#
		"""
Returns parameters for the request read from the IPC client handler.

:return: (dict) Request parameters
:since:  v0.1.01
		"""

		# pylint: disable=protected-access

		_return = { }

		data = self.handler.get_data(256)
		newline_position = data.find("\n")
		message = ""

		if (newline_position > 0):
		#
			data_size = int(data[:newline_position])

			if (data_size > 256):
			#
				message = data[(newline_position + 1):]
				data_size -= (255 - newline_position)
				message += self.handler.get_data(data_size, True)
			#
			else:
			#
				message = data[(newline_position + 1):(newline_position + 1 + data_size)]
				if (len(data) > (newline_position + 1 + data_size)): self.handler._set_data(data[(newline_position + 1 + data_size):])
			#
		#

		if (message == ""): _return['method'] = "dNG.pas.bus.Connection.close"
		else:
		#
			parameters = JsonResource().json_to_data(message)
			if (parameters is not None): _return = parameters
		#

		return _return
	#

	def init(self):
	#
		"""
Do preparations for request handling.

:since: v0.1.01
		"""

		if ("method" not in self.parameters): raise IOException("Invalid bus request received")
	#

	def _init_response(self):
	#
		"""
Initializes the bus response instance.

:return: (object) Response object
:since:  v0.1.01
		"""

		response = BusResponse(self.handler)
		if (self.log_handler is not None): response.set_log_handler(self.log_handler)

		return response
	#

	def is_close_requested(self):
	#
		"""
Returns true if the client wants to close the connection.

:return: (bool) True if close is received
:since:  v0.1.01
		"""

		return (self.get_parameter("method") == "dNG.pas.bus.Connection.close")
	#

	def is_received(self):
	#
		"""
Returns true if a valid IPC request has been received.

:return: (bool) True if requested method is received
:since:  v0.1.01
		"""

		return (self.get_parameter("method") is not None)
	#
#

##j## EOF