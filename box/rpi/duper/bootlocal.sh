#!/bin/sh
# put other system startup commands here
/usr/local/etc/init.d/openssh start
sudo source /root/.bashrc
sudo chmod 700 /root
sudo chgrp root /root
for f in `cat /mnt/sdb3/tce/iiab.lst`; do
   if [ ! -f /mnt/sdb3/tce/optional/$f ];then
      tce-load -wi "$f"
   fi
done

