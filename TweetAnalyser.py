##NB  THIS IS BUILT IN PYTHON 3.X!!  WILL NOT RUN ON PYTHON 2.x  ALSO NEEDS INTERNET CONNECTION!!!
## Data Cohen 2019-12-09
import json
import re
import os
import threading
import requests
import random
from re import *
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import tkinter.ttk as ttk
from threading import *
import folium
from folium.plugins import FastMarkerCluster
from collections import Counter
import pandas as pd
import numpy as np


##--------------------------------------------------------------------------------------------------------------------------------
##Globals
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##Stored JSON Data
listID = []
listUser = []
listDate = []
listContent = []
listLat = []
listLong= []
listGeoLocation = []
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
storedvalues = []
SlistPOS = []
tweetcount = 0 
lines = 0
gui = Tk() 
resultsnum = 0
mapprintmode = 0
##--------------------------------------------------------------------------------------------------------------------------------



def populateme(js0n):
	'''
	takes a path to a JSON file as an argument.
	wipes any previous data in the list arrays to make sure all data added is from the new file. Then, opens the file and adds 1 to the lines variable for every line in the file. This gives a line count value.
	the file is then parsed by python's JSON library (NOTE:  it has to be encoded as utf-8 or python throws an error). Each row in the JSON file is a tweet, so the for loop loads each row of data; parses it as
	json, and then stores it in the tweets variable.  The tweet is then deconstructed into the different list arrays corresponding to the data they store.

	Tweetcount is used as a counter variable to give the user a loading bar.
	'''
	global tweetcount
	global lines
	global listID
	global listUser
	global listDate
	global listContent
	global listLat
	global listLong
	global listGeoLocation
	global mapprintmode
	mapprintmode = 0
	listID = []
	listUser = []
	listDate = []
	listContent = []
	listLat = []
	listLong= []
	listGeoLocation = []
	with open(js0n, 'r', encoding='utf-8') as file:
		lines = sum(1 for _ in file)
	with open(js0n, 'r', encoding='utf-8') as file:
		for row in file:
			tweets = json.loads(row)
			listID.append(str(tweets['user']['_id']))
			listUser.append(str(tweets['user']['screenName']))
			listDate.append(str(tweets['createdAt']['$date']))
			listContent.append(str(tweets['text']))
			listLat.append(str(tweets['geoLocation']['latitude']))
			listLong.append(str(tweets['geoLocation']['longitude']))
			listGeoLocation.append(str(tweets['geoLocation']['latitude']) + "," +str(tweets['geoLocation']['longitude']))
			print("\r"+"====================================================================")
			print("\r"+"")
			print("\r"+"Loading Tweet: " + str((tweetcount+1))+ "/" + str(lines))
			print("\r"+"")
			print("\r"+"====================================================================")
			print("\r"+"")
			tweetcount = tweetcount+1

def onFrameConfigure(canvas):
	'''
	Configures the canvas to be able to scroll all the way down.
	'''
	canvas.configure(scrollregion=canvas.bbox("all"))

def createMap(mp, num, latitude, longitude, name, text, date):
	'''
	takes 7 arguments simply corresponding to tweet data to be placed onto a pop up marker.
	MP is the folium map to add them to. 
	'''
	poppy = "<h3><b> @" + name + "</b></h3><br><h4>" + "Tweet: " + text + "</h4><br><h5> Sent at: " + date + "</h5>" 
	tooltip = "Tweet " + str(num)
	folium.Marker([latitude,longitude], popup=poppy, tooltip=tooltip).add_to(mp)

def lookupward(jsondata):
	'''
	lookupward takes a single argument, which is a preprepared JSON packet for requests to send to the postcodes.io API.
	it sends this request, ensuring the correct headers are set (also it HAS to be sent as data, as the createmapjson() function already packaged it into json).

	Once sent, and the response recieved, the program will look specifically for the admin_ward key value within the returned json, and put this into the postarray; returning this array at the end.
	'''
	postarray = []
	makeurl = 'https://api.postcodes.io/postcodes/'
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	r = requests.post(makeurl, data=jsondata, headers=headers)
	jsontext = r.json()
	for x in range(0,(len(jsontext['result'])-1)):
		print("\r"+"====================================================================")
		print("\r"+"")
		print("\r"+ "Processing Tweet: " + str(x)+ "/" + str(len(jsontext['result'])-1))
		print("\r"+"")
		print("\r"+"====================================================================")
		print("\r"+"")
		if jsontext['result'][x]['result'] == None:
			print("\r"+"")
			print("No value found:  Skipping.")
			print("\r"+"")
		else:
			postarray.append(jsontext['result'][x]['result'][0]['admin_ward'])
	return postarray
	

	
def OPMap(mode):
#	This is rather complex code, but rather simple when you put it into perspective.
#
#	Imagine this like a big tree.
#											Which MODE?
#											 /      \
#										  Marker   Heat Map
#										    /          \
#				Has a search been performed?            Has a search been performed?
#				|                        |          (also create Warddata[] and attrib[])
#				|                        |              |                          |
#				Yes                      No             Yes                        No
#				|                        |              |                          |
#				Run createmap      Run createmap        |                          |
#				using SlistPOS     using the normal     |                           \_____________is listID longer than 100 (postcode.io's max bulk rate)
#				for the search     list arrays          |                                            |                                                 |
#				index values            |               |                                           Yes                                                No
#					  |                 |               |                                            |                                                 |
#			  ________/________________/                |                                    Divide the length by 100 to                    Throw it to lookupward and
#			 |                                          |                                   know how many times to iterate.                store the array into postcodes
#			 |                                          |                                   then store the lookupward                                   |
#			 |           is SlistPOS longer than 100 (postcode.io's max bulk rate)          array in postcodes, providing                               |
#			 |           |                                                    |             a start value from the iterator                             |
#			 |          Yes                                                   No            multiplied by 100 to return to                              |
#			 |           |                                                    |             the amount of values in the                                 |
#			 |           |                                                    |             dataset                                                     |
#			 |           |                                                    |                           |                                             |
#            |   Divide the length by 100 to know          Throw it to lookupward and                     |                                             |
#			 |   how many times to iterate. Then,          store the array into postcodes                 |                                             |
#			 |   store the lookupward array in                           |                                |                                             |
#			 |   postcodes, providing a start                            |                                |                                             |
#			 |   value from the iterator                                 |                                |                                             |
#			 |   multiplied by 100 to return to the                      |                                |                                             |
#			 |   amount of values in the dataset                         |                                |                                             |
#			 |                  |                                        |                                |                                             |
#			 |                  |                                        |                                |                                             |
#			 |                  Use the collections Counter() function to create a dictionary of how many times each Ward appears.  Use this to create a
#			 |                  Pandas dataframe of the wards and how many times they show up. Then, create a choropleth map using folium and GEOJSON
#			 |                  data from the UK-GeoJSON github.
#			 |                               |
#			 \_______________________________/
#                           |
#			                |
#		 Save the map to the selected output location 

	global mapprintmode
	mp = folium.Map(location=[53.4781,-2.2447], zoom_start=15)
	counter = len(listID)
	try:
		filepick = filedialog.asksaveasfilename(initialdir = "/",title = "Select file",filetypes = [("Folium Map","*.html")])
	except FileNotFoundError or TypeError:
		messagebox.showerror("Error", "Please select a location")
		return
	if mode == 0:
		if mapprintmode == 0:
			for x in range(0,counter):
				createMap(mp, (x+1), float(listLat[x]),float(listLong[x]), str(listUser[x]), str(listContent[x]),str(listDate[x]))
		elif mapprintmode == 1:
			for x in range(0,len(SlistPOS)):
				createMap(mp, (x+1), float(listLat[SlistPOS[x]]),float(listLong[SlistPOS[x]]), str(listUser[SlistPOS[x]]), str(listContent[SlistPOS[x]]),str(listDate[SlistPOS[x]]))
	elif mode == 1:
		warddata = []
		attrib = []
		electoral_wards = 'https://github.com/martinjc/UK-GeoJSON/raw/master/json/electoral/eng/wards.json'
		if mapprintmode == 0:
			if len(listID)>100:
				for y in range(0,(int(round(len(listID)/100))),1):
					postcodes = lookupward(createmapjson(((y*100))))
					for x in range(0,len(postcodes)):
						warddata.append(postcodes[x])
			else:
				postcodes = lookupward(createmapjson(None))
				for x in range(0,len(postcodes)):
					warddata.append(postcodes[x])
		elif mapprintmode == 1:
			if len(SlistPOS)>100:
				for y in range(0,(int(round(len(SlistPOS)/100))),1):
					postcodes = lookupward(createmapjson(y*100))
					for x in range(0,len(postcodes)):
						warddata.append(postcodes[x])
			else:
				postcodes = lookupward(createmapjson(None))
				for x in range(0,len(postcodes)):
					warddata.append(postcodes[x])
		wardcounts = Counter(warddata)
		warddata=[]
		for k,v in wardcounts.items():
			warddata.append(k)
			attrib.append(v)
		dataframe = pd.DataFrame(columns = {'Ward', 'Data'})
		dataframe.columns = ['Ward','Data']
		dataframe['Ward'] = warddata
		dataframe['Data'] = attrib
		folium.Choropleth(geo_data=electoral_wards,
			  name='Heat Map',
			  data=dataframe,
			  columns=['Ward', 'Data'],
			  key_on='feature.properties.WD13NM',
			  fill_color='BuPu',
			  fill_opacity=0.7,
			  line_opacity=0.5,
			  legend_name='Tweets').add_to(mp)
	mp.save(str(filepick))
	
def createmapjson(starter):
	'''
	createmapjson is integral to using the postcodes.io API.  it formats the tweet geolocation into a VERY specific JSON dictionary to be sent.
	The function is technically 'overloaded', since None can be passed to it.  This is because the function needs a way to know if the given dataset exceeds postcodes.io's bulk lookup limit of 100
	If an IndexError is thrown due to the function trying to access outside of the array, the function knows that this means there is less than 100 values left in the dataset, and it should
	only look for the specific number of values left.

	The Python Dictionary is then converted to JSON.
	'''
	jsondata={}
	temp=[]
	if starter == None:
		if mapprintmode == 0:
				temp = [{'longitude': float(listLong[x]),'latitude': float(listLat[x])} for x in range(0,len(listID))]
		elif mapprintmode == 1:
				temp = [{'longitude': float(listLong[SlistPOS[x]]),'latitude': float(listLat[SlistPOS[x]])} for x in range(0,len(SlistPOS))]
		jsondata['geolocations'] = temp
	else:
		if mapprintmode == 0:
			try:
				temp = [{'longitude': float(listLong[x]),'latitude': float(listLat[x])} for x in range(starter,(starter+99))]
			except IndexError:
				finalpoint = len(listID)-starter
				temp = [{'longitude': float(listLong[x]),'latitude': float(listLat[x])} for x in range(starter,(starter+finalpoint))]
		elif mapprintmode == 1:
			try:
				temp = [{'longitude': float(listLong[SlistPOS[x]]),'latitude': float(listLat[SlistPOS[x]])} for x in range(starter,(starter+99))]
			except IndexError:
				finalpoint = len(SlistPOS)-starter
				temp = [{'longitude': float(listLong[SlistPOS[x]]),'latitude': float(listLat[SlistPOS[x]])} for x in range(starter,(starter+finalpoint))]
		jsondata['geolocations'] = temp
	return json.dumps(jsondata)
	
def OPJSON():
	'''
	The function performs two try catches.  The first is to open a GUI interface at the current working directory (cwd) using the python OS library. If a file is not chosen, an error will be thrown and the function will be stopped.
	The second, attempts to run the populateme function using the file previously selected.  if this fails, an error is thrown to the user again, and the function is stopped once again.  If the function is successful,
	it will tell the user.
	'''
	cwd = os.getcwd()
	try:
		filepick = filedialog.askopenfilename(initialdir = cwd,title = "Select JSON File", filetypes = [("JSON File","*.json")])
	except FileNotFoundError:
		messagebox.showerror("Error", "Please select a location")
		return
	try:
		populateme(filepick)
	except TypeError:
		messagebox.showerror("IO Error", "Please select a file!")
		return
	messagebox.showinfo("File Opened", "Successfully opened: " + str(filepick))
    
	
def Search(inputarray,searchterm):
	'''
	Search takes two parameters:
	inputarray: is an array to search through
	searchterm: is a string or RE to look for
	To begin, the function sets mapprintmode to 1, as this tells OPMAP to only create a map from the values in SlistPOS.
	Then, the function checks whether the first value from searchterm is a RE Character.
	It will then use the python RE library to search the entire inputarray for a match (where the returned value isnt None) and stores it into global storedvalues array.
	'''
	global mapprintmode
	mapprintmode = 1
	expressions_re = ["[","\\", ".","^","$","*","+","{","|","("]
	if searchterm[0] in expressions_re:
		nonre_search = searchterm
	else:
		nonre_search = "(" + searchterm + ")"
	for x in range(0,len(inputarray)):
		if re.search(nonre_search, inputarray[x], re.IGNORECASE) != None:
			storedvalues.append(x)
	
def rmdupe(inputarray):
	'''
	rmdupe takes an array and transfers values to SlistPOS, ensuring no duplicates go into SlistPOS
	'''
	for number in inputarray:
		if number not in SlistPOS:
			SlistPOS.append(number)

def Results(frame, searchme):
	'''
	Results takes 2 parameters.  frame, which is just the frame for printresults to print the results onto, and searchme.  Searchme is the string or RE to search.
	TKinter allows you to access the object to find the children within a frame. Results uses this to WIPE the provided frame of all widgets, ready to write new labels.
	Using multithreading for each array, the thread is instructed to execute searchme on the provided array.
	SlistPOS is used to store result index values into
	rmdupe makes sure there are no duplicate entries within SlistPOS
	printresults is then called to print the results.
	A messagebox appears to the user to tell them how many results were found.
	NOTE:  return 'break' is used to overwrite the TKinter textbox widget's newline function.
	'''
	global storedvalues
	global SlistPOS
	global resultsnum
	storedvalues = []
	SlistPOS = []
	for widget in frame.winfo_children():
		widget.destroy()
	global tweetcount
	x = threading.Thread(target=Search, args=(listID,searchme))
	xa = threading.Thread(target=Search, args=(listUser,searchme))
	xb = threading.Thread(target=Search, args=(listDate,searchme))
	xc = threading.Thread(target=Search, args=(listContent,searchme))
	xd = threading.Thread(target=Search, args=(listGeoLocation,searchme))
	x.start()
	xa.start()
	xb.start()
	xc.start()
	xd.start()
	x.join()
	xa.join()
	xb.join()
	xc.join()
	xd.join()
	rmdupe(storedvalues)
	printresults(frame)
	resultsnum = len(SlistPOS)
	messagebox.showinfo("Search Completed", "Found: " + str(len(SlistPOS)) + " items.")
	return 'break'
	
def printresults(frame):
	'''
	The print results function takes a frame as a param.  This has to be the fram you want the data to be drawn on.  The function takes data from the List arrays, using the position values in SlistPOS to tell the function which
	specific lines of data to write. tweetrows is used as a counter variable to just move the metaphorical label "pen" down one row for each iteration.
	'''
	global SlistPOS
	Grid.rowconfigure(frame,0,weight=1)
	Grid.columnconfigure(frame,0,weight=1)
	tweetrows = 2
	for x in range(0,len(SlistPOS)):
		print("\r"+"====================================================================")
		print("\r"+"")
		print("\r"+ "Processing Tweet: " + str(x)+ "/" + str(len(SlistPOS)))
		print("\r"+"")
		print("\r"+"====================================================================")
		print("\r"+"")
		Label(frame, text="User_ID", width=20, borderwidth="1", relief="solid").grid(row=1, column=0)
		Label(frame, text="Twitter Handle", width=20, borderwidth="1", relief="solid").grid(row=1, column=1)
		Label(frame, text="Date of Tweet", width=30, borderwidth="1", relief="solid").grid(row=1, column=2)
		Label(frame, text="Tweet Content", width=30, borderwidth="1", relief="solid").grid(row=1, column=3)
		Label(frame, text="GeoLocation", width=20, borderwidth="1", relief="solid").grid(row=1, column=4)
##===========================================================================================================================##
		Label(frame, text=listID[SlistPOS[x]], width=20,height=7, borderwidth="1", relief="solid").grid(row=tweetrows, column=0)
		Label(frame, text="@"+listUser[SlistPOS[x]], width=20,height=7, borderwidth="1",relief="solid").grid(row=tweetrows, column=1)
		Label(frame, text=listDate[SlistPOS[x]], width=30,height=7, borderwidth="1", relief="solid").grid(row=tweetrows, column=2)
		Label(frame, text=listContent[SlistPOS[x]], width=30,height=7, borderwidth="1", relief="solid", wraplength=200, justify="left", anchor = "nw").grid(row=tweetrows, column=3)
		Label(frame, text=listGeoLocation[SlistPOS[x]], width=20,height=7, borderwidth="1", relief="solid").grid(row=tweetrows, column=4)
##============================================================================================================================##
		Grid.rowconfigure(frame,tweetrows,weight=1)
		Grid.columnconfigure(frame,tweetrows,weight=1)
		tweetrows = tweetrows + 1
	
def templatesearch(selection, frame):
	'''
	templatesearch takes 2 arguments.
	selection:  is which template within the combobox has been chosen.
	frame: is the frame to draw the results on.

	This function wipes storedvalues and SlistPOS to make sure they're empty. Then, it deletes all drawn widgets within the given frame.
	The template arrays are then set up.
	The function then checks which selection the user has chosen, and iterates through the corresponding template array, searching the tweets for any matches for each of the values within the template array.
	rmdupe then checks to make sure no duplicates are printed twice, and then the results are printed using printresults.
	'''
	global storedvalues
	global SlistPOS
	global resultsnum
	storedvalues = []
	SlistPOS = []
	for widget in frame.winfo_children():
		widget.destroy()
	violent = ["violence", "violent", "knife crime", "assault", "murder"]
	nonviolent = ["theft", "robbery", "slander", "hacking", "hack"]
	if selection == 0:
		for x in range(0,len(violent)):
			Search(listContent,violent[x])
	elif selection == 1:
		for x in range(0,len(nonviolent)):
			Search(listContent,nonviolent[x])
	else:
		messagebox.showwarning("Error", "No template selected!")
	rmdupe(storedvalues)
	printresults(frame)
	messagebox.showinfo("Template Loaded", "Found: " + str(len(SlistPOS)) + " items.")
	resultsnum = len(SlistPOS)

def main():
	'''This is the Main function.  It sets up the TKinter window. It takes the systems display size and uses that to create a window to a relative size.  It also uses the bind and configure TK functions
		to set up a scroll bar.  This is used for scrolling throught results.  The GUI sets up the following:
		1. Open JSON button - calls OPJSON function
		2. Export Map button - calls OPMAP function
		3. Map Type Combobox - changes what mode is sent to OPMAP to alter what kind of map is produced
		4. Search Box - Overwriting the normal TK function using "return 'break'", the searchbar is able to be activated with the return key.  It uses REGEX as well.
		5. Search Button - Alternative to using return,  calls results() using what is in the searchbox as a parameter
		6. Template Combo Box - Can be used to search data for crime types. Uses the <<comboboxselected>> binding to perform searches using Results() and REGEX for specific words.

		Most of the GUI is in Grid format, but some aspects are using pack() to make it look prettier. :)
	'''
	gui.title("Twitter Analyzer") 
	canvas = Canvas(gui, borderwidth=0, background="#ffffff")
	Label(gui, text="TWITTER ANALYSIS TOOL BY DATA COHEN", bg="#1da1f2", fg="white").pack(fill=X)
	toolframe = Frame(gui, background="#1da1f2")
	toolframe.pack(fill=X)
	Label(toolframe, text="Export to Map: ", bg="#1da1f2", fg="white").grid(row=1, column=2)
	mapmakebutton = Button(toolframe, text="Export", command=lambda: OPMap(maptypebox.current())).grid(row=1,column=3)
	maptypebox = ttk.Combobox(toolframe, values=["Plotted Map", "Heat Map"])
	maptypebox.grid(row=1, column=4, padx=(10,10))
	maptypebox.current(0)
	frame = Frame(canvas, background="#ffffff") 
	frame.columnconfigure(0, weight = 1)
	frame.rowconfigure(0,weight = 1)
	scrolly = Scrollbar(gui, orient="vertical", command=canvas.yview) 
	canvas.configure(yscrollcommand=scrolly.set)
	scrolly.pack(side="right", fill="y")
	canvas.pack(side="top", fill="both", expand=True) 
	canvas.create_window((4,4), window=frame, anchor="nw")
	frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas)) 
	swidth = gui.winfo_screenwidth()
	sheight = gui.winfo_screenheight()
	windowsize = str((int(swidth*0.70))) + "x" + str((int(sheight*0.5))) 
	gui.geometry(windowsize) 
	Label(toolframe, text="Open JSON File: ", bg="#1da1f2", fg="white").grid(row=1, column=0)
	opjsonbutton = Button(toolframe, text="Open Tweets", command=lambda: OPJSON()).grid(row=1,column=1, padx=(5,5))
	Label(toolframe, text="           Search: ", bg="#1da1f2", fg="white").grid(row=1, column=5)
	searchbox1 = Text(toolframe, height = 1, width=20)
	searchnbutton = Button(toolframe, text="Search", command=lambda: Results(frame, searchbox1.get("1.0", "end-1c"))).grid(row=1,column=7)
	searchbox1.grid(row=1, column=6, padx=(10, 10))
	searchbox1.bind('<Return>',lambda event: Results(frame, searchbox1.get("1.0", "end-1c")))
	Label(toolframe, text="Predefined Templates: ", bg="#1da1f2", fg="white").grid(row=1, column=8)
	templatetype = ttk.Combobox(toolframe, values=["Violent Crime", "Non-violent Crime"])
	templatetype.grid(row=1, column=9, padx=(10,10))
	templatetype.current(0)
	templatetype.bind('<<ComboboxSelected>>', lambda event: templatesearch(templatetype.current(),frame))
	gui.mainloop()
main()
