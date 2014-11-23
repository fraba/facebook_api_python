#!/usr/bin/env python

# fun.py

# This function assumes a SQLite database with schema detailed in createdb.py and a
# well formed Python dictionary obtained with requests.get().json() to the Facebook API
# Due to relational tables dependencies, functions must be called in this order.

import sys, os, inspect
import json
import smtplib
import html2text
import types
import sqlite3
import requests
import re
from random import randint
from time import sleep, strftime, strptime

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

## Main function
def scrapeFbObject(OBJECT_ID, ACCESS_TOKEN, DB, keep_paginating, mail_spec, since=''):

    # This shouldn't be changed
    BASE_URL = 'https://graph.facebook.com/v2.1/'
    url = '%s%s/feed/?access_token=%s&since=%s' % (BASE_URL, OBJECT_ID, ACCESS_TOKEN, since)

    # Check nrow (posts, comments, profiles)
    numberRecords = checkNumberRecords(DB)

    response = requests.get(url).json()
    response = manageApiResponse(response, url, DB)

    # Quit if API returns any error
    if 'error' in response:
        msg = composeMailMessage(response['error'].get('message'), OBJECT_ID, True, False, DB)
        sendMail(mail_spec['me'], mail_spec['you'], mail_spec['pwd'], msg)
        print('Execution terminated. API returned: ' + response['error'].get('message'))
        return

    print 'Parsing object ' + OBJECT_ID + '...' 
    
    parseFbProfile(response, DB)
    parseFbApplication(response, DB)
    parseFbPost(response, DB)
    parseFbComment(response, DB, BASE_URL, ACCESS_TOKEN)

    if keep_paginating == True:
        counter = 1
        while True:
            try:
                # Try to request additional pages if present
                url = response['paging']['next']
            
                response = requests.get(url).json()
            
                response = manageApiResponse(response, url, DB)
                if 'error' in response:
                    msg = composeMailMessage(response['error'].get('message'), OBJECT_ID, True, False, DB)
                    sendMail(mail_spec['me'], mail_spec['you'], mail_spec['pwd'], msg)
                    print('Execution terminated. API returned: ' + response['error'].get('message'))
                    return

                counter += 1     
                print 'Parsing page ' + str(counter) + ' from ' + OBJECT_ID + '...' 
            
                parseFbProfile(response, DB)
                parseFbApplication(response, DB)
                parseFbPost(response, DB)
                parseFbComment(response, DB, BASE_URL, ACCESS_TOKEN)
                # Sleep few seconds
                sleep(randint(1,15))
                # Every mail_msg_threshold send email
                if (counter % mail_spec['msg_threshold'] == 0):
                    #send email with numberRecords
                    numberRecords_ante = numberRecords
                    numberRecords = checkNumberRecords(DB)
                    parsed_posts = numberRecords[0] - numberRecords_ante[0]
                    parsed_comments = numberRecords[1] - numberRecords_ante[1]
                    parsed_profile = numberRecords[2] - numberRecords_ante[2]
                    diff_records = [parsed_posts, parsed_comments, parsed_profile] 
                    msg = composeMailMessage(diff_records, OBJECT_ID, False, False, DB)
                    sendMail(mail_spec['me'], mail_spec['you'], mail_spec['pwd'], msg)
                
            except KeyError:
                # Break the while at the last page
                break
        # Uncomment to send email    
        # numberRecords = checkNumberRecords(DB)    
        # msg = composeMailMessage(numberRecords, OBJECT_ID, False, True, DB)
        # sendMail(mail_spec['me'], mail_spec['you'], mail_spec['pwd'], msg)       
        print('I parsed ' + str(counter) + ' pages from ' + OBJECT_ID + ".")
        return
    
    else:
        # Uncomment to send email at the end
        # numberRecords = checkNumberRecords(DB)
        # msg = composeMailMessage(numberRecords, OBJECT_ID, False, True, DB)
        # sendMail(mail_spec['me'], mail_spec['you'], mail_spec['pwd'], msg)  
        print ('I parsed only one page from ' + OBJECT_ID + ".")
        return
        

def enterLog(dict, request, db):
    
    if 'error' in dict:
        error = dict.get('error')
        response = 'error'
        error_message = error.get('message').encode('utf-8')
        error_type = error.get('type').encode('utf-8')
        error_code = error.get('code')
    else:
        response = 'OK'
        error_message = ''
        error_type = ''
        error_code = ''

    conn = sqlite3.connect(db, timeout=10)
    conn.text_factory = str
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO log (request_string, response, error_message, error_type, error_code) VALUES (?, ?, ?, ?, ?)", (request, response, error_message, error_type, error_code))

    conn.commit()

    return

def parseFbProfile(dict, db):

    data = dict['data']

    for item in data:
        try:
            # Main post
            id = item['from'].get('id','').encode('utf-8')
            name = item['from'].get('name','').encode('utf-8')
            category = item['from'].get('category','').encode('utf-8')

            conn = sqlite3.connect(db, timeout=10)
            conn.text_factory = str
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO profile (id, name, category) VALUES (?, ?, ?)", (id, name, category))

            # Comments
            if 'comments' in item:
                comments = item.get('comments')
                comment_data = comments.get('data')
                for item_comment in comment_data:
                    id = item_comment['from'].get('id','').encode('utf-8')
                    name = item_comment['from'].get('name','').encode('utf-8')
                    cursor.execute("INSERT OR IGNORE INTO profile (id, name) VALUES (?, ?)", (id, name))

            # Likes
            if 'likes' in item:
                likes = item.get('likes')
                like_data = likes.get('data')
                for like_item in like_data:
                    id = like_item.get('id','').encode('utf-8')
                    name = like_item.get('name','').encode('utf-8')
                    cursor.execute("INSERT OR IGNORE INTO profile (id, name) VALUES (?, ?)", (id, name))     

            conn.commit()
        except Exception,e:
            print str(e)
            pass
           

    return

def parseFbApplication(dict, db):

    data = dict['data']

    for item in data:
        try:
            if 'application' in item:
                id = item['application'].get('id','').encode('utf-8')
                name = item['application'].get('name','').encode('utf-8')
                namespace = item['application'].get('namespace','').encode('utf-8')

                conn = sqlite3.connect(db, timeout=10)
                conn.text_factory = str
                cursor = conn.cursor()
                cursor.execute("INSERT OR IGNORE INTO application (id, name, namespace) VALUES (?, ?, ?)", (id, name, namespace))
                conn.commit()

        except Exception,e:
            print str(e)
            pass
                
    return

def parseFbPost(dict, db):

    data = dict['data']

    for item in data:
        try:
            # Post
            id = item.get('id','').encode('utf-8')
            created_time = item.get('created_time','').encode('utf-8')
            print ('Post created at ' + created_time + '.')
            if 'application' in item:
                application_id = item['application'].get('id','').encode('utf-8')
            else:
                application_id = ''
            description = item.get('description','').encode('utf-8')
            from_ = item['from'].get('id','').encode('utf-8')
            # Check if any target profile and parse them all
            if 'to' in item:
                to_ = item['to']['data']
                for target in to_:
                    target_name = target.get('name','').encode('utf-8')
                    target_id = target.get('id','').encode('utf-8')
                    conn = sqlite3.connect(db, timeout=10)
                    conn.text_factory = str
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO [to] (post_id, profile_id) VALUES (?, ?)", (id, target_id))
                    cursor.execute("INSERT OR IGNORE INTO profile (id, name) VALUES (?, ?)", (target_id, target_name)) 
                    conn.commit()
            link = item.get('link','').encode('utf-8')
            name = item.get('name','').encode('utf-8')
            picture = item.get('picture','').encode('utf-8')
            status_type = item.get('status_type','').encode('utf-8')
            story = item.get('story','').encode('utf-8')
            type_ = item.get('type','').encode('utf-8')
            updated_time = item.get('updated_time','').encode('utf-8')
            caption = item.get('caption','').encode('utf-8')
            icon = item.get('icon','').encode('utf-8')
            message = item.get('message','').encode('utf-8')
            object_id = item.get('object_id','').encode('utf-8')
            if 'place' in item:
                place = item['place'].get('id','').encode('utf-8')
            else:
                place = ''
            source = item.get('source','').encode('utf-8')

            conn = sqlite3.connect(db, timeout=10)
            conn.text_factory = str
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO post (id, created_time, application, description, [from], link, name, picture, status_type, story, type, updated_time, caption, icon, message, object_id, place, source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, created_time, application_id, description, from_, link, name, picture, status_type, story, type_, updated_time, caption, icon, message, object_id, place, source))

            # Comments ## If you modify this, also modiy following function
            if 'comments' in item:
                comments = item.get('comments')
                comment_list = comments.get('data')

                enterFbComment(cursor, comment_list, id)

            # Likes
            if 'likes' in item:       
                likes = item.get('likes')
                like_data = likes.get('data')
                for like_item in like_data:
                    liker_id = like_item.get('id','').encode('utf-8')
                    cursor.execute("INSERT OR IGNORE INTO post_likes (post_id, profile_id) VALUES (?, ?)", (id, liker_id))  
        
            conn.commit()

        except Exception,e:
            print str(e)
            pass
      
    return


def enterFbComment(cursor, comment_list, post_id):
    for comment_item in comment_list:
        try:
            from_ = comment_item['from'].get('id','').encode('utf-8')
            created_time = comment_item.get('created_time','').encode('utf-8')
            comment_id = comment_item.get('id','').encode('utf-8')
            like_count = comment_item.get('like_count','')
            message = comment_item.get('message','').encode('utf-8')
            can_remove = comment_item.get('can_remove','')
            if 'attachment' in comment_item:
                attachment = comment_item.get('attachment','')
                attachment_url = attachment.get('url','').encode('utf-8')
            else:
                attachment_url = ''  
            can_comment =  comment_item.get('can_comment','')
            comment_count = comment_item.get('comment_count','')
            user_likes =  comment_item.get('user_likes','')
            if 'parent' in comment_item:
                parent = comment_item['parent'].get('id','').encode('utf-8')
            else:
                parent = ''      
            cursor.execute("INSERT OR IGNORE INTO comment (id, attachment_url, can_comment, comment_count, created_time, [from], message, like_count, can_remove, user_likes, post_id, parent) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (comment_id, attachment_url, can_comment, comment_count, created_time, from_, message, like_count, can_remove, user_likes, post_id, parent))

        except Exception,e:
            print str(e)
            pass

    return

def parseFbComment(dict, db, BASE_URL, ACCESS_TOKEN):

    data = dict['data']

    for item in data:
        try:
            id = item.get('id','').encode('utf-8')
            fields = 'id,from,created_time,like_count,message,can_remove,attachment,can_comment,comment_count,user_likes,parent.fields(id)'
            # Request comments with replies
            url = '%s%s/comments/?filter=stream&limit=100&fields=%s&access_token=%s' % (BASE_URL, id, fields, ACCESS_TOKEN,)

            response = requests.get(url).json()
            response = manageApiResponse(response, url, db)
            if 'error' in response:
                print "API returned: \"" + response['error'].get('message') + "\" while trying to parse comments for this post. Skipping to next post..."
                continue

            # print 'Parsing comment page of ' + id + '...'

            comment_list = response['data']

            conn = sqlite3.connect(db, timeout=10)
            conn.text_factory = str
            cursor = conn.cursor()
        
            enterFbComment(cursor, comment_list, id)

            conn.commit()

            counter = 1
            while True:
                try:
                    # Try to request additional pages if present
                    url = response['paging']['next']
            
                    response = requests.get(url).json()
                    response = manageApiResponse(response, url, db)
                    if 'error' in response:
                        print "API returned: \"" + response['error'].get('message') + "\" while trying to parse additional pages for comments. Skipping to next post..."
                        break

                    comment_list = response['data']

                    counter += 1     
                    # print 'Parsing comment page ' + str(counter) + ' from ' + id + '...'

                    conn = sqlite3.connect(db, timeout=10)
                    conn.text_factory = str
                    cursor = conn.cursor()

                    enterFbComment(cursor, comment_list, id)

                    conn.commit()
            
                    # Sleep few seconds
                    sleep(randint(1,5))
                except KeyError:
                    # Break the while at the last page
                    break
           
            print 'I parsed ' + str(counter) + ' comment page(s) from ' + id
            
        except Exception,e:
            print str(e)
            pass
            
    return
    
def checkNumberRecords(db):

    conn = sqlite3.connect(db, timeout=10)
    conn.text_factory = str
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM post')
    n_posts = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM comment')
    n_comments = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM profile')
    n_profiles = cursor.fetchone()[0]

    list = [n_posts, n_comments, n_profiles]

    conn.close()
    
    return list

# Expect three arguments: msg (string or list), error (bool), end (bool)
# Return an html formatted string
def composeMailMessage(info, object_id, error, end, db):

    if error == True:
        html = "<p>Hi!<br>Here the bot parsing \"" + object_id + "\"<br>Something went wrong and the error message is<br><br>" + str(info) + "</p>"
        return html
    
    elif (end == True) and isinstance(info, list):
        html = "<p>Hi!<br>Here the bot parsing Facebook object \"" + object_id + "\"<br>I finshed my job.</br>The database contains:<br>Posts: " + str(info[0]) + "<br>Comments: " + str(info[1]) + "<br>Profiles: " + str(info[2]) + "<br>Have a nice day.</p>"
        return html
           
    elif (end == False) and isinstance(info, list):
        html = "<p>Hi!<br>Here the bot parsing Facebook object \"" + object_id + "\"<br>Here the number of records added to the database since the last email:<br>Posts: " + str(info[0]) + "<br>Comments: " + str(info[1]) + "<br>Profiles: " + str(info[2]) + "</p>"
        return html

    else:
        html = "p>Hi!<br>Here the bot parsing Facebook object \"" + object_id + "\"<br>Something went wrong composing your email message.</p>"
        return html

def sendMail(me, you, pwd, html):

    try:
    
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Stats from your script"
        msg['From'] = me
        msg['To'] = you 

        # Create the body of the message (a plain-text and an HTML version).
        text = html2text.html2text(html)
        html = """\
        <html>
        <head></head>
        <body>
        %s
        </body>
        </html>
        """ % (html)

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        # Send the message via local SMTP server.
        mailServer = smtplib.SMTP("smtp.gmail.com", 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(me, pwd)
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        mailServer.sendmail(me, you, msg.as_string())
        mailServer.close()

    except Exception,e:
        print str(e)
        pass
        
    return

def manageApiResponse(response, url, db):

    # Add request to log
    enterLog(response, url, db)

    if 'error' in response:
        message1 = response['error'].get('message')
        # Attempts 3 times to submit the request
        if response['error'].get('code') == 803:
            return response
        for x in range(0, 3):
            sleep(1)
            response = requests.get(url).json()
            enterLog(response, url, db)
            if 'error' in response:
                message2 = response['error'].get('message')
                if message1 != message2:
                    manageApiResponse(response, url, db)
                else:
                    continue
            else:
                return response
        return response
    return response

def returnLastPageRequest(db):

    conn = sqlite3.connect(db, timeout=10)
    conn.text_factory = str
    cursor = conn.cursor()

    cursor.execute("SELECT request_string FROM log WHERE id = (SELECT MAX(id) FROM (SELECT * FROM log WHERE request_string LIKE '%/feed?access_token=%'));")

    url = cursor.fetchone()[0]

    conn.close()
    
    return url
