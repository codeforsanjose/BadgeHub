# BadgeHub

BadgeHub, formerly called "Code For San Jose Login System", prints out name tags which contain the guest's name and
email address as a QR code, name in plain text, and the organization logo. The guest information is recorded in 
a `.csv` file and automatically uploaded to Google sheets when the Sheets API is turned on.

An administration settings page is available to toggle the various features and adjust the positioning of the elements
for how they should be printed.

Compare to the services [Envoy](https://envoy.com) provides.

![creating a name tag][1]

Pre-requisites
--------------
* A Raspberry Pi (confirmed working on versions 2, 3B, 3B+, and Zero W).  
* DYMO LabelWriter 450 printer connected to the Raspberry Pi via USB.
* Internet access for the Raspberry Pi.

The Bill of Materials provides the complete list of equipments, pricing, and links to recommended products.

<details><summary>**Bill of Materials (click to open)**</summary><p>

| Item No. | Description                                            | Quantity | Price  | Link                |
|----------|--------------------------------------------------------|----------|--------|---------------------|
| 1        | Raspberry Pi 3 B+  (recommended)                       | 1        | $38.10 | [Amazon link][2]    |
| 2        | Raspberry Pi 3.3190G 7" Touchscreen Display (optional) | 1        | $74.00 | [Amazon link][3]    |
| 3        | SmartiPi Touch case (optional)                         | 1        | $27.99 | [Amazon link][4]    |
| 3        | Power Adapter                                          | 1        |  $9.99 | [Amazon link][5]    |
| 4        | Keyboard                                               | 1        | $14.99 | [Amazon link][6]    |
| 5        | Micro SD Card                                          | 1        |  $7.99 | [Amazon link][7]    |
| 6        | DYMO LabelWriter 450 Turbo                             | 1        | $79.99 | [Amazon link][8]    |
| 7        | DYMO 2-1/4" x 4" labels (30857)                        | 1        | $10.00 | [Amazon link][9]    |
| 8        | PN532 NFC/RFID controller breakout board (optional)    | 1        | $39.95 | [Adafruit link][10] |
| 9        | PN532 NFC/RFID (optional, alternate version)           | 1        |  $7.20 | [Alibaba link][11]  |


**Total Cost:** $223.18

</p></details>

Setting up your Raspberry Pi as a name tag kiosk
-------------------------------------------------
Setting up your Raspberry Pi as a name tag kiosk involves these steps:

1. [Flashing the SD card for Raspbian](#flash_raspbian) (a fresh install is optional, but recommended)
2. [Installing the login system](#installing_login)
3. [Adding the DYMO LabelWriter 450 printer](#adding_printer)
4. [Connecting the NFC reader](#connecting_nfc) (optional)
5. [Setup Google sheets Uploading](#uploading_data) (optional) 

### <a name="flash_raspbian">Flashing The SD Card</a>

This step is used for headless installs, if no display is available. This will allow you to SSH into the Raspberry Pi and configure WiFi.

1. Download [Etcher]
2. Download "Raspbian Stretch with desktop" or "Raspbian Stretch Lite" from the [Raspbian Downloads page]. 
   If you choose the desktop option, then kiosk mode will be used during setup, automatically starting Chromium to the login page.
3. Use Etcher to flash the SD card
4. Create a `wpa_supplicant.conf` file with your WiFi credentials (an example of this is in the `install` folder.
5. Create an empty file named `ssh` (no file extension).
6. Remount the SD card (unplug it, then plug it back in to your computer). It should show up as a drive labeled "boot"
7. Copy the `wpa_supplicant.conf` and `ssh` files over to the "boot" drive.
8. Eject the SD card and insert it into the Raspberry Pi, power it up, and wait a few seconds.
9. SSH into it using `ssh pi@raspberrypi` with default password `raspberry`.
10. Update the software: `sudo apt-get update && sudo apt-get upgrade -y`
11. Reboot (`sudo reboot`), then SSH in again and continue to the next step.


### <a name="installing_login">Installing the login system</a>

Everything you need to install the software is included in [the install script]. This script can be directly executed 
by running the following command from a shell prompt on the Raspberry Pi:

```
wget -O - https://raw.githubusercontent.com/codeforsanjose/BadgeHub/master/install/install.sh | bash
```

The installation process may take several minutes to complete. The script installs all the dependencies required for 
the program including the driver for the DYMO LabelWriter 450 printer.

There are two installation modes:
* **kiosk** - if a desktop environment is installed (such as if you loaded "Raspbian Stretch with desktop"), then 
  kiosk mode will be used and the script will configure the Raspberry Pi to start Chromium automatically on startup.
* **headless** - If no desktop environment is installed, then the script will set it up to start in headless mode, 
  where the web interface is accessible over the local network.


### <a name="adding_printer">Adding the DYMO LabelWriter 450 printer</a>

*Note: when preparing to use the DYMO LabelWriter with Linux, it's important to note that [the official DYMO Linux drivers]
 no longer compile against the lastest software that are included with Raspbian. 
 A [community-maintained fork of the official DYMO Linux SDK] fixes this issue and this is what will be used 
 automatically during the setup process.*

1. Open Chromium and browse to [http://localhost:631/](http://localhost:631/). If no display is connected to 
   the Raspberry Pi, then an SSH tunnel will need to be setup first: `ssh pi@raspberrypi -T -L 3631:localhost:631`, 
   then go to [http://localhost:3631/](http://localhost:3631/) from the host computer.
2. Click the **Administration** tab at the top and click **Add Printer** under Printers.
3. In the **Authentication Required** dialog box, enter `pi` as the user name and `raspberry` as the password.
4. Click **Log In**.
5. In the Add Printer page, select **DYMO LabelWriter 450 (DYMO LabelWriter 450)** and click **Continue**.
6. Review the Name and Description and click **Continue**.
7. Select **DYMO LabelWriter 450 (en)** from the Model list.
8. Click **Add Printer**.
9. In the Set Default Options for DYMO_LabelWriter_450 page, set the following:
	* Media size: **30857 Badge Label** or **30323 Shipping Label** 
	* Output Resolution: **300x600 DPI**
	* Halftoning: **Error Diffusion**
	* Print Density: **Normal**
	* Print Quality: **Barcodes and Graphics**
10. Click **Set Default Options**. You will be redirected to the Printers tab.
11. Click the **Administration** drop-down and select **Set As Server Default**.
12. Finally, reboot the device.

After rebooting, the Raspberry Pi will automatically start Chromium in kiosk mode and display the login system.


### <a name="connecting_nfc">Connecting the pn532 NFC Reader</a>

Wire it up using the "SPI" interface, since I2C and UART are reportedly unstable on the Raspberry Pi.

https://learn.adafruit.com/adafruit-pn532-rfid-nfc/python-circuitpython

Consult the Pi diagram:
https://pinout.xyz/pinout/spi

| pn532 Pin | Raspberry Pi Pin                         | Other Names |
|-----------|------------------------------------------|-------------|
| 5V        | 5V (Pins 2 or 4)                         | VDD5V       |
| GND       | GND (pins 6, 9, 14, 20, 25, 30, 34, 39)  |             |
| SCK       | 23/BCM11                                 | SCLK        |
| MOSI      | 19/BCM10                                 | MO          |
| MISO      | 21/BCM9                                  | MI          |
| NSS       | 29/BCM5                                  | SSEL        |


### <a name="uploading_data">Uploading to Google sheets</a>

1. Open Chromium and browse to [https://developers.google.com/sheets/api/quickstart/python].
2. Follow the instructions under "Step 1: Turn on the Google Sheets API" to create and download client_secret.json.
3. Copy the file into the CFSJ-Login-System folder.

The uploder.py copies the user name and email address of the guest from the `.csv` file into Google sheets.
After a successful update, the `.csv` file is deleted. If the update fails, the user information is retained in 
the `.csv` file until a successful retry.


### Local development

You need a local running version of Redis. The best way to do this for development is to use Docker.
https://hub.docker.com/_/redis/

Note that the `-p 6379:6379` argument is required on macOS to route traffic to the default Redis port 6379.
Please see the [docker for mac networking documentation] for more information on how this works.

```bash
# create a running container named 'redis'
docker pull redis
docker run --name redis -p 6379:6379 -v redis-data:/data -d redis redis-server --appendonly yes

# to clear the redis cache inside a running container named 'redis':
docker exec -it redis redis-cli FLUSHALL
```

Note that this application relies on notifications from Redis. For more information about this, 
check out the [redis notifications documentation](https://redis.io/topics/notifications) or
check out this ["Redis Keyspace Notifications in Python" blog post](https://tech.webinterpret.com/redis-notifications-python/)

```bash
# if Redis is installed locally
redis-cli config set notify-keyspace-events KEA

# if running Redis in a container named 'redis'
docker exec -it redis redis-cli config set notify-keyspace-events KEA

```



```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt

# to run just the front end
python run.py -w

# to run just the NFC portion:
python -m BadgeHub.nfc_manager

# or to run the whole program:
python main.py
```

TODO: look into using [cffi](https://cffi.readthedocs.io/en/latest/) for communicating status with CUPS.

[1]: app/static/images/nametag_web.gif
[2]: https://www.amazon.com/ELEMENT-Element14-Raspberry-Pi-Motherboard/dp/B07BDR5PDW
[3]: https://www.amazon.com/Raspberry-Pi-7-Touchscreen-Display/dp/B0153R2A9I/
[4]: https://www.amazon.com/SmartiPi-Official-Raspberry-Touchscreen-Display/dp/B01HV97F64/
[5]: https://www.amazon.com/CanaKit-Raspberry-Supply-Adapter-Charger/dp/B00MARDJZ4/
[6]: https://www.amazon.com/Anker-Bluetooth-Ultra-Slim-Keyboard-Devices/dp/B005ONMDYE/
[7]: https://www.amazon.com/Samsung-MicroSD-Adapter-MB-ME32GA-AM/dp/B06XWN9Q99/
[8]: https://www.amazon.com/DYMO-LabelWriter-Thermal-Printer-1752265/dp/B0027JIIKQ
[9]: https://www.amazon.com/DYMO-Adhesive-LabelWriter-Printers-30857/dp/B00009WO6F
[10]: https://www.adafruit.com/product/364
[11]: https://www.alibaba.com/product-detail/PN532-NFC-Precise-RFID-IC-Card_60371602748.html
[Etcher]: https://www.balena.io/etcher/
[the install script]: https://github.com/codeforsanjose/BadgeHub/blob/master/install/install.sh
[https://developers.google.com/sheets/api/quickstart/python]: https://developers.google.com/sheets/api/quickstart/python
[the official DYMO Linux drivers]: http://www.dymo.com/en-US/dymo-label-sdk-and-cups-drivers-for-linux-dymo-label-sdk-cups-linux-p--1
[community-maintained fork of the official DYMO Linux SDK]: https://github.com/Kyle-Falconer/DYMO-SDK-for-Linux
[Raspbian Downloads page]: https://www.raspberrypi.org/downloads/raspbian/
[docker for mac networking documentation]: https://docs.docker.com/docker-for-mac/networking/