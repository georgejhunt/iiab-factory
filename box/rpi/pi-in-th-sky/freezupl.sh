#!/bin/bash -x
# copy the compact the image, zip it, and copy to internetarchive.org
# Param 1: device containing the image
# Param 2: type of image ("LITE" | "PIXEL" )

# get the current settings
source ../../../factory-settings

DEVICE=$1
# What do we want to shrink?
PARTITION=${DEVICE}2
if [ "$2" == "LITE" ];then
   OSVER=LITE_$OSVER
else
   OSVER=PIXEL_$OSVER
fi

if [ ! -b $PARTITION ];then
   echo "Device $PARTITION not found".
   exit 1
fi

mkdir -p /mnt/sdcard
umount $PARTITION
umount /media/usb*

mount $PARTITION /mnt/sdcard
touch /mnt/sdcard/.resize-rootfs

# create id for image
pushd /mnt/sdcard/opt/iiab/iiab
HASH=`git log --pretty=format:'g%h' -n 1`
YMD=$(date +%y%m%d)
FILENAME=$(printf "%s-%s-%s-%s-%s.img" $PRODUCT $VERSION $YMD $OSVER $HASH)
echo $FILENAME > /mnt/sdcard/.iiab-image
echo $FILENAME > ../../last-filename
echo $HASH > ../../last-hash
popd

umount /mnt/sdcard

# now resize

DEVICE=${PARTITION:0:-1}
PART_DIGIT=${PARTITION: (-1)}

PART_START_SECTOR=`parted -sm  $DEVICE unit s print|cut -d: -f1,2|grep $PART_DIGIT:|cut -d: -f2`
root_start=${PART_START_SECTOR:0:-1}

# total prior sectors is 1 less than start of this one
prior_sectors=$(( root_start - 1 ))

# resize root file system
umount $PARTITION
e2fsck -fy $PARTITION
minsize=`resize2fs -P $PARTITION | cut -d" " -f7`
block4k=$(( minsize + 100000 )) # add 400MB OS claims 5% by default
resize2fs $PARTITION $block4k

umount $PARTITION
e2fsck -fy $PARTITION

# fetch the new size of ROOT PARTITION
blocks4k=`e2fsck -n $PARTITION 2>/dev/null|grep blocks|cut -f5 -d" "|cut -d/ -f2`

root_end=$(( (blocks4k * 8) + prior_sectors ))

umount $PARTITION
e2fsck -fy $PARTITION

# resize root partition
parted -s $DEVICE rm $PART_DIGIT
parted -s $DEVICE unit s mkpart primary ext4 $root_start $root_end

umount $PARTITION
e2fsck -fy $PARTITION

# set the percentage reserved by OS to 1 percent
tune2fs -m 1 $PARTITION

# recalc last sector and read that many sectors from card
last_sector=`parted -s $DEVICE unit s print |tail -2 |head -1| awk '{print $3}'`
last=${last_sector:0:-1}
last=$(( last / 8  )) # integer division
last=$(( last + 1  )) # round up
echo "last sector: $last"
dd if=$DEVICE of=/$CACHE_DIR/$FILENAME bs=4K count=$last
echo "last sector: $last"

zip $CACHE_DIR/$FILENAME.zip $CACHE_DIR/$FILENAME
md5sum $CACHE_DIR/$FILENAME.zip > $CACHE_DIR/$FILENAME.zip.md5.txt

./pits/upload2ia.py $CACHE_DIR/$FILENAME.zip
