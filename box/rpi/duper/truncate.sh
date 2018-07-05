#!/bin/bash
# Functions useful to manipulate SD card content
# All sizes in bytes, unless otherwise noted

# number of partitions on IIAB may change
LIBRARY_PARTITION=2
if [ -f /etc/iiab/iiab.env ]; then
   source /etc/iiab/iiab.env
else
   PRODUCT=IIAB 
   VERSION=6.5
fi

min_device_size(){
   # Params:  in: full path of file containing image (2 partitions)
   #  -- echos out: bytes

   # get the next loop device
   DEVICEREF=$(losetup -f)
   $(losetup -P $DEVICEREF $1)
   if [ $? -ne 0 ];then
      echo failed to create RAWDEVICE reference for $1
      losetup -d $DEVICEREF
      exit 1
   fi
   PARTITION=${DEVICEREF}p${LIBRARY_PARTITION}

   root_start=$(fdisk -l $DEVICEREF | grep $PARTITION | awk '{print $2}')

   umount $PARTITION
   e2fsck -fy $PARTITION > /dev/null
   block4k=`resize2fs -M -P $PARTITION | cut -d" " -f7`
   e2fsck -fy $PARTITION > /dev/null
   echo $(expr $block4k \* 4096 + $root_start \* 512)
   # clean up
   losetup -d $DEVICEREF
}

size_image(){
   # truncate last partition
   # param1: full path of the file containing IIAB image
   # param2 (optional): desired size in 4kblocks (smallest possible if not specified)
   # returns 0 on success

   # get the next loop device
   DEVICEREF=$(losetup -f)
   $(losetup -P $DEVICEREF $1)
   if [ $? -ne 0 ];then
      echo failed to create RAWDEVICE reference for $1
      losetup -d $DEVICEREF
      exit 1
   fi
   PARTITION=${DEVICEREF}p${LIBRARY_PARTITION}

   root_start=$(fdisk -l $DEVICEREF | grep $PARTITION | awk '{print $2}')

   # total prior sectors is 1 less than start of this one
   prior_sectors=$(( root_start - 1 ))

   # resize root file system
   umount $PARTITION
   e2fsck -fy $PARTITION > /dev/null
   if test $? -ne 0; then 
      losetup -d $DEVICEREF
      exit 1
   fi
   if [ $# -lt 2 ]; then
     block4k=`resize2fs -P $PARTITION | cut -d" " -f7`
   else
     block4k=$(echo "$2 / 4096 " | bc )
   fi

   # do the real work of this function
   resize2fs $PARTITION $block4k

   umount $PARTITION
   e2fsck -fy $PARTITION > /dev/null

   # fetch the new size of ROOT PARTITION
   blocks4k=`e2fsck -n $PARTITION 2>/dev/null|grep blocks|cut -f5 -d" "|cut -d/ -f2`

   root_end=$( echo "$blocks4k * 8 + $prior_sectors" | bc )

   umount $PARTITION
   e2fsck -fy $PARTITION > /dev/null

   # resize root partition
   parted -s $DEVICEREF rm $LIBRARY_PARTITION
   parted -s $DEVICEREF unit s mkpart primary ext4 $root_start $root_end
   losetup -d $DEVICEREF

   copy_size=`echo "$blocks4k * 4096 + prior_sectors * 512" | bc`
   copy4k=$(echo "($copy_size / 4096) + 1" | bc)
   set +x
   dd if=$1 of=$1.$$ bs=4096 count=$copy4k status=progress | \
   while read -r line; do
      copied=$(echo $line | awk '{print $1}')
      if [ -z "$copied" ]; then 
         copied=0; 
         line=""
      fi
      percent=$(expr $copied \* 100 / $CHOSEN_SIZE) &> /dev/null
      echo "copied: $copied  percent: $percent"
      echo XXX
      echo $percent
      echo $line
      echo XXX 
   done | dialog --title "Writing a Smaller resized image" --gauge "Copying the image.. This may take some time ... " 10 78 0
   set -x
   if test $? -ne 0; then exit 1; fi
   rm $1
   mv $1.$$ $1
}

ptable_size(){
   # parameter is filename of image
   DEVICEREF=$(losetup -f)
   $(losetup -P $DEVICEREF $1)
   if [ $? -ne 0 ];then
      error_msg="failed to create RAWDEVICE reference for $1"
      losetup -d $DEVICEREF
      exit 1
   fi
   sectors=$(fdisk  -l $DEVICEREF | grep ${DEVICEFEF}p2 | awk '{print $3}')
   losetup -d $DEVICEREF
   echo "$sectors * 512" | bc
}

iiab_label(){
   if [ $# -ne 3 ];then
      echo "requires parameters iiab partition mount, username, labelstring"
      exit 1
   fi
   PARTITION=$1
   USER=$2
   LABEL=$3
   local iiab=false
   if [ -d $PARTITION/opt/iiab/iiab ]; then
      iiab=true
   fi

   # create id for image
   if test "$iiab" = "true"; then
      pushd /$PARTITION/opt/iiab/iiab > /dev/null
      HASH=`git log --pretty=format:'g%h' -n 1`
      popd > /dev/null
   else
      HASH="$$"
      PRODUCT=LOCAL
      VERSION="0.1"
   fi
   YMD=$(date "+%y%m%d-%H%M")
   FILENAME=$(printf "%s-%s-%s-%s-%s-%s.img" $PRODUCT $VERSION $USER $LABEL $YMD $HASH)
   persistVariable "LAST_FILENAME" $FILENAME
   echo $FILENAME
}

auto_expand(){
   # receives partition as $1, assumes IIAB is loaded on that partition
   PARTITION=$1
   mkdir -p /tmp/duper/sdcard
   mount $PARTITION /tmp/duper/sdcard

   touch /tmp/duper/sdcard/.resize-rootfs
   umount /tmp/duper/sdcard
}

modifyImage(){
   echo $FILENAME > /tmp/duper/identifier_filename
   echo $FILENAME > /tmp/duper/sdcard/.iiab-image
   git branch >> /tmp/duper/sdcard/.iiab-image
   git log -n 5 >> /tmp/duper/sdcard/.iiab-image
   cat /tmp/duper/sdcard/duper/etc/rpi-issue >> /tmp/duper/sdcard/.iiab-image

   echo $FILENAME > ../../last-filename
   echo $HASH > ../../last-hash

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

persistVariable(){
   # Save name value pair $1 $2
   # see if it already exists
   grep $1 $PERSIST_STATE_FILE > /dev/null
   if [ $? -eq 0 ]; then
      sed -i -e "s|^$1=.*|$1=$2|" $PERSIST_STATE_FILE
   else
      (echo "$1=$2") >> $PERSIST_STATE_FILE
   fi
}

getPersistedVariable(){
   grep ^$1 $PERSIST_STATE_FILE > /dev/null
   if [ $? -eq 0 ]; then
      echo $(grep ^$1 $PERSIST_STATE_FILE | cut -d= -f2)
   else
      echo
   fi
}
