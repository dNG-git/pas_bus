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

# pylint: disable=import-error, no-name-in-module

from dNG.data.dbus.message import Message

from .abstract_response import AbstractResponse

class BusResponse(AbstractResponse):
    """
Bus response sends the result for one executed bus result.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: bus
:since:      v0.3.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    def __init__(self, connection):
        """
Constructor __init__(BusResponse)

:param handler: IPC client handler

:since: v0.3.00
        """

        AbstractResponse.__init__(self)

        self.connection = connection
        """
IPC connection to send the result to.
        """
        self.message = Message()
        """
Result message to be send
        """
    #

    def handle_critical_error(self, message):
        """
"handle_critical_error()" is called to send a critical error message.

:param message: Message (will be translated if possible)

:since: v0.3.00
        """

        self.handle_error(message)
    #

    def handle_error(self, message):
        """
"handle_error()" is called to send a error message.

:param message: Message (will be translated if possible)

:since: v0.3.00
        """

        self.message.set_type(Message.TYPE_ERROR)
        self.message.set_error_name("de.direct-netware.pas.Bus.Error")
        self.message.set_body(message)
    #

    def handle_exception(self, message, exception):
        """
"handle_exception()" is called if an exception occurs and should be
send.

:param message: Message (will be translated if possible)
:param exception: Original exception or formatted string (should be shown in
                  dev mode)

:since: v0.3.00
        """

        self.handle_error("{0!r}".format(exception)
                          if (message is None) else
                          message
                         )
    #

    def send(self):
        """
Sends the prepared response.

:since: v0.3.00
        """

        self.message.set_reply_serial(1)
        self.connection.write_data(self.message.marshal(2))
    #

    def set_result(self, result):
        """
Sets the encoded message to be send based on the result given.

:param result: Result data

:since: v0.3.00
        """

        self.message.set_type(Message.TYPE_METHOD_REPLY)
        if (result is not None): self.message.set_body(result)
    #
#
