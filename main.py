#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class BoxyLinux:

	def destroy(self, widget, data=None):
		gtk.main_quit()
		
	def __init__(self):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
