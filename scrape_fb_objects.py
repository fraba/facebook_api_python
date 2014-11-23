#!/usr/bin/env python

# scrape_fb_objects.py

# Set email specification to receive news from the bot
##
# me == my email address
# you == recipient's email address
me = ""
you = ""
pwd = ""
# Every how many pages do you want to receive an email?
mail_msg_threshold = 100
mail_spec = {'me' : me, 'you' : you, 'pwd' : pwd, 'msg_threshold' : mail_msg_threshold}
##

import json
import types
import requests
import sys, os, inspect
from random import randint
from time import sleep
import sqlite3

# Define setting variables
DB = "max_fb.sqlite" # Database to store fb data
targets = sys.argv[1] + '.sqlite' # Database containing target objects
keep_paginating = False # Boolean
##

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

# Loop

while True:
    conn = sqlite3.connect(targets, timeout=10)
    conn.text_factory = str
    cursor = conn.cursor()
    cursor.execute("SELECT object_id FROM target")
    results = cursor.fetchall()

    for result in results:

        try:
            object_id =  result[0]
            print ('FB Object: ' + object_id)
            scrapeFbObject(object_id, ACCESS_TOKEN, DB, True, mail_spec)       
            sleep(15)
        except Exception,e:
            print str(e)
            pass
        
    conn.commit()
 
