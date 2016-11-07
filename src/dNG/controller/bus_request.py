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

from dNG.data.dbus.message import Message
from dNG.plugins.hook import Hook
from dNG.plugins.manager import Manager
from dNG.runtime.io_exception import IOException
from dNG.runtime.type_exception import TypeException

from .abstract_request import AbstractRequest
from .bus_response import BusResponse

class BusRequest(AbstractRequest):
    """
"BusRequest" implements an IPC request.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: bus
:since:      v0.3.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    def __init__(self, connection, message_data):
        """
Constructor __init__(BusRequest)

:param connection: IPC connection

:since: v0.3.00
        """

        AbstractRequest.__init__(self)

        self.connection = connection
        """
IPC connection to use
        """
        self.message = None
        """
IPC request message
        """
        self.message_data = message_data
        """
Raw IPC request message data
        """

        self.init()
    #

    def execute(self):
        """
Executes the incoming request.

:since: v0.3.00
        """

        # pylint: disable=broad-except,star-args

        method = self.get_parameter("method")
        response = self._init_response()

        try:
            params = self.get_parameter("params", { })

            if (self.log_handler is not None): self.log_handler.debug("{0!r} will call {1!s}", self, method, context = "pas_bus")
            if (not isinstance(params, dict)): raise TypeException("Parameters given are not provided as dict")

            result = (Manager.reload_plugins(**params)
                      if (method == "dNG.pas.Plugins.reload") else
                      Hook.call(method, **params)
                     )

            if (self.log_handler is not None): self.log_handler.debug("{0!r} {1}", self, ("got nothing to return" if (result is None) else "is returning an result"), context = "pas_bus")
            if (response is not None): response.set_result(result)
        except Exception as handled_exception:
            if (self.log_handler is not None): self.log_handler.error(handled_exception, context = "pas_bus")
            if (response is not None): response.handle_exception(None, handled_exception)
        #

        if (response is not None): self._respond(response)
    #

    def init(self):
        """
Do preparations for request handling.

:since: v0.3.00
        """

        self.message = Message.unmarshal(self.message_data)
        self.message_data = None

        if (not self.message.is_method_call()
            or self.message.get_serial() != 1
            or self.message.get_object_interface() != "de.direct-netware.pas.Bus1"
            or self.message.get_object_path() != "/de/direct-netware/pas/Bus"
            or self.message.get_object_member() not in ( "call", "close" )
           ): raise IOException("IPC request received is invalid")

        message_body = self.message.get_body()
        if (type(message_body) is dict): self.parameters = message_body
    #

    def _init_response(self):
        """
Initializes the bus response instance.

:return: (object) Response object
:since:  v0.3.00
        """

        _return = None

        if (self.message.get_flags() & Message.FLAG_NO_REPLY_EXPECTED != Message.FLAG_NO_REPLY_EXPECTED):
            _return = BusResponse(self.connection)
            if (self.log_handler is not None): _return.set_log_handler(self.log_handler)
        #

        return _return
    #

    def is_close_requested(self):
        """
Returns true if the client wants to close the connection.

:return: (bool) True if close is received
:since:  v0.3.00
        """

        return (self.message.get_object_member() == "close")
    #
#
