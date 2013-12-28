#!/bin/sh

# this script is run by the bootstrap.sh found on gh-pages. it runs as root
# using sudo

# to install on a fresh raspbmc:
#
# 1. install and start raspbmc
# 2. select "Exit" from the shutdown menu
# 3. when prompted, press ESC for a terminal
# 4. login as "pw", password "raspberry"
# 5. type in the following command
#
#    wget -O- http://mbr.github.io/xvisi/bootstrap.sh  | sh
#
# 6. enjoy

set -e

echo "installing xvisi..."

REPO_URL=https://github.com/mbr/xvisi
REPO_DIR=/opt/local/xvisi
PLUGIN_NAME=plugin.video.xvisi
ADDONS_DIR=/home/pi/.xbmc/addons
ADDON_PATH=$ADDONS_DIR/$PLUGIN_NAME
XBMC_USER=pi
XVISI_DEPS="python-requests python-lxml"

# update apt repositories
apt-get update -y

# install git and dependencies
apt-get install -y git $XVISI_DEPS

# erase old
rm -rf $REPO_DIR $ADDON_PATH

# create new
mkdir -p $REPO_DIR
git clone $REPO_URL $REPO_DIR
sudo -u pi -- ln -s $REPO_DIR/$PLUGIN_NAME $ADDON_PATH
