#!/usr/bin/env python
from xml.dom.minidom import parseString
import sys
import os
import json
import requests
import argparse
import threading
import hashlib
import random
import time

import gettext
gettext.install('boxlinux', './', unicode=1)

global debug
debug = False
global httpbin
httpbin = False

proxies = {"":"","":""}


class boxlinux():

	def __init__(self):
		self.init_time = int(round(time.time() * 1000))
		self.apikey = "l7c2il3sxmetf2ielkyxbvc2k4nqqkm4"
		self.client_id = self.apikey
		self.client_secret = "eRINJlFQ4aVf1iJ5G477pYKVIUUBJj5a"
		self.version = "0.2"
		self.homeDir = os.path.expanduser("~")
		self.access_token=None
		self.refresh_token=None
		self.proxies=None
		self.saveDir=None
		takesfile = _("filename")
		if(os.name=="nt"):
			self.separator = "\\"
		else:
			self.separator="/"
	"""
	takes nothing, gives user link to visit on box.com and waits for enter to indicate user has authed	
	the "first leg" of the oauth process
	"""
	
	def mk_confirm_url(self):
		uniqueId = self.random_string(10)
		self.confirm_url = "https://api.box.com/oauth2/authorize?response_type=code&client_id="+self.client_id+"&redirect_uri=https://ssebastian.koding.com/box/boxset.php&state="+uniqueId
		return [self.confirm_url, uniqueId]
	
	def setup(self):
		print(_("Open this link in browser and confirm!"))
		uniqueId = self.random_string(10)
		self.confirm_url = "https://api.box.com/oauth2/authorize?response_type=code&client_id="+self.client_id+"&redirect_uri=https://ssebastian.koding.com/box/boxset.php&state="+uniqueId
		print("https://api.box.com/oauth2/authorize?response_type=code&client_id="+self.client_id+"&redirect_uri=https://ssebastian.koding.com/box/boxset.php&state="+uniqueId)
		self.get_access_token(uniqueId)
		dir_prompt = _("Directory to save files in: ")
		#update self.saveDir
		if(sys.version_info[0]==2):
			self.saveDir = raw_input(dir_prompt+self.homeDir+self.separator)
		else:
			self.saveDir = input(dir_prompt+self.homeDir+self.separator)
		self.save_settings()
		
	
	"""
	takes nothing.
	fetches item list
	currently does not update with --dir?
	Writes data using sys.stdout.write instead of print()
	"""	
	def ls_stdout(self):
		items = self.get_item_list()
		i=0
		for item in items:
			sys.stdout.write(items['entries'][i]['name'])
			i+=1
	
	
	"""
	takes nothing
	Fetches the base JSON for the box.com folder.
	Also initilizes the headers that are used throughout the classes
	Calls load settings to load other settings from save file
	"""
	def init_settings(self):
		self.load_settings()
		self.rootJSON = json.loads(self.get_folder_list(0).decode('ascii'))
		if(self.init_time >= (self.last_refresh + (3600*1000))): #adds one hour to the time started if greater then has to refresh
			self.refresh_token_()
		elif(self.init_time >= (self.last_refresh + (14*24*60*60*1000))):	
		#if 14 days have passed since getting new refresh token, have to go through the whole oauth process again
			print(_("Have to authenticate again! Blame box not me. Can only be \"logged\" in for 14 days at a time"))
			self.setup()
		if(debug):
			print(self.rootJSON)
		try:
			print(_("Error encountered! Error was ")+self.rootJSON['status'])
		except:
			pass	
		
	"""
	Loads in settings into self from ~/.boxlinux
	"""		
	def load_settings(self):
		f = open(self.homeDir+self.separator+'.boxlinux', 'r')
		jsonData = json.loads(str(f.read()))
		self.saveDir = jsonData['saveDir']
		self.access_token = jsonData['access_token']
		self.refresh_token = jsonData['refresh_token']
		self.last_refresh = jsonData['last_refresh']
		f.close()
		self.basePath = self.homeDir+self.separator+self.saveDir
		if not os.path.exists(self.basePath):
			os.makedirs(self.basePath)
		global headers
		headers = {'Authorization' : str('Bearer '+self.access_token),}
		if(debug):
			print(headers)
			
	"""
	takes nothing
	Takes settings set from --setup (init_settings and others) and saves them into ~/.boxlinux as JSON data
	"""		
	def save_settings(self):
		## this becomes problem because it will overwrite the file getting rid of any bitly settings
		f = open(self.homeDir+self.separator+'.boxlinux', 'w')
		data = {"access_token":self.access_token, "proxies":self.proxies, "saveDir": self.saveDir, "refresh_token":self.refresh_token, "last_refresh": int(round(time.time() * 1000))}
		f.write(json.dumps(data))
		f.close()
		
	"""
	More boring v1.0 authentication stuff, this gets the auth_token used throughout the classes.
	@return auth_token
	"""		
	def get_access_token(self, uniqueId):
		temR = requests.get("http://ssebastian.koding.com/box/boxget.php?identifier="+uniqueId)
		code = temR.content
		url = "https://api.box.com/oauth2/token"
		data = {"grant_type":"authorization_code", "code": code, "client_secret": self.client_secret, "client_id": self.client_id}
		r = requests.post(url = url, data = data)
		self.process_OAuth_response(r.content)
		return
	
	"""
	Fetches folder list from box
	@return folderList JSON
	"""	
	def get_folder_list(self, folderid):
		url = self.build_url("folder", str(folderid), None)
		r = requests.get(url=url, headers=headers, proxies=self.proxies)
		if(debug):
			print(r.content)
		return r.content
	
	"""
	prints folder list of the current JSON
	can be changed using update_json prior to call
	"""	
	def print_folder_list(self):
		folderList = self.rootJSON['item_collection']['entries']
		print(_("Folders##############"))
		for i in folderList:
			if(i['type']=="folder"):
				print(i['name']+" ID:"+i['id'])				
	"""
	Prints folder list of the current JSON
	can be changed using update_json prior to call
	"""
	def print_file_list(self):
		fileList = self.rootJSON['item_collection']['entries']
		print(_("Files##############"))
		for i in fileList:
			if(i['type']=="file"):
				print(i['name']+" ID:"+i['id'])	
				
	"""
	@param fileid, fileid on box.com, can be got with uni_get_name
	@param filepath, does nothing? I guess I replaced it with self.basePath
	Downloads a file based on the fileid
	"""
	def download_fileid(self, fileid, filepath):
		self.infoprint(_("Downloading: ")+fileid)
		fileid=str(fileid)
		url = self.build_url("file", fileid, "content")
		if(httpbin):
			url = "http://httpbin.org/get"
		r = requests.get(url=url, headers=headers, proxies=self.proxies)
		filedata = r.content
		if(debug):
			print(r)
			print(filedata)
		filename = self.uni_get_id(fileid, "name", "file")
		f = open(self.basePath+self.separator+filename, 'w')
		f.write(filedata)
		f.close()
		
	"""
	Impementation of the downloadThread to use python's threading capabilities
	@param fileid, fileid on box.com, can be got with uni_get_name
	@param filepath, does nothing? I guess I replaced it with self.basePath	
	Meant to use and return the same as download_fileid
	"""	
	def downloadThreaded(self, fileid, filepath):
		self.infoprint(_("Downloading: ")+fileid)
		fileid = str(fileid)
		url = self.build_url("file", fileid, "content")
		dlThread = downloadThread()
		filename = self.uni_get_id(fileid, "name", "file")
		dlThread.setData(fileid, filename, filepath, headers, self.proxies, url, self.separator, self.basePath)
		dlThread.start()
	
	"""
	@param filepath, filepath of the file to read and send up to box.com
	@param filename, name for the file on box.com
	@param folderid, id of the folder to put the file in, default will probably be zero
	"""	
	def upload(self, filepath, filename, folderid):
		self.infoprint(_("Uploading..."))
		url = self.build_url("file", "content", None)
		payload = {'filename1': filename, 'folder_id': folderid}
		try:
			data = {filename: open(filepath, 'r')}
		except:
			self.errprint(_("File selected is not a file or other error"))
			return
		r = requests.post(url=url, data=payload, headers=headers, files=data, proxies=self.proxies)
	
	"""
	@param fileid, id of file to delete
	Deleted file with corresponding fileid on box.com
	"""
	def rm_file(self, fileid):
		try:
			sha1sum = self.get_sha1sum_remote(fileid)
		#self.varprint("Sha1sum of file to be deleted: "+sha1sum)
			url = self.build_url("file", fileid, None)
			headers_ = {'Authorization' : 'Bearer '+self.access_token, 'If-Match': sha1sum}
			r = requests.delete(url=url, headers=headers_, proxies=self.proxies)
			print(r.content)
		except:
			self.infoprint(_('Something bad happened when deleting file...'))
	
	"""
	@param folderid, id of folder to delete
	Deletes folder with corresponding id
	Does not delete locally
	"""
	def rm_folder(self, folderid):
		print(_("Deleting Folder with id ")+folderid)
		url = self.build_url("folder", str(folderid)+"?recursive=true", None)
		#varprint(url)
		r = requests.delete(url=url, headers=headers, proxies=self.proxies)
		print(r.content)
	
	"""
	Fetches file ids from the current self.rootJSON
	@return returns list of fileids
	"""
	def get_all_file_id(self):
		fileList = self.get_item_list()
		j=0
		numberFiles=0
		for item in fileList['entries']:
			if item['type']=="file":
				numberFiles+=1
		rtrnList = range(0, numberFiles)
		for i in fileList['entries']:
			if(i['type']=="file" ):
				try:
					rtrnList[j] = i['id']
				except:
					pass
				j+=1
			
				
				
		return rtrnList
	
	"""
	@param fileid, fileid of sha1 to fetch
	@return returns the fileid of file
	Used when deleting files
	"""
	def get_sha1sum_remote(self, fileid):
		fileList = self.rootJSON['item_collection']['entries']
		if(debug):
			print(self.rootJSON)
		for item in fileList:
			if(item['id']==fileid):
				return item['sha1']				
	
	"""
	@param foldername, name of new folder
	@param parent_folderid, id of the folder to create new folder in (root=0)
	@return server response, can be checked for pass/fail
	"""
	def mk_new_folder(self, foldername, parent_folderid):
		url = self.build_url("folder", None, None)
		payload = {'name': ''+foldername+'', 'parent': {'id': parent_folderid}}
		r = requests.post(url=url, data=json.dumps(payload), headers=headers, proxies=self.proxies)
		return r.content
	
	"""
	@param itemid, id of item to get shareurl of
	@param itemtype, file or folder
	@return shareurl, returns the shareable URL
	"""
	def get_item_url(self, itemid, itemtype):
		if itemtype=="folder" or itemtype=="FOLDER":
			url = self.build_url(itemtype, itemid, None)
			payload = {'shared_link': {'access': 'Open'}}
			r = requests.put(url=url, data=json.dumps(payload), headers=headers, proxies=self.proxies)
			rtrnval = json.loads(r.content)			
		elif itemtype=="file" or itemtype=="FILE":
			url =self.build_url(itemtype, itemid, None)
			payload = {'shared_link': {'access':'Open'}}
			r = requests.put(url=url, data=json.dumps(payload), headers=headers, proxies=self.proxies)
			rtrnval = json.loads(r.content)
		return [rtrnval['shared_link']['url'], rtrnval['shared_link']['download_url']]
	"""
	@param itemid, itemid of item to remove url of
	@param itemtype, folder or file
	@return content, returns the server reponse that can be checked for pass fail
	"""
	def rm_share_url_item(self, itemid, itemtype):
		if itemtype=="folder" or itemtype=="FOLDER":
			url = self.build_url(itemtype, itemid, None)
			payload = {'shared_link': None}
			r = requests.put(url=url, data=json.dumps(payload), headers=headers, proxies=self.proxies)
			return r.content
		elif itemtype=="file" or itemtype=="FILE":
			url = self.build_url(itemtype, itemid, None)
			payload = {'shared_link': None}
			r = requests.put(url=url, data=json.dumps(payload), headers=headers, proxies=self.proxies)
			return r.content
			
	"""
	@param newname, new name for file or folder
	@param itemid, id of item to rename
	@param itemtype, folder or file
	"""
	def rename_item(self, newname, itemid, itemtype):
		if(itemtype=="file" or itemtype=="FILE"):
			url = self.build_url(itemtype, itemid, None)
			payload = {'name': newname}
			r = requests.put(url=url, data=json.dumps(payload), headers=headers, proxies=self.proxies)
			return r.content
		elif(itemtype=="folder" or itemtype=="FOLDER"):
			url = self.build_url(itemtype, itemid, None)
			payload = {'name': newname}
			r = requests.put(url=url, data=json.dumps(payload), headers=headers, proxies=self.proxies)
			return r.content
	
	"""
	Shortcut, not really necessary
	"""
	def get_item_list(self):
		# self.rootJSON	
		return self.rootJSON['item_collection']
	"""
	@param itemid, name of the item to get info about
	@param getthis, what info to get about the item
	@param itemtype, what kind of item it is, either folder or file
	Used for fetching any kind of info from the JSON
	@return iteminfo requested
	"""
	def uni_get_id(self, itemid, getthis, itemtype):
		files = self.rootJSON['item_collection']['entries']
		for item in files:
			if(item['id']==itemid and item['type']==itemtype):
				return item[getthis]	
	
	"""
	@param itemname, name of the item to get info about
	@param getthis, what info to get about the item
	@param itemtype, what kind of item it is, either folder or file
	Used for fetching any kind of info from the JSON
	@return iteminfo requested
	"""
	def uni_get_name(self, itemname, getthis, itemtype):
		files = self.rootJSON['item_collection']['entries']
		for item in files:
			if(item['name']==itemname and item['type']==itemtype):
				return item[getthis]
				
		return None
				
	"""
	@param folderid, folderid to update JSON to
	Updates the JSON to a new folder. Used by many different methods. Replaces update_dom
	More or less how you `cd`
	"""
	def update_json(self, folderid):
		self.infoprint(_("Moving into new Directory"))
		self.rootJSON = json.loads(self.get_folder_list(folderid))
		if(debug):
			print(self.rootJSON)
	
	"""
	@param http_proxy
	@param https_proxy
	takes proxies in form of USERNAME:PASSWORD@IPADDRESS:PORT
	Saves settings in .boxlinux
	"""
	def setup_proxies(self, http_proxy, https_proxy):
		#httpproxy = raw_input("What is the HTTP proxy?: ")
		#httpsproxy = raw_input("What is the HTTPS proxy?: ")
		self.proxies = {"http": "http://"+http_proxy, "https": "https://"+https_proxy,}
		self.save_settings()
	
	"""
	@param fileid	
	@return list of text of comments, appear to come in chronological order
	"""
	def get_comments(self, fileid):
		url = self.build_url("file", fileid, "comments")
		r = requests.get(url=url, headers=headers)
		if(debug):
			print(r.content)
		return json.loads(r.content)
	
	"""
	@param comments, list of comments as returned by get_comments()
	"""
	def print_comments(self, comments):
		i=0
		for k in comments['entries']:
			print(comments['entries'][i]['created_by']['name']+" said: "+comments['entries'][i]['message'])
			i+=1
	
	"""
	@param itemtype, folder or file
	@param itemid, file or folder id of the item
	@param getthis, something like "content" or something else
	Shortcut method for building urls for many of the methods
	@return url
	"""
	def build_url(self, itemtype, itemid, getthis):
		if(debug):
			print(itemtype, itemid, getthis)
		url = "https://api.box.com/2.0/"+str(itemtype)+"s/"
		if not itemid==None:
			url+=str(itemid)
			if not getthis==None:
				url+="/"+str(getthis)
		if(debug):
			self.varprint(url)
		return url
		
	"""
	@param fileid, fileid to comment on
	@param comment, comment to be made on the file specifed by fileid
	"""
	def mk_comment(self, fileid, comment):
		url = self.build_url("file", fileid, "comments")
		if(debug):
			print(url)
		payload = {"message": comment}
		r = requests.post(url=url, data=json.dumps(payload), headers=headers, proxies=self.proxies)
		
	"""
	@param file_list, taken from get_all_file_id()
	calls downloadThreaded for with every one of the list items in file_list
	"""
	def download_all(self, file_list):
		j=0
		for i in file_list:
			#print i
			#self.download_fileid(file_list[j], "")
			self.downloadThreaded(file_list[j], "")			
			j+=1
			
	"""
	@param itemid, box.com itemid
	@param itemtype, should be file or folder
	@return raw info on item
	"""
	def get_info_item(self, itemid, itemtype):
		if itemtype=="folder" or itemtype=="FOLDER":
			url = "https://api.box.com/2.0/folders/"+str(itemid)+".xml"
			r = requests.get(url=url, headers=headers, proxies=self.proxies)
			return r.content
		elif itemtype=="file" or itemtype=="FILE":
			url = "https://api.box.com/2.0/files/"+str(itemid)+".xml"
			r = requests.get(url=url, headers=headers)
			return r.content
			
	"""
	Shortcut
	"""
	def ls(self):
		self.print_folder_list()
		self.print_file_list()
	"""
	Lists items shared 
	Not currently supported
	WILL NOT RUN
	"""
	def list_items_shared(self):
		self.print_file_list(self.print_folder_list(-1, True), False)
	"""
	Deprecated, from when everything was a list of options.
	"""
	def get_local_files():
		return os.listdir(os.getcwd())	
	"""
	Convient error printing.
	Should add timestamp
	"""
	def errprint(self, printthis):	
		print(_("[ERROR] ")+printthis)
	"""
	Shortcut for variable checking (mostly used for testing)
	"""
	def varprint(self, printthis):
		print(_("[VARCHECK] ")+str(printthis))
	"""
	Shortcut for printing info
	"""		
	def infoprint(self, printthis):
		print(_("[INFO] ")+str(printthis))
	
	"""
	@param filename takes a full file location
	"/home/sam/filename" not just "filename"
	@return sha1sum of given file
	"""	
	def get_sha1sum_local(self, filename):
		#print filename
		if( not os.path.isdir(filename)):
			f = open(filename, "r")
			hasher = hashlib.sha1()
			hasher.update(f.read())
			sha1 = hasher.hexdigest()
			f.close()
			return sha1
		else:
			return
			
	def random_string(self, length):
		output = ''
		for num in range(length):
			rand = random.randint(65, 90) #ascii reg chars A-Z
			output += str(chr(rand))
		return output
		
	def refresh_token_(self):
		url = "https://api.box.com/oauth2/token"
		data = {"refresh_token": self.refresh_token, "client_id": self.client_id, "client_secret": self.client_secret, "grant_type": "refresh_token"}
		r = requests.post(url = url, data = data)
		if(debug):
			print(r.content)
		self.process_OAuth_response(r.content)
		
	"""
	access token lasts for one hour
	refresh token lasts for 14 days	
	"""
	def process_OAuth_response(self, data):
		JSON = json.loads(data)		
		self.access_token = JSON.get("access_token")
		self.refresh_token = JSON.get("refresh_token")
		if((self.access_token == None) and (self.refresh_token == None)):
			print(_("Access token not found"))
			print(_("Refresh token not found"))
			sys.exit(1)
		self.save_settings()
		self.update_headers()	
		return
		
	def update_headers(self):
		global headers
		headers = {'Authorization' : str('Bearer '+self.access_token),}
		
	def upload_raw(self, raw, filename, folderid):
		self.infoprint(_("Uploading..."))
		url = self.build_url("file", "content", None)
		payload = {'filename1': filename, 'folder_id': folderid}
		f = os.tmpfile()
		f.write(raw)
		try:
			data = {filename: f}
		except:
			self.errprint(_("File selected is not a file or other error"))
			return
		r = requests.post(url=url, data=payload, headers=headers, files=data, proxies=self.proxies)
		f.close()
		
	def need_refresh(self):
		if(self.init_time >= (self.last_refresh + (3600*1000))): #adds one hour to the time started if greater then has to refresh
			return [True, "refresh"]
		elif(self.init_time >= (self.last_refresh + (14*24*60*60*1000))):	
			return [True, "newOAuth"]
		
class downloadThread(threading.Thread):
	"""
	Sets data for the thread.
	To be used before running dlThread.start()
	"""
	def setData(self, fileid, filename, filepath, headers, proxies, url, separator, basePath):
		self.fileID = fileid
		self.filename = filename
		self.filepath = filepath
		self.headers = headers
		self.proxies = proxies
		self.url = url
		self.separator = separator
		self.basePath = basePath
	"""
	The download Thread...
	Writes the data to file
	"""
	def run(self):
		self.fileID=str(self.fileID)
		r = requests.get(url=self.url, headers=self.headers, proxies=self.proxies)
		#r = requests.get(url="http://httpbin.org/get", headers=self.headers, proxies=self.proxies)
		filedata = r.content
		f = open(self.basePath+self.separator+self.filename, 'w')
		f.write(filedata)
		f.close()
			

class googlShort():
	"""
	@return goo.gl link. 
	"""
	def shorten_url(self, longURL):
		url = "https://www.googleapis.com/urlshortener/v1/url"
		headers = {'Content-type': 'application/json'}
		data = {'longUrl': longURL}
		r = requests.post(url=url, headers=headers, data=json.dumps(data))
		return json.loads(r.content)['id']

class bitlyShort():
	"""
	
	returns nothing sets all in self
	""" 
	def load_api_key():
		self.api_key
		self.username
		f = open(os.getenv("HOME")+'/.boxlinux', 'r')
		settings = json.loads(f.read())
		self.api_key = settings['bitly']
		self.username = settings['username']
		
	"""
	
	"""
	def shorten_url(longUrl):
		longUrl = urllib.quote_plus(longUrl)
		load_api_key()
		url = "https://api-ssl.bitly.com/v3/shorten?longUrl="+longUrl+"&login="+self.username+"&apiKey="+self.api_key
		r = requests.get(url)
		rtrnval = json.loads(r.content)
		#this is quick and dirty, it will break if any changes are made to the bitly API
		rtrnval = json.loads(json.dumps(rtrnval['data']))
		return rtrnval['url']
		
		
		
		
		

"""
    BoxLinux; Bringing Box services to the Linux desktop
    Copyright (C) 2012  Sam Sebastian
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""



"""
Dependincies:
python-requests
	in the ubuntu repos it only installs the version for 2.7
	looking for fix for python3.2 now...
python2.7 (duh!)
"""