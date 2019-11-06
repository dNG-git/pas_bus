# -*- coding: utf-8 -*-

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

from dpt_runtime.binary import Binary
from dpt_runtime.io_exception import IOException
from pas_dbus import Message
from pas_server.controller import AbstractThreadDispatchedConnection
from pas_server.shutdown_exception import ShutdownException

from .bus_request import BusRequest

class BusConnection(AbstractThreadDispatchedConnection):
    """
"BusConnection" is an opened conversation with a running IPC aware application.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: bus
:since;      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    __slots__ = [ "_request_message_data" ]
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """

    def __init__(self):
        """
Constructor __init__(BusConnection)

:since: v1.0.0
        """

        AbstractThreadDispatchedConnection.__init__(self)

        self._request_message_data = None
        """
Raw IPC request message data
        """
    #

    @property
    def request_message_data(self):
        """
Returns the pending, raw IPC request message data.

:return: (bytes) Raw IPC request message data
:since:  v1.0.0
        """

        if (self._request_message_data is None): raise IOException("No IPC request message data available")

        _return = self._request_message_data
        self._request_message_data = None

        return _return
    #

    def _thread_run(self):
        """
Handles the active, threaded connection.

:since: v1.0.0
        """

        # pylint: disable=broad-except

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -{0!r}._thread_run()- (#echo(__LINE__)#)", self, context = "pas_bus")

        data = Binary.BYTES_TYPE()
        request_message_size = 0

        while (self._socket is not None):
            try:
                if (len(data) > 0): data += self.get_data(4096)
                else: data = self.get_data(16, True)

                if (request_message_size == 0):
                    try: request_message_size = Message.get_marshaled_message_size(data)
                    except IOException: pass
                #

                if (0 < request_message_size <= len(data)):
                    self._request_message_data = data[:request_message_size]

                    self._set_data(data[request_message_size:])
                    data = Binary.BYTES_TYPE()
                    request_message_size = 0

                    request = BusRequest()
                    request.init(self)

                    if (request.is_close_requested): self.stop()
                    else:
                        # Stop handler on shutdown request immediately as well
                        if (request.get_parameter("method") == "pas.Application.stop"): self.stop()
                        request.execute()
                    #
                #
            except ShutdownException: raise
            except Exception as handled_exception:
                if (self._log_handler is not None): self._log_handler.error("#echo(__FILEPATH__)# -bus_connection._thread_run()- reporting: Error {1!r} occurred", self, handled_exception, context = "pas_bus")
            #
        #
    #
#
