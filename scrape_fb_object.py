#!/usr/bin/env python

# scrape_fb_object.py

# Set email coordinates
# me == my email address
# you == recipient's email address
me = ""
you = ""
pwd = ""

# Every how many pages do you want to receive an email?
mail_msg_threshold = 100

mail_spec = {'me' : me, 'you' : you, 'pwd' : pwd, 'msg_threshold' : mail_msg_threshold}

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

call_error_msg = "Error: This script requires at least two arguments, a Facebook object (id or name) and a SQLite database file (possibly asbolute path). E.g. \"python scrape_fb_object.py billgates facebook_store\". The third argument is optional: add \"Yes\" or \"False\" to parse all additional pages."

# Receive the argument from bash or return error message
try:
    OBJECT_ID = sys.argv[1]
except IndexError:
    sys.exit(call_error_msg)
try:         
    DB = sys.argv[2] + '.sqlite'
except IndexError:
    sys.exit(call_error_msg)
    
# Third argument is False by default
try:
    keep_paginating = sys.argv[3]
    if (keep_paginating.lower() == 'true') or (keep_paginating.lower() == 'yes'):
        keep_paginating = True
    else:
        keep_paginating = False      
except IndexError:
    keep_paginating = False


scrapeFbObject(OBJECT_ID, ACCESS_TOKEN, DB, keep_paginating, mail_spec)



