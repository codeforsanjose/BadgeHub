#!/bin/sh
# Run this file once

sudo apt-get update
sudo apt-get install -y \
	zbar-tools \
	qrencode \
	libcups2-dev \
	libcupsimage2-dev  \
	g++ \
	cups \
	cups-client

wget http://download.dymo.com/Download%20Drivers/Linux/Download/dymo-cups-drivers-1.4.0.tar.gz
tar xvf dymo-cups-drivers-1.4.0.tar.gz
cd dymo-cups-drivers-1.4.0.5
sudo ./configure
sudo make
sudo make install

sudo usermod -a -G lpadmin pi

