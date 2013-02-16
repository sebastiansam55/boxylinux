# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

import gettext
from gettext import gettext as _
gettext.textdomain('boxylinux')

from gi.repository import Gtk # pylint: disable=E0611
import logging
logger = logging.getLogger('boxylinux')

from boxylinux_lib import Window
from boxylinux.AboutBoxylinuxDialog import AboutBoxylinuxDialog
from boxylinux.PreferencesBoxylinuxDialog import PreferencesBoxylinuxDialog

# See boxylinux_lib.Window.py for more details about how this class works
class BoxylinuxWindow(Window):
    __gtype_name__ = "BoxylinuxWindow"
    
    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(BoxylinuxWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutBoxylinuxDialog
        self.PreferencesDialog = PreferencesBoxylinuxDialog

        # Code for other initialization actions should be added here.

