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