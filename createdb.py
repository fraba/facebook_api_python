#!/usr/bin/env python

# createdb.py

# Call it from console passing database filename: python createdb.py filename

import sqlite3
import sys

# Receive the argument from bash
filename = sys.argv[1] + '.sqlite'
 
conn = sqlite3.connect(filename)
 
cursor = conn.cursor()
 
# Create database

# Create tables
cursor.execute("""
-- Table: profile
CREATE TABLE profile ( 
    id        CHAR  PRIMARY KEY,
    name      CHAR,
    category  CHAR,
    --- Type: User, a Page, a Group, an Event
    type      CHAR, 
    timestamp DATETIME DEFAULT ( CURRENT_TIMESTAMP ) 
    );
               """)

cursor.execute("""
CREATE TABLE log ( 
    id             INTEGER  PRIMARY KEY AUTOINCREMENT,
    timestamp      DATETIME NOT NULL
                            DEFAULT ( CURRENT_TIMESTAMP ),
    request_string CHAR     NOT NULL,
    response       CHAR     NOT NULL,
    error_message  CHAR,
    error_type     CHAR,
    error_code     CHAR
    );
               """)

cursor.execute("""
-- Table: post
CREATE TABLE post ( 
    id              CHAR     PRIMARY KEY,
    created_time    DATETIME,
    application  CHAR  REFERENCES application (id),
    description     TEXT,
    [from]          CHAR  REFERENCES profile ( id ),
    link            CHAR,
    name            CHAR,
    picture         CHAR,
    status_type     CHAR,
    story           CHAR,
    type            CHAR,
    updated_time    DATETIME,
    caption         CHAR,
    icon            CHAR,
    message         CHAR,
    object_id       CHAR,
    place           CHAR,
    source          CHAR,
    timestamp       DATETIME DEFAULT ( CURRENT_TIMESTAMP )
    );
               """)

cursor.execute("""
-- Table: comment
CREATE TABLE comment ( 
    id             CHAR     PRIMARY KEY,
    attachment_url CHAR,
    can_comment    CHAR,
    comment_count  INT,
    created_time   DATETIME,
    [from]         CHAR      REFERENCES profile ( id ),
    message        TEXT,
    like_count     INT,
    can_remove     CHAR,
    user_likes     CHAR,
    post_id        CHAR     REFERENCES post ( id ),
    parent         CHAR,
    timestamp      DATETIME DEFAULT ( CURRENT_TIMESTAMP ) 
    );
               """)

cursor.execute("""
-- Table: message_tags
CREATE TABLE message_tags ( 
    id         INTEGER  PRIMARY KEY AUTOINCREMENT,
    post_id    CHAR     REFERENCES post ( id ),
    profile_id CHAR      REFERENCES profile ( id ),
    timstamp   DATETIME DEFAULT ( CURRENT_TIMESTAMP ) 
    );
               """)

cursor.execute("""
-- Table: with_tags
CREATE TABLE with_tags ( 
    id         INTEGER  PRIMARY KEY AUTOINCREMENT,
    post_id    CHAR     REFERENCES post ( id ),
    profile_id CHAR  REFERENCES profile ( id ),
    timestamp  DATETIME DEFAULT ( CURRENT_TIMESTAMP ) 
    );
               """)

cursor.execute("""
-- Table: to
CREATE TABLE [to] ( 
    id         INTEGER  PRIMARY KEY AUTOINCREMENT,
    post_id    CHAR     REFERENCES post ( id ),
    profile_id CHAR  REFERENCES profile ( id ),
    timestamp  DATETIME DEFAULT ( CURRENT_TIMESTAMP ) 
    );
               """)

cursor.execute("""
-- Table: story_tags
CREATE TABLE story_tags ( 
    id         INTEGER  PRIMARY KEY AUTOINCREMENT,
    post_id    CHAR     REFERENCES post ( id ),
    profile_id CHAR      REFERENCES profile ( id ),
    timestamp  DATETIME DEFAULT ( CURRENT_TIMESTAMP ) 
    );
               """)

cursor.execute("""
-- Table: post_likes
CREATE TABLE post_likes ( 
    id         INTEGER  PRIMARY KEY AUTOINCREMENT,
    post_id    CHAR     NOT NULL
                        REFERENCES post ( id ),
    profile_id CHAR  NOT NULL
                        REFERENCES profile ( id ),
    timestamp  DATETIME DEFAULT ( CURRENT_TIMESTAMP ) 
    );
               """)

cursor.execute("""
-- Table: application
CREATE TABLE application ( 
    id         CHAR  PRIMARY KEY,
    name       CHAR,
    namespace  CHAR,
    timestamp  DATETIME DEFAULT ( CURRENT_TIMESTAMP )
    );
               """)

# Close connection
conn.commit()
