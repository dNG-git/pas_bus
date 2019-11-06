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
from time import time
import re
import socket

from dpt_module_loader import NamedClassLoader
from dpt_runtime.binary import Binary
from dpt_runtime.descriptor_selector import DescriptorSelector
from dpt_runtime.io_exception import IOException
from dpt_settings import Settings
from pas_dbus import Message, TypeObject

class Client(object):
    """
IPC client for the application.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: bus
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    __slots__ = [ "__weakref__", "_connected", "_log_handler", "socket", "_timeout" ]
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """

    def __init__(self, app_config_prefix = "pas_bus"):
        """
Constructor __init__(Client)

:since: v1.0.0
        """

        self._connected = False
        """
Connection ready flag
        """
        self._log_handler = NamedClassLoader.get_singleton("dpt_logging.LogHandler", False)
        """
The LogHandler is called whenever debug messages should be logged or errors
happened.
        """
        self.socket = None
        """
Socket instance
        """
        self._timeout = int(Settings.get("pas_bus_socket_data_timeout", 0))
        """
Request timeout value
        """

        if (self._timeout < 1): self._timeout = int(Settings.get("global_client_socket_data_timeout", 0))
        if (self._timeout < 1): self._timeout = int(Settings.get("global_socket_data_timeout", 30))

        listener_address = Settings.get("{0}_listener_address".format(app_config_prefix))
        listener_mode = Settings.get("{0}_listener_mode".format(app_config_prefix))

        if (listener_mode == "ipv6"): listener_mode = socket.AF_INET6
        elif (listener_mode == "ipv4"): listener_mode = socket.AF_INET

        try:
            if (listener_mode is None or listener_mode == "unixsocket"):
                listener_mode = socket.AF_UNIX
                if (listener_address is None): listener_address = path.join(Settings.get("path_data"), "pas-bus.socket")
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
            if (self._log_handler is not None): self._log_handler.debug("{0!r} connects to '{1}:{2:d}'", self, listener_host, listener_port, context = "pas_bus")
            listener_data = ( listener_host, listener_port )
        elif (listener_mode == socket.AF_UNIX):
            if (self._log_handler is not None): self._log_handler.debug("{0!r} connects to '{1}'", self, listener_host, context = "pas_bus")
            listener_data = path.normpath(listener_host)
        #

        self.socket = socket.socket(listener_mode, socket.SOCK_STREAM)
        self.socket.settimeout(self._timeout)
        self.socket.connect(listener_data)

        self._connected = True
    #

    def __del__(self):
        """
Destructor __del__(Client)

:since: v1.0.0
        """

        if (self.is_connected): self.disconnect()
    #

    @property
    def is_connected(self):
        """
Returns true if the connection is ready.

:return: (bool) True if connected
:since:  v1.0.0
        """

        return self._connected
    #

    @property
    def timeout(self):
        """
Returns the timeout for receiving a IPC message.

:return: (float) Timeout in seconds
:since:  v1.0.0
        """

        return self._timeout
    #

    @timeout.setter
    def timeout(self, timeout):
        """
Sets the timeout for receiving a IPC message.

:param timeout: Timeout in seconds

:since: v1.0.0
        """

        self._timeout = timeout
        self.socket.settimeout(self._timeout)
    #

    def disconnect(self):
        """
Closes an active session.

:since: v1.0.0
        """

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -{0!r}.disconnect()- (#echo(__LINE__)#)", self, context = "pas_bus")

        if (self.is_connected):
            message = self._get_message_call_template()
            message.flags = Message.FLAG_NO_REPLY_EXPECTED
            message.object_member = "close"

            self._write_message(message)
            self._connected = False
        #

        if (self.socket is not None):
            self.socket.close()
            self.socket = None
        #
    #

    def _get_message_call_template(self):
        """
Returns a D-Bus message prepared to be used for IPC communication.

:return: (object) Message instance
:since:  v1.0.0
        """

        _return = Message(Message.TYPE_METHOD_CALL)
        _return.body_signature = "a{sv}"
        _return.object_interface = "de.direct-netware.pas.Bus1"
        _return.object_member = "call"
        _return.object_path = "/de/direct-netware/pas/Bus"
        _return.serial = 1

        return _return
    #

    def _get_response_message(self):
        """
Returns the IPC response message read from the socket.

:param timeout: Alternative timeout value

:return: (object) Message instance
:since:  v1.0.0
        """

        # pylint: disable=broad-except

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -{0!r}._get_message()- (#echo(__LINE__)#)", self, context = "pas_bus")

        data_unread = 16
        message_data = Binary.BYTES_TYPE()
        message_size = 0
        selector = DescriptorSelector([ self.socket.fileno() ])
        timeout_time = time() + self.timeout

        while ((data_unread > 0 or message_size == 0) and time() < timeout_time):
            if (len(selector.select(self.timeout, False)[0]) < 1): raise IOException("Failed to receive data")
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
:since:  v1.0.0
        """

        _hook = Binary.str(_hook)

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -{0!r}.request({1})- (#echo(__LINE__)#)", self, _hook, context = "pas_bus")
        _return = None

        if (not self.is_connected): raise IOException("Connection already closed")

        request_message = self._get_message_call_template()
        if (_hook == "pas.Application.stop"): request_message.flags = Message.FLAG_NO_REPLY_EXPECTED

        request_message_body = { "method": _hook }
        if (len(kwargs) > 0): request_message_body['params'] = TypeObject("a{sv}", kwargs)

        request_message.body = request_message_body

        if (not self._write_message(request_message)): raise IOException("Failed to transmit request")

        if (_hook == "pas.Application.stop"):
            self._connected = False
            self.disconnect()
        else:
            response_message = self._get_response_message()

            if (((not response_message.is_error) and (not response_message.is_method_reply))
                or response_message.reply_serial != 1
                or response_message.serial != 2
               ): raise IOException("IPC response received is invalid")

            if (response_message.is_error):
                response_body = response_message.body

                raise IOException(Binary.str(response_body)
                                  if (type(response_body) == Binary.BYTES_TYPE) else
                                  response_message.error_name
                                 )
            else: _return = response_message.body
        #

        return _return
    #

    def _write_message(self, message):
        """
Sends a message to the helper application.

:param message: Message to be written

:return: (bool) True on success
:since:  v1.0.0
        """

        # pylint: disable=broad-except

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -{0!r}._write_message()- (#echo(__LINE__)#)", self, context = "pas_bus")
        _return = True

        try: self.socket.sendall(message.marshal())
        except Exception as handled_exception:
            if (self._log_handler is not None): self._log_handler.error(handled_exception, "pas_bus")
            _return = False
        #

        return _return
    #
#
