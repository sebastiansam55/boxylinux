#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

import webbrowser
import urllib2
from xml.dom.minidom import parseString

class SignInBoxLinux:

#how to do global vars in python?
	global apikey
	apikey = "l7c2il3sxmetf2ielkyxbvc2k4nqqkm4"

	def destroy(self, widget, data=None):
		gtk.main_quit()
		
	def delete_event(self, widget, data=None):
		print "delete event!"
		return False
		
	def signin(self, widget, data=None):
		print("Sign in!")
		ticket = self.authenticate()
		global BoxUserData
		BoxUserData = self.auth_token_data(ticket)
		
	def authenticate(self):
		#these need to be changed to add in https checking
		response = urllib2.urlopen("https://www.box.com/api/1.0/rest?action=get_ticket&api_key="+apikey)
		xml = response.read()
		dom = parseString(xml)
		#this doesn't work right it will return something else with the ticket
		#global ticket
		ticket = dom.getElementsByTagName('ticket')[0].toxml()
		ticket = ticket.replace('<ticket>', '').replace("</ticket>","")
		print ticket
		#open web browser and make user authenticate Box.com account
		webbrowser.open("https://www.box.com/api/1.0/auth/"+ticket)
		
		#pop up dialog box and wait for user to click next
		self.waitWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.waitingforauth = gtk.Label("Click continue after approving the Box App")
		self.continuebtn = gtk.Button("Continue")
		self.continuebtn.connect("clicked", self.mainAppLaunch, None)
		self.vbox2 = gtk.VBox(False, 0)
		self.vbox2.pack_start(self.waitingforauth, True, True, 0)
		self.vbox2.pack_start(self.continuebtn, True, True, 0)
		self.waitWindow.add(self.vbox2)
		self.vbox2.show()
		self.waitWindow.show()
		self.continuebtn.show()
		self.waitingforauth.show()
		return ticket
		
	def auth_token_data(self, ticket):
		#trigger this after getting response from self.waitingbox
		#add support for https checking
		response = urllib2.urlopen("https://www.box.com/api/1.0/rest?action=get_auth_token&api_key="+apikey+"&ticket="+ticket)
		xml = response.read()
		dom = parseString(xml)
		
		return dom
		#should return multiple strings or just the xml file and make method to fetch?
		
	def mainAppLaunch(self, widget, data=None):
		#destroy the two previous dialogs...
		self.window.set_visible(False)
		self.waitWindow.set_visible(False)
		print "Launching!"
		return
		
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
		self.setTest()
		
		
		
		
		
		
	def setTest(self):
		#don't abuse the test user!
		self.password.set_text("password")
		self.username.set_text("samsebastian@narod.ru")
			
		
	def main(self):
		gtk.main()


if __name__ == "__main__":
	Box = SignInBoxLinux()
	Box.main()