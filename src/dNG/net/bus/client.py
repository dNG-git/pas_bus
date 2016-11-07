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

from os import path
from select import select
from time import time
import re
import socket

from dNG.data.binary import Binary
from dNG.data.settings import Settings
from dNG.data.dbus.message import Message
from dNG.data.dbus.type_object import TypeObject
from dNG.module.named_loader import NamedLoader
from dNG.runtime.io_exception import IOException

class Client(object):
    """
IPC client for the application.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: bus
:since:      v0.3.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    def __init__(self, app_config_prefix = "pas_bus"):
        """
Constructor __init__(Client)

:since: v0.3.00
        """

        self.connected = False
        """
Connection ready flag
        """
        self.log_handler = NamedLoader.get_singleton("dNG.data.logging.LogHandler", False)
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
            if (listener_mode is None or listener_mode == "unixsocket"):
                listener_mode = socket.AF_UNIX
                if (listener_address is None): listener_address = "/tmp/dNG.pas.socket"
            elif (listener_address is None): listener_address = "localhost:8135"
        except AttributeError:
            listener_mode = socket.AF_INET
            listener_address = "localhost:8135"
        #

        re_result = re.search("^(.+):(\\d+)$", listener_address)

        if (re_result is None):
            listener_host = listener_address
            listener_port = None
        else:
            listener_host = re_result.group(1)
            listener_port = int(re_result.group(2))
        #

        listener_host = Binary.str(listener_host)

        if ((listener_mode == socket.AF_INET) or (listener_mode == socket.AF_INET6)):
            if (self.log_handler is not None): self.log_handler.debug("{0!r} connects to '{1}:{2:d}'", self, listener_host, listener_port, context = "pas_bus")
            listener_data = ( listener_host, listener_port )
        elif (listener_mode == socket.AF_UNIX):
            if (self.log_handler is not None): self.log_handler.debug("{0!r} connects to '{1}'", self, listener_host, context = "pas_bus")
            listener_data = path.normpath(listener_host)
        #

        self.socket = socket.socket(listener_mode, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)
        self.socket.connect(listener_data)

        self.connected = True
    #

    def __del__(self):
        """
Destructor __del__(Client)

:since: v0.3.00
        """

        if (self.connected): self.disconnect()
    #

    def disconnect(self):
        """
Closes an active session.

:since: v0.3.00
        """

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.disconnect()- (#echo(__LINE__)#)", self, context = "pas_bus")

        if (self.connected):
            message = self._get_message_call_template()
            message.set_flags(Message.FLAG_NO_REPLY_EXPECTED)
            message.set_object_member("close")

            self._write_message(message)
            self.connected = False
        #

        if (self.socket is not None):
            self.socket.shutdown(socket.SHUT_RD)
            self.socket.close()

            self.socket = None
        #
    #

    def _get_message_call_template(self):
        """
Returns a D-Bus message prepared to be used for IPC communication.

:return: (object) Message instance
:since:  v0.3.00
        """

        _return = Message(Message.TYPE_METHOD_CALL)
        _return.set_body_signature("a{sv}")
        _return.set_object_interface("de.direct-netware.pas.Bus1")
        _return.set_object_member("call")
        _return.set_object_path("/de/direct-netware/pas/Bus")
        _return.set_serial(1)

        return _return
    #

    def _get_response_message(self):
        """
Returns the IPC response message read from the socket.

:param timeout: Alternative timeout value

:return: (object) Message instance
:since:  v0.3.00
        """

        # pylint: disable=broad-except

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._get_message()- (#echo(__LINE__)#)", self, context = "pas_bus")

        data_unread = 16
        message_data = Binary.BYTES_TYPE()
        message_size = 0
        timeout_time = time() + self.timeout

        while ((data_unread > 0 or message_size == 0) and time() < timeout_time):
            select([ self.socket.fileno() ], [ ], [ ], self.timeout)
            data = self.socket.recv(data_unread)

            if (len(data) > 0):
                message_data += data

                if (message_size < 1):
                    try:
                        message_size = Message.get_marshaled_message_size(message_data)
                        data_unread = (message_size - len(message_data))
                    except IOException: pass
                else: data_unread -= len(data)
            #
        #

        if (message_size == 0): raise IOException("Timeout occurred before message size was calculable")
        elif (len(message_data) < message_size): raise IOException("Timeout occurred before expected message size of {0:d} bytes was received".format(message_size))

        return Message.unmarshal(message_data)
    #

    def request(self, _hook, **kwargs):
        """
Requests the IPC aware application to call the given hook.

:param _hook: Hook
:param args: Parameters

:return: (mixed) Result data; None on error
:since:  v0.3.00
        """

        _hook = Binary.str(_hook)

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.request({1})- (#echo(__LINE__)#)", self, _hook, context = "pas_bus")
        _return = None

        if (not self.connected): raise IOException("Connection already closed")

        request_message = self._get_message_call_template()
        if (_hook == "dNG.pas.Status.stop"): request_message.set_flags(Message.FLAG_NO_REPLY_EXPECTED)

        request_message_body = { "method": _hook }
        if (len(kwargs) > 0): request_message_body['params'] = TypeObject("a{sv}", kwargs)

        request_message.set_body(request_message_body)

        if (not self._write_message(request_message)): raise IOException("Failed to transmit request")

        if (_hook == "dNG.pas.Status.stop"): self.connected = False
        else:
            response_message = self._get_response_message()

            if (((not response_message.is_error()) and (not response_message.is_method_reply()))
                or response_message.get_reply_serial() != 1
                or response_message.get_serial() != 2
               ): raise IOException("IPC response received is invalid")

            if (response_message.is_error()):
                response_body = response_message.get_body()

                raise IOException(Binary.str(response_body)
                                  if (type(response_body) == Binary.BYTES_TYPE) else
                                  response_message.get_error_name()
                                 )
            else: _return = response_message.get_body()
        #

        return _return
    #

    def set_timeout(self, timeout):
        """
Sets the timeout for receiving a IPC message.

:param timeout: Timeout in seconds

:since: v0.3.00
        """

        self.timeout = timeout
    #

    def _write_message(self, message):
        """
Sends a message to the helper application.

:param message: Message to be written

:return: (bool) True on success
:since:  v0.3.00
        """

        # pylint: disable=broad-except

        if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._write_message()- (#echo(__LINE__)#)", self, context = "pas_bus")
        _return = True

        try: self.socket.sendall(message.marshal())
        except Exception as handled_exception:
            if (self.log_handler is not None): self.log_handler.error(handled_exception, "pas_bus")
            _return = False
        #

        return _return
    #
#
