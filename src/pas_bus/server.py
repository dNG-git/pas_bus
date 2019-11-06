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
import re
import socket

from dpt_settings import Settings
from pas_server import Dispatcher

from .controller.bus_connection import BusConnection

class Server(Dispatcher):
    """
"Server" is responsible to handle requests on the IPC aware bus.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: bus
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    __slots__ = [ ]
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """

    def __init__(self, app_config_prefix = "pas_bus"):
        """
Constructor __init__(Server)

:since: v1.0.0
        """

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

        listener_data = [ ]

        if (listener_mode in ( socket.AF_INET, socket.AF_INET6 )):
            re_result = re.search("^(.+):(\\d+)$", listener_address)

            if (re_result is None):
                listener_data.append(listener_address)
                listener_data.append(None)
            else:
                listener_data.append(re_result.group(1))
                listener_data.append(int(re_result.group(2)))
            #
        else: listener_data.append(listener_address)

        listener_socket = Dispatcher.prepare_socket(listener_mode, *listener_data)

        listener_max_actives = int(Settings.get("{0}_listener_actives_max".format(app_config_prefix), 100))
        Dispatcher.__init__(self, listener_socket, BusConnection, listener_max_actives)
    #
#
