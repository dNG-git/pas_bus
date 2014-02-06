# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.net.bus.Client
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

from os import path
import re
import socket
import time

from dNG.data.json_parser import JsonParser
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
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
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
		self.timeout = int(Settings.get("pas_server_socket_data_timeout", 0))
		"""
Request timeout value
		"""

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
			if (self.log_handler != None): self.log_handler.debug("pas.bus.Client connects to '{0}:{1:d}'".format(listener_host, listener_port))
			listener_data = ( listener_host, listener_port )
		#
		elif (listener_mode == socket.AF_UNIX):
		#
			if (self.log_handler != None): self.log_handler.debug("pas.bus.Client connects to '{0}'".format(listener_host))
			listener_data = path.normpath(listener_host)
		#

		self.socket = socket.socket(listener_mode, socket.SOCK_STREAM)
		self.socket.settimeout(self.timeout)
		self.socket.connect(listener_data)
		if (self.timeout < 1): self.timeout = int(Settings.get("pas_global_socket_data_timeout", 30))

		self.connected = True
	#

	def __del__(self):
	#
		"""
Destructor __del__(Client)

:since: v0.1.00
		"""

		if (self.connected): Client.disconnect(self)
	#

	def disconnect(self):
	#
		"""
Closes an active session.

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -Client.disconnect()- (#echo(__LINE__)#)")

		if (self.connected):
		#
			self.write_message("")
			self.connected = False
		#

		self.socket.shutdown(socket.SHUT_RD)
		self.socket.close()
	#

	def get_message(self):
	#
		"""
Returns data read from the socket.

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -Client.get_message()- (#echo(__LINE__)#)")
		_return = Binary.BYTES_TYPE()

		data = None
		data_size = 0
		force_size = False
		message_size = 256
		timeout_time = (time.time () + self.timeout)

		while ((data == None or (force_size and data_size < message_size)) and time.time() < timeout_time):
		#
			try:
			#
				data = self.socket.recv(message_size)

				if (len(data) > 0):
				#
					if (data_size < 1):
					#
						newline_position = data.find("\n")

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
					#
					else:
					#
						_return += data
						data_size = len(Binary.utf8_bytes(_return))
					#
				#
				else: data = None
			#
			except Exception: _return = ""
		#

		if (_return == None or (force_size and data_size < message_size)): raise IOException("Received data size is smaller than the expected message size of {0:d} bytes".format(message_size))
		return Binary.str(_return)
	#

	def request(self, hook, *args):
	#
		"""
Requests the IPC aware application to call the given hook.

:param hook: Hook
:param args: Parameters

:return: (mixed) Result data; None on error
:since:  v0.1.00
		"""

		hook = Binary.str(hook)

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -Client.request({0}, *args)- (#echo(__LINE__)#)".format(hook))
		_return = None

		json_parser = JsonParser()

		data = json_parser.data2json({ "jsonrpc": "2.0", "method": hook, "params": args, "id": 1 })

		if (self.write_message(data) and hook != "dNG.pas.Status.stop"):
		#
			data = self.get_message()

			if (len(data) > 0):
			#
				data = json_parser.json2data(data)
				if (type(data) == dict and "result" in data): _return = data['result']
			#
		#

		return _return
	#

	def write_message(self, message):
	#
		"""
Sends a message to the helper application.

:param message: Message to be written

:return: (bool) True on success
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -Client.write_message(message)- (#echo(__LINE__)#)")
		_return = True

		message = Binary.utf8_bytes(message)
		message = (Binary.utf8_bytes("{0:d}\n".format(len(message))) + message)

		if (len(message) > 0):
		#
			try: self.socket.sendall(message)
			except Exception as handled_exception:
			#
				if (self.log_handler != None): self.log_handler.error(handled_exception)
				_return = False
			#
		#

		return _return
	#
#

##j## EOF