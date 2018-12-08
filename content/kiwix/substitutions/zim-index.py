#!/usr/bin/env python
# -*- coding: utf-8 -*-
# after content is downloaded, create a lookup json with required data

import os
import sys
from fill_db import scrape_kiwix_catalog 
import MySQLdb
import MySQLdb.cursors
import g
import json

def refresh_zim_idx(conn):
   c = conn.cursor()
   with open(g.DOWNLOADED_ZIMS, 'r') as down_fp:
      json_data = down_fp.read()
      dload = json.loads(json_data)
      outstr = '['
      for key in dload.keys():
         #print(key,dload[key])
         #sql = 'SELECT articleCount,size,category,mediaCount,mod.date,men.name,perma_ref FROM modules as mod,menus as men WHERE mod.perma_ref = %s AND men.zim_name = mod.perma_ref'
         sql = 'SELECT me.name,mo.name,mo.perma_ref,size,articleCount,mediaCount FROM modules as mo,menus as me WHERE  me.zim_name = mo.perma_ref  AND mo.perma_ref = %s'
         try:
            c.execute(sql,(key,))
            rv = c.fetchone()
            if rv:
               outstr += ' {"' + key + '":{\n'
               if rv['mo.name']:
                  outstr += '  "name":"' + rv['mo.name'] + '",\n'
               menuitem = rv.get('name','')
               outstr += '  "menuitem":"' + menuitem + '",\n'
               outstr += '  "fileref":"' + dload[key] + '",\n'
               outstr += '  "size":"' + rv['size'] + '",\n'
               outstr += '  "articleCount":"' + rv['articleCount'] + '",\n'
               outstr += '  "mediaCount":"' + rv['mediaCount'] + '"\n'
               outstr += '  }\n'
               outstr += ' },\n'
         except MySQLdb.Error as e:
            print str(e)
            print sql
      outstr = outstr[:-2] + '\n]'
      with open(g.DL_ZIMS,'w') as outfile:
         outfile.write(outstr)
         outfile.close()
###########################################################
if __name__ == "__main__":
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
   #scrape_kiwix_catalog(conn)
   refresh_zim_idx(conn)
   conn.close()
