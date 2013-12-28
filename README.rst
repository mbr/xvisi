I found the XBMC auto-updating capabilities severely lacking, as a result, only raspbmc is supported (openelec has no way of installing the required lxml package).

To use on any linux system, ensure python's lxml and requests are installed.

Installation on a fresh raspbmc
===============================
1. install and start raspbmc
2. select "Exit" from the shutdown menu
3. when prompted, press ESC for a terminal
4. login as "pi", password "raspberry"
5. type in the following command
   wget -O- http://mbr.github.io/xvisi | sh
6. wait for a reboot and enjoy


Unsupported and not-up-to date: https://raw.github.com/mbr/xvisi/gh-pages/repository.xvisi.zip
