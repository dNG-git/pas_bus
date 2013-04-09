# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.net.bus.client
"""
"""n// NOTE
----------------------------------------------------------------------------
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?pas;http;core

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
import json, re, socket, time

from dNG.pas.data.settings import direct_settings
from dNG.pas.module.named_loader import direct_named_loader
from dNG.pas.pythonback import *

class direct_client(object):
#
	"""
Client for the "direct_server" infrastructure.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: bus
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def __init__(self, app_config_prefix = "pas_bus"):
	#
		"""
Constructor __init__(direct_client)

:since: v0.1.00
		"""

		self.connected = False
		"""
Connection ready flag
		"""
		self.log_handler = direct_named_loader.get_singleton("dNG.pas.data.logging.log_handler", False)
		"""
The log_handler is called whenever debug messages should be logged or errors
happened.
		"""
		self.socket = None
		"""
Socket instance
		"""
		self.timeout = int(direct_settings.get("pas_server_socket_data_timeout", 30))
		"""
Request timeout value
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -client.__init__()- (#echo(__LINE__)#)")

		listener_address = direct_settings.get("{0}_listener_address".format(app_config_prefix))
		listener_mode = direct_settings.get("{0}_listener_mode".format(app_config_prefix))

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
		except:
		#
			listener_mode = socket.AF_INET
			listener_address = "localhost:8135"
		#

		re_result = re.search("^(.+?):(\d+)$", listener_address)

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

		listener_host = direct_str(listener_host)

		if ((listener_mode == socket.AF_INET) or (listener_mode == socket.AF_INET6)):
		#
			if (self.log_handler != None): self.log_handler.debug("pas.bus client connects to '{0}:{1:d}'".format(listener_host, listener_port))
			listener_data = ( listener_host, listener_port )
		#
		elif (listener_mode == socket.AF_UNIX):
		#
			if (self.log_handler != None): self.log_handler.debug("pas.bus client connects to '{0}'".format(listener_host))
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
Destructor __del__(direct_client)

:since: v0.1.00
		"""

		if (self.connected): self.disconnect()
		if (self.log_handler != None): self.log_handler.return_instance()
	#

	def disconnect(self):
	#
		"""
Closes an active session.

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -client.disconnect()- (#echo(__LINE__)#)")

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

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -client.get_message()- (#echo(__LINE__)#)")
		var_return = direct_bytes("")

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
								var_return = data[(newline_position + 1):]
								message_size -= (255 - newline_position)
								force_size = True
							#
							else: var_return = data[(newline_position + 1):(newline_position + 1 + message_size)]
						#
					#
					else:
					#
						var_return += data
						data_size = len(direct_bytes(var_return))
					#
				#
				else: data = None
			#
			except: var_return = ""
		#

		if (var_return != None and ((not force_size) or message_size <= data_size)): return direct_str(var_return)
		else: raise OSError("get_message({0:d})".format(message_size), 5)
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

		hook = direct_str(hook)

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -client.request({0}, *args)- (#echo(__LINE__)#)".format(hook))
		var_return = None

		data = json.dumps({ "jsonrpc": "2.0", "method": hook, "params": args, "id": 1 })

		if (self.write_message(data) and hook != "dNG.pas.status.shutdown"):
		#
			data = self.get_message()

			if (len(data) > 0):
			#
				data = json.loads(data)
				if (type(data) == dict and "result" in data): var_return = data['result']
			#
		#

		return var_return
	#

	def write_message(self, message):
	#
		"""
Sends a message to the helper application.

:param message: Message to be written

:return: (bool) True on success
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -client.write_message(message)- (#echo(__LINE__)#)")
		var_return = True

		message = direct_bytes(message)
		message = (direct_bytes("{0:d}\n".format(len(message))) + message)

		if (len(message) > 0):
		#
			try: self.socket.sendall(message)
			except Exception as handled_exception:
			#
				if (self.log_handler != None): self.log_handler.error(handled_exception)
				var_return = False
			#
		#

		return var_return
	#
#

##j## EOF