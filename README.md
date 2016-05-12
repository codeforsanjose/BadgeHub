*note* everytime you see "pi@raspberrypi ~ $" in this tutorial, it means it's a command line function, just copy what you see after "pi@raspberrypi ~ $" into the lxterminal and hit enter

Preliminary information:
	This guide is under the assumption that you have a Raspberry pi 1 or 2 with your Dymo printer connected to it via USB. Also this guide was created with a Raspberry Pi 2 with Raspbian installed - your mileage may vary depending on your Raspberry Pi model and OS.

Directions at a glance

	1) Install QR scanning and generating repositories
		a. pi@raspberrypi ~ $ sudo apt-get install zbar-tools
		b. pi@raspberrypi ~ $ sudo apt-get install qrencode
		
	2) Download the repository from Github and unzip the contents into your Raspberry Pi's root directory
		a. Make the kill.sh an executable by running the chmod command
			i. pi@raspberrypi ~ $ chmod 755 kill.sh
	3) Run sudo apt-get update to initialize before we install the printer repositories
		a. pi@raspberrypi ~ $ sudo apt-get update
	4) Install the printer repositories
		a.  CUPS libraries and other necessary libraries to build: 
			i. pi@raspberrypi ~ $ sudo apt-get install libcups2-dev libcupsimage2-dev g++ cups cups-client 
		b. Download Dymo LabelWriter SDK for Linux:
			i. pi@raspberrypi ~ $ wget http://download.dymo.com/Download%20Drivers/Linux/Download/dymo-cups-drivers-1.4.0.tar.gz 
		c. Unpack, configure and install the drivers.
			i. pi@raspberrypi ~ $ tar xvf dymo-cups-drivers-1.4.0.tar.gz 
			ii. pi@raspberrypi ~ $ cd dymo-cups-drivers-1.4.0.5/ 
			iii. pi@raspberrypi ~/dymo-cups-drivers-1.4.0.5 $ sudo ./configure 
			iv. pi@raspberrypi ~/dymo-cups-drivers-1.4.0.5 $ sudo make 
			v. pi@raspberrypi ~/dymo-cups-drivers-1.4.0.5 $ sudo make install 
	5) Add the printer
		a. Add the pi user to the printer admin group to allowed to login to the printer admin
			i. pi@raspberrypi ~ $ sudo usermod -a -G lpadmin pi 
		b. Navigate to http://localhost:631/
			i. Click on administration at the top and then click on add printer in this new page
				1) If it asks for a password enter pi as the user and raspberry as the password
			ii. Click on the DYMO LabelWriter 450 Turbo and then continue
			iii. For the next page you can customize the information of the printer and then hit continue
			iv. On this page it'll ask for the model of the printer, ensure that the model is the model of your printer then hit add printer
			v. Verify everything through the admin interface - click Manage Printers and the LabelWriter should appear in the list.
			vi. Finally, we must make the labelwriter the default printer 
				1) Click on printers and then click on the name of your printer
				2) On the new page click on administration and then click on set as server default
			vii. You're done!
	6) Enable camera 
		a. pi@raspberrypi ~ $ sudo raspi-config 
			i. Once here, choose #6 and enable the camera. 
	7) Finally, Reboot the device!
	8) After everything is said and done run the command python welcomek.py to test the program.


Side note- emergency camera shutoff function:
	V4l2-ctl --overlay=0

How to run the program:

	1) After booting the system enter "pi" as the user ID and "raspberry" as the password (no quotations)
	2) Enter "python welcome.py" to run the program
	3) to exit the program press the keys "ctrl" and "c" about 3 or 4 times consecutively

To access your CSV file:

	1) after booting the system and logging in, simply enter "startx" in the command line to bring up the GUI
	2) at the top click on the file cabinet icon
	3) at the sidebar to your left click on the "pi" directory - your csv file should be there titled "userInformation.csv"

