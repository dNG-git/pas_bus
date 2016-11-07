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

import re
import socket

from dNG.data.settings import Settings
from dNG.net.server.dispatcher import Dispatcher

from .connection import Connection

class Server(Dispatcher):
    """
"Server" is responsible to handle requests on the IPC aware bus.

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
Constructor __init__(Server)

:since: v0.3.00
        """

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

        listener_socket = Dispatcher.prepare_socket(listener_mode, listener_host, listener_port)

        listener_max_actives = int(Settings.get("{0}_listener_actives_max".format(app_config_prefix), 100))
        Dispatcher.__init__(self, listener_socket, Connection, listener_max_actives)
    #
#
