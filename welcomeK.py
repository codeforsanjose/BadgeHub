import os
import sys
		
os.system("clear")

def printNameBadge(name):
	p = open("printCurrentUser.txt", "w")
	p.write("Hello My Name Is:")
	p.write("\n")
	p.write("\n")
	p.write(name)
	p.close()
	
	os.system("lpr -o landscape -o lpi=2 -o cpi=5 -o  PageSize=Custom.50x100mm printCurrentUser.txt")

def printQRCode(name, email):
	os.system("qrencode -o " + email + ".png " + " '" + name + ";" + email + "' " )
	os.system("lpr -o landscape -o PageSize=Custom.60x100mm " + email + ".png")
	
while True:
	print "If you have your QR code enter 'y' if you don't have your QR code enter 'n' \n"
	print "When finished with user registration enter '0' \n" 
	newUser = raw_input("[y]\[n]\[0]\n")

	if newUser  == "n":
		#New User
		#User input process
		os.system("clear")
		print "Hi!\n"
	
		correctName = "n"

		while correctName == "n":
			userName = raw_input("What's your name? ")
			userEmail = raw_input("What's your email? ")
			print "Is your name and email correct?"
			correctName = raw_input("[y]\[n]\n")
	
		f = open("newUser.txt", "a")
		f.write(userName + "\n" + userEmail + "\n" + "\n")
		f.close()
	
		os.system ("clear")
		print "Thank you for checking in, " + userName + "!"
		print "Please wait a moment, your Name Badge and QR code are printing!\n"
		print "\n"
	
		printNameBadge(userName)
		printQRCode(userName, userEmail)
		
	if newUser == "y":
		#Returning user
		#User input process
		os.system("clear")
		print "Hi!\n"
		print "Please scan your QR code!"
		print "\n"

		#QR scan process
		os.system("sudo modprobe bcm2835-v4l2")
		os.system("v4l2-ctl --overlay=1")
		x = os.popen("zbarcam -v --nodisplay --prescale=640x480","r")
		
		barcode = x.readline()
		barcodedata = str(barcode)
		
		splitPosition = barcodedata.find(":");
		if splitPosition != -1:
			userName = barcodedata[splitPosition + 1:]
		
		splitPosition = userName.find(";");
		if splitPosition != -1:
			userName = userName[:splitPosition]
		0	
		splitPosition = barcodedata.find(";");
		if splitPosition != -1:
			userEmail = barcodedata[splitPosition + 1:]
		
		y = open("returningUser.txt", "a")
		y.write(userName + " " + userEmail)
		
		printNameBadge(userName)

		if barcodedata:
			print "{0}".format(barcodedata)
			os.system("/home/pi/kill.sh")
			os.system("v4l2-ctl --overlay=0")
			y.close()
		os.system("clear\n")

	if newUser =="0":
		#End program
		exit()
