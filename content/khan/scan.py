#!/usr/bin/python
# Scan KA Lite content, update video sizes in blank field in database

import sys, shutil, os.path, argparse, sqlite3

src_dir = "/library/ka-lite/content"
kalite_dbase_dir = "/library/ka-lite/database"

parser = argparse.ArgumentParser(description="List topics, sizes, and totals for paths listed in ini file. Ouput video ids with -p")
parser.add_argument("-i","--ini_file", help="the full, or relative, path to the ini file containing list of paths. Default path khan/")
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
   kalite_content_dir = args.src
else:
   kalite_content_dir = "/library/ka-lite/content/"

if args.work:
   work_dir = args.work
else:
   work_dir = kalite_content_dir

video_files = os.listdir(kalite_content_dir)

my_sqlite_file = work_dir + "/content_khan_" + lang + ".sqlite"
if not os.path.isfile(my_sqlite_file):
   # update the stock databse with size of each downloaded/available file
   shutil.copy(sqlite_file,my_sqlite_file)
   conn = sqlite3.connect(my_sqlite_file)
   c = conn.cursor()

   size = 0
   last_hash = ''
   for v in sorted(video_files):
      hash = v.split('.')[0]
      if hash != last_hash and size != 0:
          # update the database with the sum of mp4 and png
          c.execute('update item set size_on_disk = ? where youtube_id = "?" and kind = "Video" (size,hash,)')
          size = 0
      size += os.path.getsize(kalite_content_dir + v)
      last_hash = hash 
   conn.close()
sys.exit(0)


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

sys.exit(0)
'''
