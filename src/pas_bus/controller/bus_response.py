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

from pas_dbus.message import Message
from pas_server.controller import AbstractResponse

class BusResponse(AbstractResponse):
    """
Bus response sends the result for one executed bus result.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: bus
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    __slots__ = [ "_connection", "_message" ]
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """

    def __init__(self, connection):
        """
Constructor __init__(BusResponse)

:param connection: IPC client connection

:since: v1.0.0
        """

        AbstractResponse.__init__(self)

        self._connection = connection
        """
IPC connection to send the result to.
        """
        self._message = Message()
        """
Result message to be send
        """

        self.supported_features['dict_result_data'] = True
    #

    @property
    def result(self):
        """
Returns the encoded message to be send.

:return: (str) Result data
:since:  v1.0.0
        """

        return self._message.body
    #

    @result.setter
    def result(self, result):
        """
Sets the encoded message to be send based on the result given.

:param result: Result data

:since: v1.0.0
        """

        self._message.type = Message.TYPE_METHOD_REPLY
        if (result is not None): self._message.body = result
    #

    def handle_critical_error(self, message):
        """
"handle_critical_error()" is called to send a critical error message.

:param message: Message (will be translated if possible)

:since: v1.0.0
        """

        self.handle_error(message)
    #

    def handle_error(self, message):
        """
"handle_error()" is called to send a error message.

:param message: Message (will be translated if possible)

:since: v1.0.0
        """

        self._message.error_name = "de.direct-netware.pas.Bus.Error"
        self._message.body = message
    #

    def handle_exception(self, message, exception):
        """
"handle_exception()" is called if an exception occurs and should be
send.

:param message: Message (will be translated if possible)
:param exception: Original exception or formatted string (should be shown in
                  dev mode)

:since: v1.0.0
        """

        self.handle_error("{0!r}".format(exception)
                          if (message is None) else
                          message
                         )
    #

    def send(self):
        """
Sends the prepared response.

:since: v1.0.0
        """

        self._message.reply_serial = 1
        self._connection.write_data(self._message.marshal(2))
    #
#
