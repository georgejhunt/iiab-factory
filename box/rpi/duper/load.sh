#!/bin/sh
for f in `cat /mnt/sdb2/tce/iiab.lst`; do
   if [ ! -f /mnt/sdb2/tce/optional/$f ];then
      tce-load -wi "$f"
   fi
