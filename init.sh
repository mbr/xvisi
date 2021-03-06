#!/bin/sh

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

cat > /etc/init/update-xvisi.conf << EOF
description "updates xvisi from github"

start on (started mountall and net-device-up IFACE!=lo and font-loaded and custom-network-done)

console output

task

script
  set -e
  LOGFILE=/var/log/xvisi-update.log
  echo "Checking for xvisi updates..."
  echo "Started xvisi update on \`date\`" 1>> \$LOGFILE 2>> \$LOGFILE
  cd $REPO_DIR 2>> \$LOGFILE
  git pull 1>> \$LOGFILE 2>> \$LOGFILE
  UPDATE_SCRIPT=$REPO_DIR/on_update
  if [ -e \$UPDATE_SCRIPT ]; then
    echo "Running update script..." >> \$LOGFILE
    \$UPDATE_SCRIPT 1>> \$LOGFILE 2>> \$LOGFILE
  else
    echo "Update script \$UPDATE_SCRIPT not found, not running" >> \$LOGFILE
  fi;
  echo "Finished update on \`date\`" 1>> \$LOGFILE 2>> \$LOGFILE
end script
EOF

echo "Installation finished. Rebooting in 10 secs, press C-c to cancel."
sleep 10 && reboot
