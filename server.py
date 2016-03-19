#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Project 1

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.

"""

import os
import re
import requests
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following uses the sqlite3 database test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@w4111db1.cloudapp.net:5432/proj1part2
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@w4111db1.cloudapp.net:5432/proj1part2"
#
DATABASEURI = "postgresql://mlh2197:389@w4111db1.cloudapp.net:5432/proj1part2"
#DATABASEURI = "postgresql://wvb2103:389@w4111db1.cloudapp.net:5432/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)

#
# START SQLITE SETUP CODE
#
# after these statements run, you should see a file test.db in your webserver/ directory
# this is a sqlite database that you can query like psql typing in the shell command line:
# 
#     sqlite3 test.db
#
# The following sqlite3 commands may be useful:
# 
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table
# 
# The setup code should be deleted once you switch to using the Part 2 postgresql database
#
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")
#
# END SQLITE SETUP CODE
#



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a POST or GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
# 

"""
@app.route('/', methods=["POST", "GET"])
def index():
  
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict( data = names )


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)
"""

# Check guards for uid
# Error code 1: uid empty before regex
# Error code 2: uid empty after regex
# Error code 3: uid is taken
def validate_uid(uid, signup):
    if (len(uid) < 1):
	return 1

    # User IDs contain only numbers
    uid = re.sub("[^0-9]", "", uid.strip())	
    if (len(uid) < 1): # User ID must contain one or more numbers
	return 2
    uid = int(uid)
    
    # Only check this if the user is signing up
    if (signup):
    	# Check if a user with this user ID already exists
   	cursor = g.conn.execute("SELECT * FROM Users;")
   	for result in cursor:
            if int(uid) == int(result['uid']):
	        return 3
        cursor.close()
    return 0 # no error

# Check guards for vid
# Error code 1: vid empty before regex
# Error code 2: vid empty after regex
# Error code 3: vid is taken
def validate_vid(vid, addvideo):
    if (len(vid) < 1):
	return 1
        
    # Video IDs contain only numbers 
    vid = re.sub("[^0-9]", "", vid.strip())
    if (len(vid) < 1): # User ID must contain one or more numbers
	return 2
    vid = int(vid)

    # Only check this if the user is adding a video
    if (addvideo):
	# Check if a video with this video ID already exists
	cursor = g.conn.execute("SELECT * FROM Videos;")
	for result in cursor:
	    if int(vid) == int(result['vid']):
		return 3
	cursor.close()
    return 0 # no error

# Check guards for lid
# Error code 1: lid empty before regex
# Error code 2: lid empty after regex
# Error code 3: lid is taken
def validate_lid(lid, addlist):
    if (len(lid) < 1):
	return 1
        
    # List IDs contain only numbers 
    lid = re.sub("[^0-9]", "", lid.strip())
    if (len(lid) < 1): # User ID must contain one or more numbers
	return 2
    lid = int(lid)

    # Only check this if the user is adding a video
    if (addlist):
	# Check if a video with this video ID already exists
	cursor = g.conn.execute("SELECT * FROM Lists;")
	for result in cursor:
	    if int(lid) == int(result['listid']):
		return 3
	cursor.close()
    return 0 # no error

# Check to see if the webpage is valid
# Error code 1: this webpage is empty
# Error code 2: the webpage is invalid
def validate_url(webpage):
    if (len(webpage) < 1):
	return 1
    try:
	r = requests.head(webpage, timeout=3.0, allow_redirects=True)
    except:
	return 2
    if r.status_code == 200:
	print "no probs"
	return 0
    print "invalid"
    return 2

# Check to see if the string is valid
# The string can be anything
# Error code 1: this string is empty
def validate_string(string):
    if (len(string) < 1):
	return 1
    return 0    

# Home Page
@app.route('/', methods=["GET"]) 
def load_homepage():
	return render_template("index.html")

    
# User signup page 
@app.route('/signup/', methods=["GET", "POST"])
def user_signup():
    if (request.method == "POST"):
	uid = request.form["userid"]
	firstName = request.form["firstname"]
	lastName = request.form["lastname"]

	# Call validate_uid to do basic uid error-checking
	error_code = validate_uid(uid, True)
	if (error_code == 1):
	    return "User ID cannot be empty"
	elif (error_code == 2):
	    return "Invalid user ID (must contain only numbers)." 
	elif (error_code == 3):
	    return "The user ID " + str(uid) + " is already taken."
	# Use NULLs if no first or last name is specified
	if (len(firstName) < 1):
	    firstName = None
	else: # First and last names should contain only alphabetical characters
	    firstName = re.sub("[\W\d]", "", firstName.strip())
	if (len(lastName) < 1):
	    lastName = None
	else:
	    lastName = re.sub("[\W\d]", "", lastName.strip())

    	# At this point, you have a valid, unique user ID
	q = """INSERT INTO Users(uid, firstName, lastName) VALUES(%s, %s, %s)"""
	g.conn.execute(q, (uid, firstName, lastName))
	return "Created new user with ID: " + str(uid)
    else:
	return render_template("signup.html")

# User add video page
@app.route('/addvideo/', methods=["GET", "POST"])
def add_video():
    if (request.method == "POST"):
	uid = request.form["userid"]
	vid = request.form["vid"]
	lid = request.form["lid"]
	vidtitle = request.form["vidtitle"]
	vidurl = request.form["vidurl"]
	tags = request.form["tags"]
	listname = request.form["list"]

	# Perform input validation for all primary keys
	# Call validate_uid to do basic uid error-checking
	uid_error_code = validate_uid(uid, True)
	if (uid_error_code == 1):
	    return "User ID cannot be empty."
	elif (uid_error_code == 2):
	    return "Invalid user ID (must contain only numbers)." 
	elif (uid_error_code != 3):
	    return "The user ID you entered does not exist."
	
	# Check to see if the video id is valid (do the same checks as uid)
	vid_error_code = validate_vid(vid, True)
	if (vid_error_code == 1):
	    return "Video ID cannot be empty."
	elif (vid_error_code == 2):
	    return "Invalid video ID (must contain only numbers)."
	#elif (vid_error_code == 3):
	#    return "The video ID " + str(vid) + " is already taken."

	# Check to see if the list id is valid (do the same checks as vid)
	lid_error_code = validate_lid(lid, True)
	if (lid_error_code == 1):
	    return "List ID cannot be empty."
	elif (lid_error_code == 2):
	    return "Invalid list ID (must contain only numbers)."
	#elif (lid_error_code == 3):
	#    return "The list ID " + str(lid) + " is already taken."

	# We don't care about tags, video URL, video title unless we are inserting
	# Because for existing videos we only need to validate the vid
	# Insert the new list
	if (lid_error_code != 3):
	    # Check to see if the list name is valid
	    list_title_error_code = validate_string(listname)
	    if (list_title_error_code == 1):
	        return "List title cannot be empty."
	    p = """INSERT INTO Lists(listId, uid, name) VALUES (%s, %s, %s)"""
	    g.conn.execute(p, (lid, uid, listname)) 
	if (vid_error_code != 3):
	    # Validate the remaining parameters
	    # Check to see if the video title is valid
	    vid_title_error_code = validate_string(vidtitle)
	    if (vid_title_error_code == 1):
	        return "Video title cannot be empty."

	    # Check to see if the video url is valid
	    vid_url_error_code = validate_url(vidurl)
	    if (vid_url_error_code == 1):
	        return "Video URL cannot be empty."
	    elif (vid_url_error_code == 2):
	        return "Video URL is invalid."

	    # Check to see if the tag is valid
	    # need to check if the tag, separated by spaces, is a valid thing...no punct of course!	
	    tagArray = tags.split(" ")
	    for i in range(len(tagArray)): # tags should be alphabetical only
	        tagArray[i] = re.sub("[\W\d]", "", tagArray[i].strip())
	
	    newTags = []
	    # Keep only the tags with length > 1
	    # This is the one parameter that can be null
	    for i in range(len(tagArray)):
	        if len(tagArray[i]) > 1:
	            newTags.append(tagArray[i])
	    
	    # Insert the new video
	    q = """INSERT INTO Videos(vid, url, title, tags) VALUES(%s, %s, %s, %s)"""
	    g.conn.execute(q, (vid, vidurl, vidtitle, [','.join(list(newTags))]))
	
	exists = False
        cursor = g.conn.execute("SELECT * FROM Lists_Videos;")
        for result in cursor:
            if int(lid) == int(result['listid']) and int(vid) == int(result['vid']):
                exists = True
        cursor.close()

	if (exists):
	    return "Video with ID: " + str(vid) + " is already in list with ID: " + str(lid)
	# Insert the video into the list
	r = """INSERT INTO Lists_Videos(listId, vid) VALUES(%s, %s) """
	g.conn.execute(r, (lid, vid))
	return "Added video with ID: " + str(vid) + " to list with ID: " + str(lid)
    else:
        return render_template("addvideo.html")

# View list
@app.route('/viewlist/', methods=["GET", "POST"])
def view_list():
    if (request.method == "POST"):
	uid = request.form["userid"]
	# Call validate_uid to do basic uid error-checking
	error_code = validate_uid(uid, True)
	if (error_code == 1):
	    return "User ID cannot be empty"
	elif (error_code == 2):
	    return "Invalid user ID (must contain only numbers)."
	elif (error_code != 3):
	    return "The user ID " + str(uid) + " does not exist."
	# Validate lid
	lid = request.form["lid"]
	lid_error_code = validate_lid(lid, True)
        if (lid_error_code == 1):
            return "List ID cannot be empty."
        elif (lid_error_code == 2):
            return "Invalid list ID (must contain only numbers)."
        elif (lid_error_code != 3):
            return "The list ID " + str(lid) + " does not exist."
	cursor = g.conn.execute("select c.firstname, c.lastname, c.url, c.title, c.name, c.listid from (select u.uid, u.firstname, u.lastname, b.vid, b.url, b.title, b.listid, b.name from Users u inner join (select v.vid, v.url, v.title, a.listid, a.name, a.uid from Videos v inner join (select l.listid, l.name, l.uid, v.vid from Lists as l inner join Lists_Videos as v on l.listid = v.listid where l.uid = %s) a on v.vid = a.vid) b on u.uid = b.uid) c;", (uid))	
	count = 0
	output = ""
	for result in cursor:
	    if int(result['listid']) == int(lid):
		if count == 0:
		    firstName = result['firstname'].strip()
		    lastName = result['lastname'].strip()
		    channel = result['name'].strip()
		    output += channel + " (owner: " + firstName + " " + lastName + ")<br/>"
		    count += 1
		video = result['title'].strip()
		url = result['url'].strip()
		output += video + ": " + url + "<br/>"
	if count == 0:
	    return "User " + str(uid) + " does not have a list with ID " + str(lid)
	print output
	return output
    else:
        return render_template("viewlist.html")

    
# User add video page
@app.route('/search/', methods=["GET", "POST"])
def search():
    if (request.method == "POST"):
        vid = request.form["vid"]
        vidtitle = request.form["vidtitle"]
        vidurl = request.form["vidurl"]
        tags = request.form["tags"]
	print "hi"
	print vidurl
	if (len(vid) < 1 and len(vidtitle) < 1 and len(vidurl) < 1 and len(tags) < 1):
	    return "You did not search for anything."

        # Check to see if the video id is valid (do the same checks as uid)
        vid_error_code = validate_vid(vid, True)
       	if (vid_error_code == 2):
            return "Invalid video ID (must contain only numbers)."		
        if(vid_error_code==3 and vid_error_code != 1):
            q = 'SELECT s.title, s.vid, s.url, s.tags FROM Videos s WHERE vid=%s;'
	    cursor = g.conn.execute(q, (vid))
	    output = ""
	    #count = 0
	    for result in cursor:
		url = result['url'].strip()
		title = result['title']
		ttags = result['tags']
		output += title + ": " + str(url) + "<br/>"
		#count += 1
		if (ttags):
		    for i in range(len(ttags)):
			if i == 0: 
			    output += "    tags: "
		    	output += str(ttags[i]) + " "
		output += "<br/>"
		#output += str(result)
	    #if (count == 0):
		#return "Your search yielded no results."
            return output

        if (vid and vid_error_code != 3):
            return "Vid does not exist."
	print "alive"
        # Check to see if the video title is valid
        vid_title_error_code = validate_string(vidtitle)
        vid_title_present = (vid_title_error_code != 1)

        # Check to see if the video url is valid
        print "Checking valid url"
	vid_url_error_code = validate_url(vidurl)
        if (vid_url_error_code == 2): 
	    return "You presented an invalid url."
	print "it's good url"
	vid_url_present = (vid_url_error_code != 1)
        # Check to see if the tag is valid
        # need to check if the tag, separated by spaces, is a valid thing...no punct of course!	
        tagArray = tags.split(" ")
        print "tagarray: " 
	print tagArray
	for i in range(len(tagArray)): # tags should be alphabetical only
            tagArray[i] = re.sub("[\W\d]", "", tagArray[i].strip())
	print "new tags: " 
	print tagArray
        newTags = []
        # Keep only the tags with length > 1
        # This is the one parameter that can be null
        for i in range(len(tagArray)):
            if len(tagArray[i]) > 1:
                newTags.append(tagArray[i])
	print "survived up to here"
        tags_present = (len(newTags) != 0);
	
        # List the videos
	count = 0
        q = """SELECT * FROM Videos WHERE """
        if(vid_title_present):
	    vidtitle = "%" + vidtitle + "%"
            q = q + """title ilike %s"""
	    print q
	    print "About to execute title"
	    cursor = g.conn.execute(q, (vidtitle))
	    output = ""
	    for result in cursor:
		url = result['url'].strip()
		title = result['title']
		ttags = result['tags']
		output += title + ": " + str(url) + "<br/>"
		count += 1
		if (ttags):
		    for i in range(len(ttags)):
			if i == 0: 
			    output += "    tags: "
		    	output += str(ttags[i]) + " "
		output += "<br/><br/>"
		#output += str(result)
	    print output
	    if count == 0:
		return "No results for this search."
	    return output    
        elif(vid_url_present):
    	    q = q + """url=%s"""
            print q
	    print "About to execute url"
	    cursor = g.conn.execute(q, (vidurl))
	    output = ""
	    for result in cursor:
		url = result['url'].strip()
		title = result['title']
		ttags = result['tags']
		output += title + ": " + str(url) + "<br/>"
		count += 1
		if (ttags):
		    for i in range(len(ttags)):
			if i == 0: 
			    output += "    tags: "
		    	output += str(ttags[i]) + " "
		output += "<br/><br/>"
		#output += str(result)
	    if count == 0:
		return "No results for this search."
	    print output
	    return output 
        elif(tags_present):
	    cursor = g.conn.execute("""SELECT * FROM Videos""");
	    output = ""
	    for result in cursor:
		result_tags = result['tags']
		try:	
		    result_two = "%s" % "','".join(result_tags)
		    new_result_tags = result_two.split(",")
		except:
		    continue
		print newTags
		print new_result_tags
		for i in range(len(newTags)):
		    if (newTags[i] in new_result_tags):
			url = result['url'].strip()
			title = result['title']
			ttags = result['tags']
			output += title + ": " + str(url) + "<br/>"
			count += 1
		    	for i in range(len(result_tags)):
			    if i == 0: 
			        output += "    tags: "
		    	    output += str(result_tags[i]) + " "
			output += "<br/><br/>"
	    if count == 0:
		return "No results for this search."
	    return output
	 #q = """SELECT * FROM Videos WHERE title=%s"""
        #g.conn.execute(q, (vidtitle))
	
        #q = """SELECT * FROM Videos WHERE url=%s"""
        #g.conn.execute(q, (vidurl))
	
        #q = """SELECT * FROM Videos WHERE tags CONTAIN %s"""
        #g.conn.execute(q, (vid, vidurl, vidtitle, [','.join(list(newTags))]))
	
        #g.conn.execute(r, (lid, vid))
        return "Results for Added video with ID: " + str(vid) + " to  with ID: " + str(lid)
    else:
	return render_template("search.html") 

# User add video page
@app.route('/review/', methods=["GET", "POST"])
def review():
    if (request.method == "POST"):
	print "HI"
        uid = request.form["userid"]
	vid = request.form["vid"]
	review = request.form["review"]

	# Perform input validation for all primary keys
	# Call validate_uid to do basic uid error-checking
	uid_error_code = validate_uid(uid, True)
	if (uid_error_code == 1):
            return "User ID cannot be empty."
	elif (uid_error_code == 2):
	    return "Invalid user ID (must contain only numbers)." 
	elif (uid_error_code != 3):
            return "The user ID you entered does not exist."
	
	# Check to see if the video id is valid (do the same checks as uid)
	vid_error_code = validate_vid(vid, True)
	if (vid_error_code == 1):
	    return "Video ID cannot be empty."
	elif (vid_error_code == 2):
	    return "Invalid video ID (must contain only numbers)."
	elif (vid_error_code != 3):
	    return "The video ID " + str(vid) + " does not exist."
    
	# Check if a video with this video ID already exists
	cursor = g.conn.execute("SELECT * FROM users_reviews;")
	for result in cursor:
	    if ((int(uid) == int(result['uid'])) and (int(vid) == int(result['vid']))):
		return "Cannot submit more than one review for a video."
	cursor.close()
    
	# Check to see if the video id is valid (do the same checks as uid)
	if (not review):
	    return "Empty review cannot be added to database."

	# Insert the new review
	q = """INSERT INTO users_reviews(uid, vid, review) VALUES(%s, %s, %s)"""
	g.conn.execute(q, (uid, vid, review))

        return "Added review with ID: (" + str(uid) + "," + str(vid) + ") to video with ID: " + str(vid)
    
    else:
    	return render_template("review.html")
	
# Get ratings and reviews
@app.route('/getfeedback/', methods=["GET", "POST"])
def get_feedback():
    if (request.method == "POST"):
        vid = request.form["vid"]
    	vid_error_code = validate_vid(vid, True)
	if (vid_error_code == 1):
	    return "Video ID cannot be empty."
	elif (vid_error_code == 2):
	    return "Invalid video ID (must contain only numbers)."
	elif (vid_error_code != 3):
	    return "The video ID " + str(vid) + " does not exist."
	
	q = """SELECT r.star, v.title from users_ratings r inner join Videos v on r.vid = v.vid WHERE v.vid=%s"""	
	cursor = g.conn.execute(q, (vid))
	print "execute2"
	q2 = """SELECT r.review, v.title from users_reviews r inner join Videos v on r.vid = v.vid WHERE v.vid=%s"""	
	cursor2 = g.conn.execute(q2, (vid))
	print "executed"
	output = ""
	counting = 0
	print "hi"
	numRecords = 0
	for result1 in cursor:
	    print result1
	    if counting == 0:
		output += result1["title"] + "<br/>" + "Ratings: " + "<br/>"
		counting += 1
	    output += str(result1["star"]) + "<br/>"
	    numRecords += 1
	output += "<br/>"
	count = 0
	for result in cursor2:
	    if count == 0:
	    	output += "Reviews: " + "<br/>"
		count += 1
	    output += result["review"] + "<br/>"
	    numRecords += 1
	if (numRecords < 1):
	    return "No ratings and reviews for this video."
	return output
    else:
	return render_template("get_reviews.html")	

# User add rating for video
@app.route('/rate/', methods=["GET", "POST"])
def rate():
    if (request.method == "POST"):
	uid = request.form["userid"]
	vid = request.form["vid"]
	rate = request.form["rate"]

	# Perform input validation for all primary keys
	# Call validate_uid to do basic uid error-checking
	uid_error_code = validate_uid(uid, True)
	if (uid_error_code == 1):
		return "User ID cannot be empty."
	elif (uid_error_code == 2):
		return "Invalid user ID (must contain only numbers)." 
	elif (uid_error_code != 3):
		return "The user ID you entered does not exist."

	# Check to see if the video id is valid (do the same checks as uid)
	vid_error_code = validate_vid(vid, True)
	if (vid_error_code == 1):
		return "Video ID cannot be empty."
	elif (vid_error_code == 2):
		return "Invalid video ID (must contain only numbers)."
		
	# Check if a video with this video ID already exists
	cursor = g.conn.execute("SELECT * FROM users_ratings;")
	for result in cursor:
	    if ((int(uid) == int(result['uid'])) and (int(vid) == int(result['vid']))):
		return "Cannot submit more than one ratings for a video."
	cursor.close()
   
	#Check if rate is number between 0 and 5.
        if(not rate):
	    return "Empty rate cannot be added to database."
	print "Try it"
	
	star = re.sub("[^0-9]", "", rate.strip())
	# Insert the new rate
	q = """INSERT INTO users_ratings(uid, vid, star) VALUES(%s, %s, %s)"""
	g.conn.execute(q, (uid, vid, rate))
        print "executed"
	return "Added rating with ID: (" + str(uid) + "," + str(vid) + ") to video with ID: " + str(vid)
    
    else:
        return render_template("rate.html")



#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another/
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
"""
@app.route('/another/', methods=["POST", "GET"])
def another():
  return render_template("anotherfile.html")
"""

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=9001, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
