#!/bin/sh

#########################################################
#              Install script for the                   #
#                Code For San Jose                      #
#                  Login System                         #
#  https://github.com/codeforsanjose/CFSJ-Login-System  #            
#                                                       #
#               (run this file once)                    #
#########################################################

sudo apt-get update

sudo apt-get install -y \
    git \
    python3-dev \
    python3-venv \
    zbar-tools \
    qrencode \
    libtool \
    libpcsclite-dev \
    libusb-dev \
    lpr \
    cups \
    libcups2-dev \
    libcupsimage2-dev \
    python-cups \
    gcc \
    g++ \
    autoconf \
    automake \
    rabbitmq-server \
    supervisor

# install Docker
# https://www.raspberrypi.org/blog/docker-comes-to-raspberry-pi/
curl -sSL https://get.docker.com | sh
sudo usermod -aG docker pi

docker pull redis

#
# Raspberry Pi config
# enables serial, I2C, SPI, expands the file system, and sets the locale.
# (for these, 0 = enabled)
# for a complete list, see:
# https://raspberrypi.stackexchange.com/a/66939/99501
# https://github.com/RPi-Distro/raspi-config/blob/master/raspi-config
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_serial 0
sudo raspi-config nonint do_change_locale en_US.UTF-8
sudo raspi-config nonint do_configure_keyboard us
sudo raspi-config nonint do_expand_rootfs



# libnfc install
sudo apt-get install -y libnfc-dev

# this should now list an NFC device
sudo nfc-list



# Python 3 install
#wget https://bootstrap.pypa.io/get-pip.py
#sudo python3 get-pip.py
#rm ./get-pip.py
# sudo ln -s /usr/bin/python /usr/bin/python3
# sudo ln -s /usr/bin/pip3 /usr/bin/pip

# clear the bash cache, because reasons
#hash -r


# Setup RabitMQ
# sudo rabbitmqctl add_user badgehub password
# sudo rabbitmqctl add_vhost badgehubvhost
# sudo rabbitmqctl set_permissions -p badgehubvhost badgehub ".*" ".*" ".*"


# celery worker -A nametag_server.celery --loglevel=info


#
# Install the printer driver for the Dymo LabelWriter.
# The official DYMO driver has an issue and won't build.
# For more information, see the project page:
# https://github.com/Kyle-Falconer/DYMO-SDK-for-Linux
cd /tmp
git clone https://github.com/Kyle-Falconer/DYMO-SDK-for-Linux.git
cd DYMO-SDK-for-Linux
aclocal
automake --add-missing
autoconf
./configure
make
sudo make install
sudo usermod -a -G lpadmin pi


PROJECT_DIR=/usr/local/cfsj-login-system

sudo mkdir $PROJECT_DIR
sudo chown -R pi $PROJECT_DIR
cd $PROJECT_DIR

#sudo pip3 --default-timeout=1000 install --upgrade virtualenv

git clone https://github.com/codeforsanjose/CFSJ-Login-System.git src
cd src
python3 -m venv venv
. venv/bin/activate
pip3 --default-timeout=1000 install -r requirements.txt

# normally we'd just use `pip install fclist`, but the official package is broken
pip3 install wheel
pip3 install git+git://github.com/Kyle-Falconer/python-fclist.git@9ce346d184f38b3b4780d6df50847897c32ed281


# test
# wget https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_PN532/master/examples/pn532_simpletest.py
# wget https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_PN532/master/examples/readwrite_ntag2xx.py
# python3 pn532_simpletest.py



# supervisord configuration
#usermod -a -G supervisor
#usermod -a pi -G supervisor
#sudo cp install/supervisord.conf /etc/supervisord.conf
#service supervisor restart


IP_ADDR=`ip route get 8.8.8.8 | awk -F"src " 'NR==1{split($2,a," ");print a[1]}'`
LOGIN_GUI_PORT=${LOGIN_GUI_PORT:=80}

echo "Finished installing!"
echo ""
echo "NOTE:"
echo "Please use the CUPS admin page to "
echo "set up your printer at http://${IP_ADDR}:631 "
echo "If you are unable to access the CUPS admin page, "
echo "try opening an ssh tunnel to this computer: "
echo "    ssh pi@${IP_ADDR} -T -L 3631:localhost:631 "
echo "then open http://localhost:3631"
echo ""
echo "You may access the login system at http://${IP_ADDR}:${LOGIN_GUI_PORT}"
echo "Configuration can be done at http://${IP_ADDR}:${LOGIN_GUI_PORT}/admin"

if [ -z "$XDG_CURRENT_DESKTOP" ]; then
    # if a desktop environment is installed, then configure Chromium to autostart
    # copy the startup scripts to allow Chromium and the login
    # system to start automatically at boot
    sudo raspi-config nonint do_boot_behaviour B4 # Desktop GUI, automatically logged in
    PI_CONFIG_DIR="/home/pi/.config/lxsession/LXDE-pi"
    if [ ! -f $PI_CONFIG_DIR"/autostart" ]; then
        cp $PI_CONFIG_DIR"/autostart" $PI_CONFIG_DIR"/autostart.orig"
    fi

    cp ./install/autostart $PI_CONFIG_DIR"/autostart"
    echo "After you have configured the printer, please reboot the Raspberry Pi to start it in kiosk mode."
    exit 0
else
    echo "We are running in headless mode."
    sudo raspi-config nonint do_boot_behaviour B1 # Text console, requiring user to login"
    # not yet implemented
fi 
