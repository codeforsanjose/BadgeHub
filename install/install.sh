#!/bin/sh

#########################################################
#              Install script for the                   #
#                Code For San Jose                      #
#                  Login System                         #
#  https://github.com/codeforsanjose/CFSJ-Login-System  #            
#                                                       #
#               (run this file once)                    #
#########################################################


PROJECT_DIR=`pwd`

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y --force-yes \
	zbar-tools \
	qrencode \
	libcups2-dev \
	libcupsimage2-dev  \
	g++ \
	cups \
	cups-client


# install the printer driver for the Dymo LabelWriter 450
# for information about this, see the documentation on the
# dymo website for the Linux SDK and CUPS Drivers
cd /tmp
wget http://download.dymo.com/Download%20Drivers/Linux/Download/dymo-cups-drivers-1.4.0.tar.gz
tar xvf dymo-cups-drivers-1.4.0.tar.gz
cd dymo-cups-drivers-1.4.0.5
sudo ./configure
sudo make
sudo make install
cd /tmp
sudo rm -rf dymo-cups-drivers-1.4.0*
sudo usermod -a -G lpadmin pi
cd $PROJECT_DIR

# install Flask and other Python dependencies
sudo pip install -r requirements.txt


# copy the startup scripts to allow Chromium and the login
# system to start automatically at boot
PI_CONFIG_DIR="/home/pi/.config/lxsession/LXDE-pi"
if [ ! -f $PI_CONFIG_DIR"/autostart" ]; then
    cp $PI_CONFIG_DIR"/autostart" $PI_CONFIG_DIR"/autostart.orig"
fi

cp ./install/autostart $PI_CONFIG_DIR"/autostart"


echo "Finished installing!"
echo "Please set up your printer now at http://localhost:631"
exit 0