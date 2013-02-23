# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

# This is your preferences dialog.
#
# Define your preferences in
# data/glib-2.0/schemas/net.launchpad.boxylinux.gschema.xml
# See http://developer.gnome.org/gio/stable/GSettings.html for more info.

from gi.repository import Gio # pylint: disable=E0611

import gettext
from gettext import gettext as _
gettext.textdomain('boxylinux')

import logging
logger = logging.getLogger('boxylinux')

from boxylinux_lib.PreferencesDialog import PreferencesDialog

class PreferencesBoxylinuxDialog(PreferencesDialog):
    __gtype_name__ = "PreferencesBoxylinuxDialog"

    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the preferences dialog"""
        super(PreferencesBoxylinuxDialog, self).finish_initializing(builder)
        
        self.sync = ""

        # Bind each preference widget to gsettings
        #settings = Gio.Settings("net.launchpad.boxylinux")
        #widget = self.builder.get_object('syncDirChooser')
        #settings.bind("filechoice", widget, "file", Gio.SettingsBindFlags.DEFAULT)
        

        # Code for other initialization actions should be added here.
        self.test = ''
	
	#handler goes here?
	def syncDir(self, widget):
		self.sync = self.builder.get_object('syncDirChooser').get_filename()
		
		
	def saveSettings():
		print("Saving settings!")
		f = open(".boxylinux", "w")
		#f.write("
		f.close()