# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.net.bus.Connection
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

from dNG.pas.controller.bus_request import BusRequest
from dNG.pas.net.server.handler import Handler

class Connection(Handler):
#
	"""
"Connection" is an opened conversation with a running IPC aware application.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: bus
:since;      v0.1.01
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def _thread_run(self):
	#
		"""
Active conversation

:since: v1.0.0
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -Connection._thread_run()- (#echo(__LINE__)#)")
		request = BusRequest(self)

		while (request.is_received()):
		#
			try:
			#
				request.execute()
				request = BusRequest(self)
			#
			except Exception as handled_exception:
			#
				if (self.log_handler != None): self.log_handler.error("#echo(__FILEPATH__)# -Connection._thread_run()- reporting: Error {0!r} occurred".format(handled_exception))
				request = BusRequest()
			#
		#
	#
#

##j## EOF