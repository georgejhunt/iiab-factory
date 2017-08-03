#!/usr/bin/python
# Scan KA Lite content, update video sizes in blank field in database

import sys, shutil, os.path, argparse, sqlite3

src_dir = "/library/ka-lite/content"
kalite_dbase_dir = "/library/ka-lite/database"

parser = argparse.ArgumentParser(description="Slice Bittorrent Kalite Videos. List topics, and sizes for paths listed in paths.list file. Ouput youtube ids with -v")
parser.add_argument("-p","--path_list", metavar="FILENAME", help="the full, or relative, path to the text file containing list of paths. Required to output youtube ID list/")
parser.add_argument("-s", "--src", metavar="SRC_DIR", help="get video availability, and sizes from this directory -- default is /library/ka-lite/content")
parser.add_argument("-l", "--lang", type=str, default='en', required=False, help="language to select (default en)")
parser.add_argument("-v", "--video", help="Instead, output video id list",action="store_true")

parser.add_argument("-w", "--work", metavar="WORK_DIR", help="copy database here, and update it with current video sizes -- default is SRC_DIR")

args = parser.parse_args()
lang = args.lang.lower()
kalite_dbase_dir = "/library/ka-lite/database/"
sqlite_file = kalite_dbase_dir + "/content_khan_" + lang + ".sqlite"

if not os.path.isfile(sqlite_file):
    print "Database " + sqlite_file + " not found."
    sys.exit(1)

if args.src:
   kalite_content_dir = args.src+'/'
else:
   kalite_content_dir = "/library/ka-lite/content/"
os.system("mkdir -p %sunused"%kalite_content_dir)
rename_dir = os.path.join(kalite_content_dir,"unused/")

if args.work:
   work_dir = args.work
else:
   work_dir = kalite_content_dir

if args.path_list:
   list_file = args.path_list
else:
   list_file = ""
if not os.path.isfile(list_file):
   if not os.path.isfile(os.path.join(work_dir,list_file)):
       if args.video:
          print("Please provide a text file with khan paths (starting with 'khan/' to generate video list")
          sys.exit(1)
   else:
      list_file = os.path.join(work_dir,list_file) 
      

video_files = os.listdir(kalite_content_dir)
videos_total_size=0L

my_sqlite_file = work_dir + "/content_khan_" + lang + ".sqlite"
#print("opening ",my_sqlite_file)

def human_fmt(num):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s" % (num, unit,)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def print_subtree(parent):
   global c
   sql = 'select * from tree where path like "%s"'%parent
   c.execute(sql)
   pathnames = c.fetchall()
   for path in pathnames:
      thisp = path[0]+'%'
      sql = 'select path,sum(size_on_disk) from item where path like "%s" group by path like "%s"'%(thisp,thisp,)
      #print(sql)
      c.execute(sql)
      result = c.fetchone()
      print result[0],human_fmt(result[1])

def print_videos(parent):
   global c,videos_total_size
   sql = 'select * from tree where path like "%s"'%parent
   c.execute(sql)
   pathnames = c.fetchall()
   for path in pathnames:
      thisp = path[0]+'%'
      sql = 'select youtube_id,size_on_disk from item where path like "%s" '%(thisp,)
      print(sql)
      c.execute(sql)
      result = c.fetchall()
      for r in result:
         if r[0] != None:
            print r[0]
            videos_total_size += r[1]
   print("Total size:%s"%human_fmt(videos_total_size))

if not os.path.isfile(my_sqlite_file):
#if True:
   # update the stock databse with size of each downloaded/available file
   conn = sqlite3.connect(my_sqlite_file)
   c = conn.cursor()
   shutil.copy(sqlite_file,my_sqlite_file)
   os.system("sync")
   conn = sqlite3.connect(my_sqlite_file)
   c = conn.cursor()

   size = 0
   success=fail=missing=0
   last_hash=""
   for v in sorted(video_files):
      hash = v.split('.')[0]
      try:
         filepath = os.path.join(kalite_content_dir, v)
         size += int(os.stat(filepath).st_size)
      except:
         pass
      if hash != last_hash and size != 0:
         # update the database with the sum of mp4 and png
         c.execute('update item set size_on_disk = ? where youtube_id = ? ', (size,hash,))
         if c.rowcount > 0:
            success += 1
            #print "successful update",size,hash
         else:
            fail += 1
            print "failed to update",hash
            src = kalite_content_dir + hash + '.mp4'
            dst = rename_dir + hash + '.mp4'
            #print src,dst
            try:
               os.rename(src,dst)
               src = kalite_content_dir + hash + '.png'
               dst = rename_dir + hash + '.png'
               os.rename(src,dst)
            except:
               print "rename exception:%s"%hash
               pass
         size = 0
      else:
         last_hash = hash
      if success % 100 ==  0:
         print("success:%s, fail:%sk "%(success,fail,))
   conn.commit()

conn = sqlite3.connect(my_sqlite_file)
c = conn.cursor()

sql = '''create table if not exists tree as with recursive chunk(path,pk) as (select path,parent_id from item where parent_id = 16991 union  select item.path,item.pk from item,chunk where item.parent_id = chunk.pk limit 100) select path from chunk;'''

c = conn.cursor()
c.execute(sql)
conn.commit()

if list_file:
   for line in  open(list_file,'r'):
      # use the first string in the line
      spec = line.split(' ')[0]
      if not args.video:
         print_subtree(spec)
      else:
         print_videos(spec)
else:
   print_subtree("khan/%")
'''
found = 0
not_found = 0
for f in video_files:
    if ".mp4" in f:
        v = f.split(".mp4")[0]
        if v not in video_ids:
            print str(v) + " not found"
            not_found += 1
            src = kalite_content_dir + f
            dst = rename_dir + f
            #print src, dst
            os.rename(src, dst)
            src = kalite_content_dir + v + ".png"
            dst = rename_dir + v + ".png"
            #print src, dst
            os.rename(src, dst)

        else:
            found += 1
print str(found) + " found."
print str(not_found) + " not found."
'''

conn.close()
sys.exit(0)
