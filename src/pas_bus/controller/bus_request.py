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

from dpt_plugins import Hook
from dpt_plugins import Manager
from dpt_runtime.io_exception import IOException
from dpt_runtime.type_exception import TypeException
from pas_dbus.message import Message
from pas_server.controller import AbstractRequest

from .bus_response import BusResponse

class BusRequest(AbstractRequest):
    """
"BusRequest" implements an IPC request.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: bus
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    def __init__(self):
        """
Constructor __init__(BusRequest)

:since: v1.0.0
        """

        AbstractRequest.__init__(self)

        self._connection = None
        """
IPC connection to use
        """
        self._message = None
        """
IPC request message
        """
    #

    @property
    def is_close_requested(self):
        """
Returns true if the client wants to close the connection.

:return: (bool) True if close is received
:since:  v1.0.0
        """

        return (self.message.object_member == "close")
    #

    @property
    def message(self):
        """
Returns IPC request message.

:return: (object) IPC request message
:since:  v1.0.0
        """

        if (self._message is None): raise IOException("No IPC request message available")
        return self._message
    #

    def execute(self):
        """
Executes the incoming request.

:since: v1.0.0
        """

        # pylint: disable=broad-except

        method = self.get_parameter("method")
        response = self._new_response()

        try:
            params = self.get_parameter("params", { })

            if (self._log_handler is not None): self._log_handler.debug("{0!r} will call {1!s}", self, method, context = "pas_bus")
            if (not isinstance(params, dict)): raise TypeException("Parameters given are not provided as dict")

            result = (Manager.reload_plugins(**params)
                      if (method == "dNG.pas.Plugins.reload") else
                      Hook.call(method, **params)
                     )

            if (isinstance(result, Exception)): raise result

            if (self._log_handler is not None): self._log_handler.debug("{0!r} {1}", self, ("got nothing to return" if (result is None) else "is returning an result"), context = "pas_bus")
            if (response is not None): response.result = result
        except Exception as handled_exception:
            if (self._log_handler is not None): self._log_handler.error(handled_exception, context = "pas_bus")
            if (response is not None): response.handle_exception(None, handled_exception)
        #

        if (response is not None): self._respond(response)
    #

    def init(self, connection_or_request):
        """
Initializes default values from the a connection or request instance.

:param connection_or_request: Connection or request instance

:since: v1.0.0
        """

        self._connection = connection_or_request
        self._message = Message.unmarshal(connection_or_request.request_message_data)

        if (not self._message.is_method_call
            or self._message.serial != 1
            or self._message.object_interface != "de.direct-netware.pas.Bus1"
            or self._message.object_path != "/de/direct-netware/pas/Bus"
            or self._message.object_member not in ( "call", "close" )
           ): raise IOException("IPC request received is invalid")

        message_body = self._message.body
        if (type(message_body) is dict): self._parameters = message_body
    #

    def _new_response(self):
        """
Initializes the matching response instance.

:return: (object) Response object
:since:  v1.0.0
        """

        _return = None

        if (not (self.message.flags & Message.FLAG_NO_REPLY_EXPECTED)):
            _return = BusResponse(self._connection)
            if (self._log_handler is not None): _return.log_handler = self._log_handler
        #

        return _return
    #
#
