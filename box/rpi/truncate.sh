#!/bin/bash
source /etc/iiab/iiab.env

truncate(){
   # truncate partition
   # param1: partition (example /dev/sdb2)
   # param2: desired size in sectors (smallest possible if not specified)
   # returns 0 on success
   PARTITION=$1

   DEVICE=${PARTITION:0:-1}
   PART_DIGIT=${PARTITION: (-1)}

   PART_START_SECTOR=`parted -sm  $DEVICE unit s print|cut -d: -f1,2|grep $PART_DIGIT:|cut -d: -f2`
   root_start=${PART_START_SECTOR:0:-1}

   # total prior sectors is 1 less than start of this one
   prior_sectors=$(( root_start - 1 ))

   # resize root file system
   umount $PARTITION
   e2fsck -fy $PARTITION
   if [ $# -lt 2 ]; then
     minsize=`resize2fs -P $PARTITION | cut -d" " -f7`
   else
     minsize=$(expr $2 / 8)
   fi
   block4k=$(( minsize + 100000 )) # add 400MB OS claims 5% by default
   resize2fs $PARTITION $block4k
   if ! $? then; exit 1; fi

   umount $PARTITION
   e2fsck -fy $PARTITION

   # fetch the new size of ROOT PARTITION
   blocks4k=`e2fsck -n $PARTITION 2>/dev/null|grep blocks|cut -f5 -d" "|cut -d/ -f2`

   root_end=$(( (blocks4k * 8) + prior_sectors ))

   umount $PARTITION
   e2fsck -fy $PARTITION

   umount $PARTITION

   # resize root partition
   parted -s $DEVICE rm $PART_DIGIT
   parted -s $DEVICE unit s mkpart primary ext4 $root_start $root_end
   if ! $? then; exit 1; fi

   umount $PARTITION
   exit 0
}
iiab_label(){
   if [ $# -ne 3 ];then
      echo "requires parameters partition, username, labelstring"
   PARTITION=$1
   USER=$2
   LABEL=$3
   mkdir -p /tmp/sdcard
   mount $PARTITION /tmp/sdcard

   if [ ! -d /tmp/sdcard/opt/iiab/iiab ]; then
     echo "Device is not IIAB root partition. Exiting."
     exit 1
   fi

   # create id for image
   pushd /tmp/sdcard/opt/iiab/iiab
   HASH=`git log --pretty=format:'g%h' -n 1`
   YMD=$(date +%y%m%d)
   FILENAME=$(printf "%s-%s-%s-%s-%s.img" $PRODUCT $VERSION $YMD $1 $HASH)
   echo $FILENAME > /tmp/sdcard/.iiab-image
   git branch >> /tmp/sdcard/.iiab-image
   git log -n 5 >> /tmp/sdcard/.iiab-image
   cat /tmp/sdcard/etc/rpi-issue >> /tmp/sdcard/.iiab-image

   echo $FILENAME > ../../last-filename
   echo $HASH > ../../last-hash
   popd
}
auto_expand(){
   # receives partition as $1, assumes IIAB is loaded on that partition
   PARTITION=$1
   mkdir -p /tmp/sdcard
   mount $PARTITION /tmp/sdcard

   touch /tmp/sdcard/.resize-rootfs
   umount /tmp/sdcard
}
