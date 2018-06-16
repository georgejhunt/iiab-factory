#!/bin/bash
# Functions useful to manipulate SD card content
# All sizes in bytes, unless otherwise noted

if [ -f /etc/iiab/iiab.env ]; then
   source /etc/iiab/iiab.env
else
   PRODUCT=IIAB 
   VERSION=6.5
fi

min_device_size(){
   # Params:  in: last partition -- echos out: bytes

   PARTITION=$1
   PART_DIGIT=${PARTITION: (-1)}

   # get the device associated with this partition
   if [ ${PARTITION:0:11} = "/dev/mmcblk" ]; then
      DEVICE=${PARTITION:0:12}
   else
      DEVICE=${PARTITION:0:-1}
   fi

   PART_START_SECTOR=`parted -sm  $DEVICE unit s print|awk -F':' -v part=$PART_DIGIT  '{if($1 == part)print $2;}'`
   root_start=${PART_START_SECTOR:0:-1}

   umount $PARTITION
   e2fsck -fy $PARTITION > /dev/null
   block4k=`resize2fs -M -P $PARTITION | cut -d" " -f7`
   echo $(expr $block4k \* 4096 + $root_start \* 512)
}

truncate(){
   # truncate partition
   # param1: partition (example /dev/sdb2)
   # param2: desired size in 4kblocks (smallest possible if not specified)
   # returns 0 on success

   PARTITION=$1
   if [ ${PARTITION:0:11} = "/dev/mmcblk" ]; then
      DEVICE=${PARTITION:0:12}
   else
      DEVICE=${PARTITION:0:-1}
   fi
   PART_DIGIT=${PARTITION: (-1)}

   PART_START_SECTOR=`parted -sm  $DEVICE unit s print|awk -v part="$PART_DIGIT" -F ":" '{if($1 == part)print $2;}'`
   root_start=${PART_START_SECTOR:0: -1}

   # total prior sectors is 1 less than start of this one
   prior_sectors=$(( root_start - 1 ))

   # resize root file system
   umount $PARTITION
   e2fsck -fy $PARTITION > /dev/null
   if test $? -ne 0; then exit 1; fi
   if [ $# -lt 2 ]; then
     block4k=`resize2fs -P $PARTITION | cut -d" " -f7`
   else
     block4k=$2
   fi
   resize2fs $PARTITION $block4k

   umount $PARTITION
   e2fsck -fy $PARTITION > /dev/null

   # fetch the new size of ROOT PARTITION
   blocks4k=`e2fsck -n $PARTITION 2>/dev/null|grep blocks|cut -f5 -d" "|cut -d/ -f2`

   root_end=$(( (blocks4k * 8) + prior_sectors ))

   umount $PARTITION
   e2fsck -fy $PARTITION > /dev/null

   # resize root partition
   parted -s $DEVICE rm $PART_DIGIT
   parted -s $DEVICE unit s mkpart primary ext4 $root_start $root_end

   umount $PARTITION
   exit 0
}
iiab_label(){
   if [ $# -ne 3 ];then
      echo "requires parameters partition, username, labelstring"
      exit 1
   fi
   PARTITION=$1
   USER=$2
   LABEL=$3
   mkdir -p /tmp/sdcard
   mount $PARTITION /tmp/sdcard > /dev/null

   if [ ! -d /tmp/sdcard/opt/iiab/iiab ]; then
     echo "Device is not IIAB root partition. Exiting."
     exit 1
   fi

   # create id for image
   pushd /tmp/sdcard/opt/iiab/iiab
   HASH=`git log --pretty=format:'g%h' -n 1`
   YMD=$(date +%y%m%d)
   FILENAME=$(printf "%s-%s-%s-%s-%s-%s.img" $PRODUCT $VERSION $USER $LABEL $YMD $HASH)
   echo $FILENAME > /tmp/identifier_filename
   echo $FILENAME > /tmp/sdcard/.iiab-image
   git branch >> /tmp/sdcard/.iiab-image
   git log -n 5 >> /tmp/sdcard/.iiab-image
   cat /tmp/sdcard/etc/rpi-issue >> /tmp/sdcard/.iiab-image

   echo $FILENAME > ../../last-filename
   echo $HASH > ../../last-hash
   popd
   umount /tmp/sdcard
   rmdir /tmp/sdcard
}

auto_expand(){
   # receives partition as $1, assumes IIAB is loaded on that partition
   PARTITION=$1
   mkdir -p /tmp/sdcard
   mount $PARTITION /tmp/sdcard

   touch /tmp/sdcard/.resize-rootfs
   umount /tmp/sdcard
}

bytesToHuman() {
    b=${1:-0}; d=''; s=0; S=(Bytes {K,M,G,T,E,P,Y,Z}B)
    while ((b > 1024)); do
        d="$(printf ".%02d" $((b % 1024 * 100 / 1024)))"
        b=$((b / 1024))
        let s++
    done
    echo "$b$d ${S[$s]}"
}
