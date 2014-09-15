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

from os import path
from select import select
from time import time
import re
import socket

from dNG.data.json_resource import JsonResource
from dNG.pas.data.binary import Binary
from dNG.pas.data.settings import Settings
from dNG.pas.module.named_loader import NamedLoader
from dNG.pas.runtime.io_exception import IOException

class Client(object):
#
	"""
IPC client for the application.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: bus
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	BINARY_NEWLINE = Binary.utf8_bytes("\n")
	"""
Newline character byte encoded
	"""

	def __init__(self, app_config_prefix = "pas_bus"):
	#
		"""
Constructor __init__(Client)

:since: v0.1.00
		"""

		self.connected = False
		"""
Connection ready flag
		"""
		self.log_handler = NamedLoader.get_singleton("dNG.pas.data.logging.LogHandler", False)
		"""
The LogHandler is called whenever debug messages should be logged or errors
happened.
		"""
		self.socket = None
		"""
Socket instance
		"""
		self.timeout = int(Settings.get("pas_bus_socket_data_timeout", 0))
		"""
Request timeout value
		"""

		if (self.timeout < 1): self.timeout = int(Settings.get("pas_global_client_socket_data_timeout", 0))
		if (self.timeout < 1): self.timeout = int(Settings.get("pas_global_socket_data_timeout", 30))

		listener_address = Settings.get("{0}_listener_address".format(app_config_prefix))
		listener_mode = Settings.get("{0}_listener_mode".format(app_config_prefix))

		if (listener_mode == "ipv6"): listener_mode = socket.AF_INET6
		elif (listener_mode == "ipv4"): listener_mode = socket.AF_INET

		try:
		#
			if (listener_mode == None or listener_mode == "unixsocket"):
			#
				listener_mode = socket.AF_UNIX
				if (listener_address == None): listener_address = "/tmp/dNG.pas.socket"
			#
			elif (listener_address == None): listener_address = "localhost:8135"
		#
		except AttributeError:
		#
			listener_mode = socket.AF_INET
			listener_address = "localhost:8135"
		#

		re_result = re.search("^(.+):(\\d+)$", listener_address)

		if (re_result == None):
		#
			listener_host = listener_address
			listener_port = None
		#
		else:
		#
			listener_host = re_result.group(1)
			listener_port = int(re_result.group(2))
		#

		listener_host = Binary.str(listener_host)

		if ((listener_mode == socket.AF_INET) or (listener_mode == socket.AF_INET6)):
		#
			if (self.log_handler != None): self.log_handler.debug("{0!r} connects to '{1}:{2:d}'", self, listener_host, listener_port, context = "pas_bus")
			listener_data = ( listener_host, listener_port )
		#
		elif (listener_mode == socket.AF_UNIX):
		#
			if (self.log_handler != None): self.log_handler.debug("{0!r} connects to '{1}'", self, listener_host, context = "pas_bus")
			listener_data = path.normpath(listener_host)
		#

		self.socket = socket.socket(listener_mode, socket.SOCK_STREAM)
		self.socket.settimeout(self.timeout)
		self.socket.connect(listener_data)

		self.connected = True
	#

	def __del__(self):
	#
		"""
Destructor __del__(Client)

:since: v0.1.00
		"""

		if (self.connected): self.disconnect()
	#

	def disconnect(self):
	#
		"""
Closes an active session.

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.disconnect()- (#echo(__LINE__)#)", self, context = "pas_bus")

		if (self.connected):
		#
			self._write_message("")
			self.connected = False
		#

		if (self.socket != None):
		#
			self.socket.shutdown(socket.SHUT_RD)
			self.socket.close()

			self.socket = None
		#
	#

	def _get_message(self):
	#
		"""
Returns data read from the socket.

:param timeout: Alternative timeout value

:return: (str) IPC message
:since:  v0.1.00
		"""

		# pylint: disable=broad-except

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._get_message()- (#echo(__LINE__)#)", self, context = "pas_bus")
		_return = Binary.BYTES_TYPE()

		data = None
		data_size = 0
		force_size = False
		message_size = 256
		timeout_time = time() + self.timeout

		while ((data == None or (force_size and data_size < message_size)) and time() < timeout_time):
		#
			select([ self.socket.fileno() ], [ ], [ ], self.timeout)
			data = self.socket.recv(message_size)

			if (len(data) > 0):
			#
				if (data_size < 1):
				#
					newline_position = data.find(Client.BINARY_NEWLINE)

					if (newline_position > 0):
					#
						message_size = int(data[:newline_position])

						if (message_size > 256):
						#
							_return = data[(newline_position + 1):]
							message_size -= (255 - newline_position)
							force_size = True
						#
						else: _return = data[(newline_position + 1):(newline_position + 1 + message_size)]
					#
					else: raise IOException("No message size value in stream detected")
				#
				else: _return += data

				data_size = len(Binary.bytes(_return))
			#
			else: data = None
		#

		if (force_size and data_size < message_size): raise IOException("Received data size is smaller than the expected message size of {0:d} bytes".format(message_size))
		return Binary.raw_str(_return)
	#

	def request(self, _hook, **kwargs):
	#
		"""
Requests the IPC aware application to call the given hook.

:param _hook: Hook
:param args: Parameters

:return: (mixed) Result data; None on error
:since:  v0.1.00
		"""

		_hook = Binary.str(_hook)

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.request({1})- (#echo(__LINE__)#)", self, _hook, context = "pas_bus")
		_return = None

		if (not self.connected): raise IOException("Connection already closed")

		json_resource = JsonResource()
		raw_request_data = json_resource.data_to_json({ "jsonrpc": "2.0", "method": _hook, "params": kwargs, "id": 1 })

		if (not self._write_message(raw_request_data)): raise IOException("Failed to transmit request")
		elif (_hook == "dNG.pas.Status.stop"): self.disconnect()
		else:
		#
			raw_response_data = self._get_message()

			if (len(raw_response_data) > 0):
			#
				response = json_resource.json_to_data(raw_response_data)

				if (type(response) == dict):
				#
					if ("error" in response): raise IOException(response['error']['message'])
					elif ("result" in response): _return = response['result']
				#
			#
		#

		return _return
	#

	def set_timeout(self, timeout):
	#
		"""
Sets the timeout for receiving a IPC message.

:param timeout: Timeout in seconds

:since: v0.1.01
		"""

		self.timeout = timeout
	#

	def _write_message(self, message):
	#
		"""
Sends a message to the helper application.

:param message: Message to be written

:return: (bool) True on success
:since:  v0.1.00
		"""

		# pylint: disable=broad-except

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._write_message()- (#echo(__LINE__)#)", self, context = "pas_bus")
		_return = True

		message = Binary.utf8_bytes(message)
		message = (Binary.utf8_bytes("{0:d}\n".format(len(message))) + message)

		if (len(message) > 0):
		#
			try: self.socket.sendall(message)
			except Exception as handled_exception:
			#
				if (self.log_handler != None): self.log_handler.error(handled_exception, "pas_bus")
				_return = False
			#
		#

		return _return
	#
#

##j## EOF