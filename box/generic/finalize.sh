#!/bin/bash 
# remove all the proprietary and non generic data


# the secure-accounts.sh  script removes developer credentials
source ./secure-accounts.sh

# Try to determin if this is raspbian
PLATFORM=`cat /etc/*release|grep ^ID=|cut -f2 -d=`

# if this is a Raspberry Pi GUI pixel version (think young kids) -nuc history
if [ -f /etc/lightdm/lightdm.conf -a "$PLATFORM" = "raspbian" ]; then
  su pi -c history -cw
  su iiab-admin -c history -cw
  history -cw
fi

# remove any aliases we might have added
rm -f /root/.bash_aliases
rm -f /home/iiab-admin/.bash_aliases

# none of the FINAL images should have openvpn enabled
systemctl disable openvpn@xscenet.service
systemctl disable openvpn

# following removes standard files used by ghunt
rm -rf /root/tools
rm -f /root/.netrc
rm -f /root/id_rsa
rm -f /etc/ssh/ssh_host*

if [ "$PLATFORM" == 'raspbian' ]; then
   cp -f ../rpi/pibashrc /root/.bashrc
   
  # if hostkeys are missing, recreate them and restart sshd
  found=$(grep "ssh-keygen" /etc/rc.local)
  if [ -z "found" ];then
      sed -i '/^exit.*/i "ssh-keygen -A\nsystemctl restart sshd"`' /etc/rc.local
  fi
fi

