# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.net.bus.server
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

import re, socket

from dNG.pas.data.settings import direct_settings
from dNG.pas.net.server.dispatcher import direct_dispatcher
from .request import direct_request

class direct_server(direct_dispatcher):
#
	"""
"direct_server" is responsible to provide an IPC aware bus.

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
Constructor __init__(direct_server)

@since v0.1.00
		"""

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

		listener_socket = direct_dispatcher.prepare_socket(listener_mode, listener_host, listener_port)

		listener_max_actives = int(direct_settings.get("{0}_listener_actives_max".format(app_config_prefix), 100))
		direct_dispatcher.__init__(self, listener_socket, direct_request, listener_max_actives)
	#
#

##j## EOF