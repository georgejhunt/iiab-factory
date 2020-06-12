#!/usr/bin/env  python3
# Read input file, download urls with missing data, write output json

import os,sys
import json
import argparse
# add path for internetarchive utility
sys.path.append('/usr/local/lib/python2.7/dist-packages')
import internetarchive
import re
from datetime import datetime
import urllib3
import certifi

# Think of the sibling files of an image file as imager_metadata

#  GLOBALS
src_url = "https://downloads.raspberrypi.org/os_list_imagingutility.json"
iiab_url = "https://raw.githubusercontent.com/georgejhunt/iiab-factory/iiab/box/rpi/iiab-imager/os_list_imagingutility_iiab.json"
repo_prefix = "/opt/iiab/iiab-factory/box/rpi/iiab-imager"
imager_menu = "subitems"
icon = "https://raw.githubusercontent.com/iiab/iiab-factory/master/box/rpi/rpi-imager/iiab40.png"
url_prefix = "https://archive.org/download"
args = None

http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',\
           ca_certs=certifi.where())
#resp = (http.request("GET",src_url,retries=10))
args = None
menu_names = [ 'name','description','extract_size','extract_sha256','image_download_size','release_date','zip.md5' ]
current_working_directory = os.getcwd()

def parse_args():
    parser = argparse.ArgumentParser(description="Upload img to archive.org, Set rpi-imager json files.")
    parser.add_argument("-c","--check", help='Check version, update metadata.',action='store_true')
    parser.add_argument("-r","--replace", help='Replace img.zip at archive.org.',action='store_true')
    parser.add_argument("-e","--experimental", help='Put image into Experimental menu.',action='store_true')
    parser.add_argument("image_name", help='Specify the image file namel')
    return parser.parse_args()

#with open('os_input','r') as img_fp:
if False:
   try:
      data = json.loads(resp.data)
   except:
      print("img.json parse error")
      sys.exit(1)


   if False:
         # pull the version string out of the url for use in identity
         url = data['regions'][region]['url']
         match = re.search(r'.*\d{4}-\d{2}-\d{2}_(v\d+\.\d+)\..*',url)
         version =  match.group(1)

         # Fetch the md5 to see if local file needs uploading
         target_zip = os.path.join(MR_HARD_DISK,'stage4',os.path.basename(url))
         with open(target_zip + '.md5','r') as md5_fp:
            instr = md5_fp.read()
            md5 = instr.split(' ')[0]
         if len(md5) == 0:
            print('md5 was zero length. ABORTING')
            sys.exit(1)

def get_archive_org_info(identifier):
      return internetarchive.get_item(identifier)

def fetch_image_info():
   md = {}
   for item in menu_names:
      fname = './%s.%s'%(args.image_name,item)
      print(fname)
      try:
         with open(fname,'r') as fp:
            md[item] = fp.read().rstrip()
      except Exception as e:
         print("error reading %s:%s"%(fname,e,))
         sys.exit(1)
   md['url'] = os.path.join(url_prefix,args.image_name,args.image_name + '.zip')
   md['icon'] = icon
   return md

def do_zip():
   my_zipfile = zipfile.ZipFile("./%s"%args.image_name  + ".zip", mode='w', compression=zipfile.ZIP_DEFLATED)
   # Write to zip file
   my_zipfile.write("./%s"%args.image_name)
   my_zipfile.close()

def digest(fname,algorithm):
    hasher = hashlib.net(algorithm)
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
           hasher.update(chunk)
    return hasher.hexdigest()

def ensure(key,value):
   if not os.path.isfile('./%s%s'%(args.image_name,key)):
      with open('./%s%s'%(args.image_name,key),'w') as fp:
         fp.write(value + '\n')
   
def create_imager_metadata():
   print('in create_image_metadata')
   imager_md = {}
   # in case the zip file is missing
   if not os.path.isfile(args.image_name + '.zip'):
      do_zip()
   if not os.path.isfile(args.image_name + '.zip.md5'):
      imager_md['md5'] = digest(args.image_name + '.zip','md5')
      ensure('zip.md5',imager_md['md5'])
   if not os.path.isfile(args.image_name + '.zip.md5.txt'):
      ensure('zip.md5.txt',imager_md['md5'])
   if not os.path.isfile(args.image_name + '.extract_sha256'):
      imager_md['sha256'] = digest(args.image_name,'sha256')
      ensure('extract_sha256',imager_md['sha256'])
   if not os.path.isfile(args.image_name + '.extract_size'):
      imager_md['extract_size'] = os.stat(args.image_name).st_size
      ensure('extract_size',imager_md['extract_size'])
   if not os.path.isfile(args.image_name + '.image_download_size'):
      imager_md['image_download__size'] = os.stat('./%s%s'%(args.image_name + '.zip')).st_size
      ensure('image_download_size',imager_md['image_download_size'])
   return imager_md

def calculate_imager_md():
   imager_md = {}
   imager_md['md5'] = digest(args.image_name + '.zip','md5')
   imager_md['sha256'] = digest(args.image_name,'sha256')
   imager_md['extract_size'] = os.stat(args.image_name).st_size
   imager_md['image_download__size'] = os.stat('./%s%s'%(args.image_name + '.zip')).st_size
   return imager_md


def xfer_imager_md_to_archive_md(imager_md):
   print(repr(imager_md))
   archive_md = {}
   archive_md['title'] = imager_md['name']
   #archive_md['collection'] = "internetinabox"
   archive_md["creator"] = "Internet in a Box" 
   archive_md["subject"] = "rpi" 
   archive_md["licenseurl"] = "http://creativecommons.org/licenses/by-sa/4.0/"
   archive_md["zip_md5"] = imager_md['zip.md5']
   archive_md["mediatype"] = "software"
   archive_md["description"] = imager_md['description']
   archive_md["extract_sha256"] = imager_md['extract_sha256']
   archive_md['extract_size'] =  imager_md['extract_size']
   archive_md['image_download_size'] =  imager_md['image_download_size']
   return archive_md
       
def check(name):
   info =  get_archive_org_info(name)
   if (info.metadata):
      print("\nArchive.org metadata:%s"%str(info.metadata))

def main():
   global args
   global imager_menu
   args = parse_args()
   if args.check:
      check(args.image_name)
      sys.exit(0)

   # fall through to do the upload
   metadata = fetch_image_info()
   #print(str(metadata))

   # Gather together the metadata for archive.org
   md = {}
   md['title'] = metadata['name']
   #md['collection'] = "internetinabox"
   md["creator"] = "Internet in a Box" 
   md["subject"] = "rpi" 
   md["licenseurl"] = "http://creativecommons.org/licenses/by-sa/4.0/"
   md["zip_md5"] = metadata['zip.md5']
   md["mediatype"] = "software"
   md["description"] = metadata['description']
   md["extract_sha256"] = metadata['extract_sha256']
   md['extract_size'] =  metadata['extract_size']
   md['image_download_size'] =  metadata['image_download_size']
   
   # Check is this has already been uploaded
   item = internetarchive.get_item(args.image_name)
   upload = False
   status = 'ok'
   if not item.metadata:
      print('Archive.org does not have file with identifier: %s'%identifier) 
      upload = True
   else:
      print('local file md5:%s  metadata md5:%s'%(metadata['zip.md5'],item.metadata['zip_md5']))
      if item.metadata['zip_md5'] == metadata['zip.md5']:
         # already uploaded
         print('Skipping %s -- checksums match'%args.image_name)
      else:
         print('md5sums for %s do not match'%md['title'])
         upload = True
   if upload:
      # Debugging information
      print('MetaData: %s'%md)
      try:
         r = internetarchive.upload(args.image_name, files=['./%s'%args.image_name], metadata=md)
         print(r[0].status_code) 
         status = r[0].status_code
      except Exception as e:
         status = 'error'
         with open('./archive_org.log','a+') as ao_fp:
            ao_fp.write("Exception from internetarchive:%s"%e) 
   with open('./archive_org.log','a+') as ao_fp:
      now = datetime.now()
      date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
      ao_fp.write('Uploaded %s at %s Status:%s\n'%(args.image_name,date_time,status))

def do_rpi_imager():
   imager_md = fetch_imager_info()

   # update the menu item json
   imager_menu = "subitems"
   if args.experimental:
      imager_menu = 'experimental'
   json_filename_suffix = os.path.join('os_list_imagingutility_iiab_' + imager_menu + '.json')
   json_filename = os.path.join(repo_prefix,json_filename_suffix)
   print('json_filename:%s'%json_filename)
   try:
      with open(json_filename,'r') as fp:
         json_str = fp.read()
         data = json.loads(json_str)
   except FileNotFoundError as e:
      print("File not found: %s"%e)
      sys.exit(1)
   except:
      print("img.json parse error")
      sys.exit(1)
   data['os_list'].insert(0,metadata)
   fname = os.path.join(repo_prefix,'output',json_filename_suffix)
   with open (fname,'w') as fp:
      json.dump(data,fp,indent=2)

if __name__ == "__main__":
   if not os.path.exists(repo_prefix +'/output'):
      os.mkdir(repo_prefix +'/output')
    # Run the main routine
   main()
