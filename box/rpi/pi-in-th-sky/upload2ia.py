#!/usr/bin/env python3
# upload a file to internetarchive.org

from internetarchive import upload
import sys
import os

if len(sys.argv) == 1:
    print('Please specify the file to upload')
    sys.exit(1)
md = { "description": "Raspberry pi image, with Internet-In-A-Box (IIAB) software layered on top, and ./runasible has done a minimal install of services","mediatype":"image"}
filepath = sys.argv[1]
identifier = os.path.basename(sys.argv[1])
#print("upload(%s, files=[%s,%s + 'md5.txt'], metadata=%s, verbose=True)"%(identifier,identifier,identifier,md,))
u = upload(identifier, files=[filepath,filepath + '.md5.txt'], metadata=md, verbose=True)
