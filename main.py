#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class BoxLinux:

	def destroy(self, widget, data=None):
		gtk.main_quit()
		
	def delete_event(self, widget, data=None):
		print "delete event!"
		return False
		
	def signin(self, widget, data=None):
		print("Sign in!")
		
	def __init__(self):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect("delete_event", self.delete_event)
		self.window.connect("destroy", self.destroy)
		#Username entry box
		self.username = gtk.Entry()
		#password entry box (duh!)
		self.password = gtk.Entry()
		#set the password obscure character
		self.password.set_invisible_char("B")
		#make password box act like one
		self.password.set_visibility(False)
		
		self.signinbtn = gtk.Button("Sign in")
		self.signinbtn.connect("clicked", self.signin, None)
		
		self.exitbtn = gtk.Button("Exit")
		self.exitbtn.connect("clicked", self.destroy, None)
		
		#hbox for buttons
		self.hbox1 = gtk.HBox(False, 0)
		self.hbox1.pack_start(self.signinbtn, True, True, 0)
		self.hbox1.pack_start(self.exitbtn, True, True, 0)
		
		#main vbox for username password and sign in buttons (checkbox for remember me?)
		self.vbox1 = gtk.VBox(False,0)
		self.vbox1.pack_start(self.username, True, True, 0)
		self.vbox1.pack_start(self.password, True, True, 0)
		self.vbox1.pack_start(self.hbox1, True, True, 0)	
		
		self.window.set_border_width(10)
		
		#add vbox and hboxes to the window
		self.window.add(self.vbox1)
		#That line doesn't WORK!
		#####self.window.add(self.hbox1)
		#show ALL the objects!
		self.vbox1.show()
		self.hbox1.show()
		self.signinbtn.show()
		self.exitbtn.show()
		self.username.show()
		self.password.show()
		self.window.show()
		
	def main(self):
		gtk.main()


if __name__ == "__main__":
	Box = BoxLinux()
	Box.main()
