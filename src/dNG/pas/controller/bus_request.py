# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.controller.BusRequest
"""
"""n// NOTE
----------------------------------------------------------------------------
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?pas;bus

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
http://www.direct-netware.de/redirect.py?licenses;mpl2
----------------------------------------------------------------------------
#echo(pasBusVersion)#
#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

from dNG.data.json_resource import JsonResource
from dNG.pas.plugins.hooks import Hooks
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
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
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

		if (self.handler != None):
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

		response = self._init_response()

		try:
		#
			method = self.get_parameter("method")
			params = self.get_parameter("params", { })

			if (self.log_handler != None): self.log_handler.debug("pas.bus.Request will call {0!s}".format(method))
			if (type(params) != dict): raise TypeException("Parameters given are not provided as dict")
			result = Hooks.call(method, **params)

			if (result != None):
			#
				if (self.log_handler != None): self.log_handler.debug("pas.bus.Request is returning an result")
				response.set_result(result)
			#
			elif (self.log_handler != None): self.log_handler.debug("pas.bus.Request got nothing to return")
		#
		except Exception as handled_exception:
		#
			if (self.log_handler != None): self.log_handler.error(handled_exception)
			response.handle_exception(None, handled_exception)
		#

		self._respond(response)
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

		if (message != ""):
		#
			parameters = JsonResource().json_to_data(message)
			if (parameters != None): _return = parameters
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
		if (self.log_handler != None): response.set_log_handler(self.log_handler)

		return response
	#

	def is_received(self):
	#
		"""
Returns true if a valid IPC request has been received.

:return: (bool) True if requested method is received
:since:  v0.1.01
		"""

		return (self.get_parameter("method") != None)
	#
#

##j## EOF