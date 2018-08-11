## How to Get Started -- Create Imager on USB 
* Download the most recent IMAGER from http://download.iiab.io/packages/imager/. Depending on the speed of your internet, this could take a while.
* On Windows:
    * After the download completes, on Windows, use the filemanager to find the downloaded file, right click on the < filename >.img.zip file, and select "extract all files".
    * On Windows, use https://etcher.io/ or https://sourceforge.net/projects/win32diskimager/ to write the downloaded image file to a USB stick (all data will be lost)
* On a MAC:
    * IMAGER has not yet been verified to function correctly on a MAC.

### Boot IMAGER on your Windows machine
* On Windows:
    * Make sure that your BIOS is set to boot first from USB -- setting the BIOS may require that you strike the f1, f2, f10, f12, or del key just after turning on the power.
    * Look for a BIOS setting called "boot options" or "boot order".
    * Put the USB stick into the machine, and turn on the power.
* On a MAC:
    * Hold down the "option" key, during the power-on sequence.
* After a short time you should see the colorful boot process of Tiny Core Linux, and eventually the IMAGER menu as shown at https://github.com/georgejhunt/iiab-factory/tree/fixes/box/rpi/imager/docs/USAGE.md.
