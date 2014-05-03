# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.controller.BusResponse
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
from dNG.pas.data.binary import Binary
from .abstract_response import AbstractResponse

class BusResponse(AbstractResponse):
#
	"""
Bus response sends the result for one executed bus result.

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
Constructor __init__(BusResponse)

:param handler: IPC client handler

:since: v0.1.01
		"""

		AbstractResponse.__init__(self)

		self.handler = handler
		"""
IPC handler to send the result to.
		"""
		self.message = None
		"""
Result message to be send
		"""
	#

	def handle_critical_error(self, message):
	#
		"""
"handle_critical_error()" is called to send a critical error message.

:param message: Message (will be translated if possible)

:since: v0.1.01
		"""

		self.handle_error(message)
	#

	def handle_error(self, message):
	#
		"""
"handle_error()" is called to send a error message.

:param message: Message (will be translated if possible)

:since: v0.1.01
		"""

		self.message = JsonResource().data_to_json({
			"jsonrpc": "2.0",
			"error": {
				"code": -32500,
				"message": message
			},
			"id": 1
		})
	#

	def handle_exception(self, message, exception):
	#
		"""
"handle_exception()" is called if an exception occurs and should be
send.

:param message: Message (will be translated if possible)
:param exception: Original exception or formatted string (should be shown in
                  dev mode)

:since: v0.1.01
		"""

		self.message = JsonResource().data_to_json({
			"jsonrpc": "2.0",
			"error": {
				"code": -32500,
				"message": ("{0!r}".format(exception) if (message == None) else message)
			},
			"id": 1
		})
	#

	def send(self):
	#
		"""
Sends the prepared response.

:since: v0.1.01
		"""

		message = Binary.str(self.message)
		bytes_unwritten = len(Binary.utf8_bytes(message))

		message = "{0:d}\n{1}".format(bytes_unwritten, message)
		self.handler.write_data(message)
	#

	def set_result(self, result):
	#
		"""
Sets the encoded message to be send based on the result given.

:param result: Result data

:since: v0.1.01
		"""

		self.message = JsonResource().data_to_json({ "jsonrpc": "2.0", "result": result, "id": 1 })
	#

#

##j## EOF