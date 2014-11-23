#!/usr/bin/env python

# scrape_fb_object.py

# Set email coordinates
# me == my email address
# you == recipient's email address
me = "lampone.server@gmail.com"
you = "francesco.bailo@sydney.edu.au"
pwd = "xarmxarm82"

# Every how many pages do you want to receive an email?
mail_msg_threshold = 100

import json
import types
import requests
import sys, os, inspect
from random import randint
from time import sleep

# This find path to additional modules in the same directory
# realpath() with make your script run, even if you symlink it :)
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

# use this if you want to include modules from a subforder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"subfolder")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

from fun import *
from local_info import *

DB = sys.argv[1] + '.sqlite'

# This shouldn't be changed
BASE_URL = 'https://graph.facebook.com/v2.1/'
url = returnLastPageRequest(DB)

# Check nrow (posts, comments, profiles)
numberRecords = checkNumberRecords(DB)

response = requests.get(url).json()
response = manageApiResponse(response, url, DB)
if 'error' in response:
    sys.exit('Execution terminated. API returned: ' + response['error'].get('message'))

# Quit if API returns any error
if 'error' in response:
    sendMail(me, you, pwd, response['error'].get('message'))
    sys.exit('Execution terminated. API returned: ' + response['error'].get('message'))

print 'Reboosting pareser...' 
    
parseFbProfile(response, DB)
parseFbApplication(response, DB)
parseFbPost(response, DB)
parseFbComment(response, DB, BASE_URL, ACCESS_TOKEN)

counter = 1
while True:
    try:
        # Try to request additional pages if present
        url = response['paging']['next']
        
        response = requests.get(url).json()

        response = manageApiResponse(response, url, DB)
        if 'error' in response:
            sys.exit('Execution terminated. API returned: ' + response['error'].get('message'))

        counter += 1     
        print 'Parsing page ' + str(counter) 

        parseFbProfile(response, DB)
        parseFbApplication(response, DB)
        parseFbPost(response, DB)
        parseFbComment(response, DB, BASE_URL, ACCESS_TOKEN)
        # Sleep few seconds
        sleep(randint(1,15))
        # Every mail_msg_threshold send email
        if (counter % mail_msg_threshold == 0):
            #send email with numberRecords
            numberRecords_ante = numberRecords
            numberRecords = checkNumberRecords(DB)
            parsed_posts = numberRecords[0] - numberRecords_ante[0]
            parsed_comments = numberRecords[1] - numberRecords_ante[1]
            parsed_profile = numberRecords[2] - numberRecords_ante[2]
            diff_records = [parsed_posts, parsed_comments, parsed_profile] 
            sendMail(me, you, pwd, diff_records)

    except KeyError:
        # Break the while at the last page
        break   

sys.exit('I parsed ' + str(counter) + ' page(s). Execution terminated.')    
