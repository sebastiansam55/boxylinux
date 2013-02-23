# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

import os


import gettext
from gettext import gettext as _
gettext.textdomain('boxylinux')

from gi.repository import Gtk # pylint: disable=E0611
import logging
logger = logging.getLogger('boxylinux')

from boxylinux_lib import Window
from boxylinux.AboutBoxylinuxDialog import AboutBoxylinuxDialog
from boxylinux.PreferencesBoxylinuxDialog import PreferencesBoxylinuxDialog

import boxlinux

# See boxylinux_lib.Window.py for more details about how this class works
class BoxylinuxWindow(Window):
    __gtype_name__ = "BoxylinuxWindow"
    
    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(BoxylinuxWindow, self).finish_initializing(builder)
        
        self.AboutDialog = AboutBoxylinuxDialog
        self.PreferencesDialog = PreferencesBoxylinuxDialog
        
        #adding handler for the update of boxlinux sync dir
        #self.PreferencesDialog.filechooserbutton1.connect("file-set", file_set_event)
        
        self.box = boxlinux.boxlinux()

        # Code for other initialization actions should be added here.
        if not os.path.exists(os.path.expanduser("~")+"/.boxylinux"):
			#means first run!			
			self.auth()
		elif self.box.need_refresh()[0]:
			refreshData = self.box.need_refresh()
			if(refreshData[1]=="refresh"):
				#just need new access token
				self.box.refresh_token_()
			elif(refreshData[1]=="newOAuth"):
				#need whole new auth proc
				self.auth()
		else:
			self.box.load_settings()
			
			
			
		#after this boxlinux will be setup
		
		
		
			
	def exitHand(self, widget):
		import sys
		print("Quit!")
		sys.exit()
		
	def syncHand(self, widget):
		print("Syncing!") 
		
	def closeDialog(self, widget):
		self.builder.get_object("dialog1").hide()
		
	def confirmed(self, widget):
		self.box.get_access_token(self.uniqueId)
		self.builder.get_object("dialog1").get_children()[0].get_children()[0].get_children()[1].set_text("Great job! Now setup your syncDir")
		
	def auth(self):
		confData = self.box.mk_confirm_url()
		self.builder.get_object("dialog1").show()
		self.builder.get_object("dialog1").get_children()[0].get_children()[0].get_children()[0].set_uri(confData[0])
		self.uniqueId = confData[1]
		self.box.save_settings()
		
	def refreshBtnClick(self, widget):
		print self.PreferencesDialog
		self.box.saveDir = self.PreferencesDialog.sync
		print("refreshing!")
		self.box.update_headers()
		self.box.update_json(0)
		self.listFiles()
	
	def listFiles(self):
		file_box = self.builder.get_object("box2")
		file_list = self.box.rootJSON['item_collection']['entries']
		for item in file_list:
			child = gtk.Label(item['name'])
			file_box.pack_start(child, False, False, 0)