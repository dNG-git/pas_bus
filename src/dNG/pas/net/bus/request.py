# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.net.bus.Request
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

import json

from dNG.pas.data.binary import Binary
from dNG.pas.net.server.handler import Handler
from dNG.pas.plugins.hooks import Hooks

class Request(Handler):
#
	"""
"Request" is an opened conversation with a running IPC aware application.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: bus
:since;      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def get_message(self):
	#
		"""
Read an expected message from the socket.

:return: (str) Message; Empty string on error
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -Request.get_message()- (#echo(__LINE__)#)")

		try:
		#
			message = self.get_data(256)
			newline_position = message.find("\n")
			_return = ""

			if (newline_position > 0):
			#
				message_size = int(message[:newline_position])

				if (message_size > 256):
				#
					_return = message[(newline_position + 1):]
					message_size -= (255 - newline_position)
					_return += self.get_data(message_size, True)
				#
				else:
				#
					_return = message[(newline_position + 1):(newline_position + 1 + message_size)]
					if (len(message) > (newline_position + 1 + message_size)): self._set_data(message[(newline_position + 1 + message_size):])
				#
			#
		#
		except EOFError: _return = ""

		return _return
	#

	def _thread_run(self):
	#
		"""
Active conversation

:since: v1.0.0
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -Request._thread_run()- (#echo(__LINE__)#)")
		message = self.get_message()

		while (len(message) > 0):
		#
			try:
			#
				data = json.loads(message)
				if (self.log_handler != None): self.log_handler.debug("pas.bus.Request will call {0!s}".format(data['method']))

				result = Hooks.call(data['method'], **data)

				if (result != None):
				#
					if (self.log_handler != None): self.log_handler.debug("pas.bus.Request is returning an result")
					result = json.dumps({ "jsonrpc": "2.0", "result": result, "id": 1 })
				#
				elif (self.log_handler != None): self.log_handler.debug("pas.bus.Request got nothing to return")

				if (data['method'] == "dNG.pas.Status.stop"):
				#
					if (self.log_handler != None): self.log_handler.info("pas.bus.Request received stop (shutdown) request")
					message = ""
					self.server.stop()
				#
				elif (result == None or self.write_message(result)): message = self.get_message()
				else: message = ""
			#
			except Exception as handled_exception:
			#
				if (self.log_handler != None): self.log_handler.error("#echo(__FILEPATH__)# -Request._thread_run()- reporting: Error {0!r} occurred in message {1}".format(handled_exception, message))
				message = ""
			#
		#
	#

	def write_message(self, message):
	#
		"""
Write a message to the socket.

:param message: Message

:return: (bool) True on success
:since:  v1.0.0
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -Request.write_message(message)- (#echo(__LINE__)#)")
		_return = True

		message = Binary.str(message)
		bytes_unwritten = len(Binary.utf8_bytes(message))

		try:
		#
			message = "{0:d}\n{1}".format(bytes_unwritten, message)
			self.write_data(message)
		#
		except Exception: _return = False

		return _return
	#
#

##j## EOF