#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Create a sqlite database from separate json, and html files

import logging
from logging.handlers import RotatingFileHandler
import os
import sys
#import sqlite3
import MySQLdb
import MySQLdb.cursors
import re
import fnmatch
import json

MENU_BASE = "/library/www/html/js-menu/menu-files/menu-defs"
ICON_BASE = "/library/www/html/js-menu/menu-files/images"
ASSET_BASE = "/library/www/html/common/assets"
KIWIX_CAT = ASSET_BASE + '/kiwix_catalog.json'
DOWNLOADED_ZIMS = ASSET_BASE + '/zim_version_idx.json'

os.chdir(MENU_BASE)


# Get the IIAB variables
sys.path.append('/etc/iiab/')
from iiab_env import get_iiab_env
doc_root = get_iiab_env("WWWROOT")

columns = ['menu_item_name','description','title','extra_html',
           'lang','zim_name','logo_url','intended_use','moddir',
           'start_url','apk_file','apk_file_size']

# Globals
zims ={}

# ########## database operations ##############
conn = MySQLdb.connect(host="localhost",
                     cursorclass=MySQLdb.cursors.DictCursor, 
                     charset="utf8",
                     user="menus_user",
                     passwd="g0adm1n",
                     db="menus_db")
if not conn:
       print("failed to open mysql database")
       sys.exit(1)
c = conn.cursor()
"""
c.execute('truncate menus')

# ########## Transfer the values  ##############
keys=[]
for filename in os.listdir('.'):
   if fnmatch.fnmatch(filename, '*.json'):
      nameval = filename[:-5]
      # skip over this file if it exists in database
      rows = c.execute("select name from menus where name = %s",(nameval,))
      if not rows:
         # make sure record exists
         sql = "INSERT IGNORE INTO menus SET name=%s"
         #print(sql)
         c.execute(sql,(nameval,)) 
         with open(filename) as json_file:  
             reads = json_file.read()
             data = json.loads(reads)
             for col in columns:
                if col in data.keys():
                   updstr = data[col].replace("'","''")
                   sql = "UPDATE menus set " + col + " = %s where name = %s"
                   try:
                     c.execute(sql,(updstr,nameval,))
                   except MySQLdb.Error as e:
                     print str(e)
                     print sql
                          
             instr = ''
             lines = reads.split('\n')
             for line in lines:
                line = line.rstrip('\n')
                line = line.rstrip('\r')
                line = line.rstrip('\n')
                line = line.lstrip(' ')
                instr += line
             updstr = instr.replace("'","''")
             #updstr = instr.replace('\\"','\\\\"')
             sql = "UPDATE menus set js = %s where name = %s"
             try:
               c.execute(sql,(updstr,nameval,))
             except MySQLdb.Error as e:
               print str(e)
               print sql
   if fnmatch.fnmatch(filename, '*.html'):
      nameval = filename[:-5]
      if True:
         with open(filename) as html_file:  
             reads = html_file.read()
             updstr = reads.replace("'","''")
             sql = "UPDATE menus set extra_html = %s where name = %s"
             try:
               c.execute(sql,(updstr,nameval))
             except MySQLdb.Error as e:
               print str(e)
               print sql
                          
   conn.commit()
# Get the images

# scan through the menus getting the list of icon names
os.chdir(ICON_BASE)
sql = "SELECT logo_url,name from menus"
num = c.execute(sql)
rows = c.fetchall()
for row in rows:
   if row and row['logo_url']:
      if os.path.isfile("./%s"%row['logo_url']):
         with open(row['logo_url']) as icon_file:  
            try:
               reads = icon_file.read()
               sql = "UPDATE menus SET icon = %s where name = %s"
               c.execute(sql,(reads,row['name'],))
            except Exception as e:
               print str(e)
               print("Logo_url error: %s"%row['logo_url'])
      else:
         print("logo_url file missing:%s"%row['logo_url'])
conn.commit()
# get mysql column names for kiwix catalog
sql = 'select * from modules limit 1'
c.execute(sql)
fields =[i[0] for i in c.description]
#print("fields in database: " + str(fields))

# start loading the table with a fresh start                          
c.execute('truncate modules')

# Read the kiwix catalog
with open(KIWIX_CAT, 'r') as kiwix_cat:
   json_data = kiwix_cat.read()
   download = json.loads(json_data)
   zims = download['zims']
   for uuid in zims.keys():
      # create a modules record with this uuid
      sql = "INSERT IGNORE INTO modules SET uuid=%s"
      c.execute(sql,(uuid,))
      for col in zims[uuid].keys():
         if col in fields:
             sql = "UPDATE modules set " + col + " = %s where uuid = %s"
             #print("UPDATE modules set %s = %s where uuid = %s"%(col,zims[uuid][col],uuid,))
             try:
               c.execute(sql,(zims[uuid][col],uuid,))
             #except MySQLdb.Error as e:
             except Exception as e:
               print str(e)
               print sql

   conn.commit()
"""
# read throug the downloaded zim versions and print out the menu names
with open(DOWNLOADED_ZIMS, 'r') as down_fp:
   json_data = down_fp.read()
   dload = json.loads(json_data)
   outstr = '{'
   for key in dload.keys():
      #print(key,dload[key])
      sql = 'SELECT name, zim_name from menus where zim_name = %s'
      c.execute(sql,(key,))
      rv = c.fetchone()
      if rv and rv['name']:
         outstr += '   "' + dload[key] + '": "' + rv['name'] + '",\n'
   outstr = outstr[:-2]
   outstr += '\n'
   outstr += '}'
   print outstr
conn.close()
