#### Steps to create Access Point and Gateway

1. Download Raspbian desktop or lite versions (lite is better for Pi Zero W)
2. Copy Raspbian Image via win32diskimager, dd, or etcher to SD card.
3. Download wifi.zip from http://d.iiab.io/packages/wifi.zip
4. Use windows filemanager to copy wifi.zip from downloads to SD /boot partition.
5. Unzip the zip file to the root directory of SD (windows will not by default put it in the root of SD).
6. Open the new file wpa_supplicant.conf, and change the ssid and password to the correct values for your upstream AP.
7 reboot.
8. If not already done, install https://download.info.apple.com/Mac_OS_X/061-8098.20100603.gthyu/BonjourPSSetup.exe.
9. Use putty, or ssh (if on a mac or linux) to connect to raspberrypi.local.
10. Once connected to the RPI, execute "sudo /boot/ap-wifi-gw
11. Reboot

#### Three Headless Connection Methods to RPI

1. USB Cable
2. Ethernet Wire
3. Wifi (with or without an Internet Access Point)



