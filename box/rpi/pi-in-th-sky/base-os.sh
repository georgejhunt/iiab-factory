#!/bin/bash -x
# copy the raspbian base OS to a raw storage device
SDMAX=128

if [ $# -eq 0 ]; then
   echo  "\nUsage: $0 <device (/dev/sdv)> <image type -- [lite | desktop]>"
   echo "  USE CAUTION: Device will be destroyed!!! --default is lite image"
   echo
   exit 1
fi

# get the current settings
source ../../../factory-settings

URL=$LITE

if [ $# -eq 2 ]; then
   case $2 of
   'desktop' | 'DESKTOP')
      URL=$DESKTOP
      BASE=PIXEL
      ;;
   esac
fi
# cache the OS to be installed -- make cache dir if necessary
mkdir -p $CACHE_DIR

BASENAME=$(basename $URL)
if [ ! -f $CACHE_DIR/$BASENAME ];then
   pushd $CACHE_DIR > /dev/null
   echo -e "Downloading $BASENAME ..."
   wget -P $CACHE_DIR  "$URL" > /dev/null
   echo Done
   echo -e "unzipping $BASENAME ..."
   unzip $BASENAME > /dev/null
   echo Done
   popd > /dev/null
fi
IMGNAME=${BASENAME/%.zip/.img}

# check that the device is no larget than 129GB -- SDMAX above
size=`parted $1 print | grep Disk | cut -d' ' -f3`
size=${size/%GB/}
# remove any decimal component
size=${size%.*}
if [ $size -gt $SDMAX ]; then
  echo "device is larger than $SDMAX -- seems like and error ... exiting"
  exit 1
fi

# check the device, skip following if image is already copied
umount /media/usb*
mount ${1}1 /mnt
if [ ! -f /mnt/config.txt ];then
  echo -e "Copying image to SD card  ..."
  umount /mnt
  # copy the image to the device
  dd if=$CACHE_DIR/$IMGNAME of=$1 bs=4M
  sync
  echo Done
fi

####################################################
#  The work of building up the image will be done here
####################################################

# shrink it, zip it, and copy to internetarchive.org
./freezupl.sh $1 $BASE
