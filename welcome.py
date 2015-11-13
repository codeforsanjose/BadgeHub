
import os
os.system("clear")

loop = 0
while loop == 0:
	print("If you have your QR code enter 'y' if you don't have your QR code enter 'n' \n")
	newUser = input("[y]\[n]")

	if newUser  == "n":
	
		#User input process
		os.system("clear")
		f = open("newUser.txt", "a")
		print("Hi!\n")
	
		correctName = "n"

		while correctName == "n":
			userName = input("What's your name? ")
			userEmail = input("What's your email? ")
			print("Is your name and email correct?")
			correctName = input("[y]\[n]")
	
		f.write(userName) 
		f.write("     ")
		f.write(userEmail)
		f.write("\n")
		f.close()
	
		os.system ("clear")
		print("Thank you for checking in " + userName + "!")
		print("Please wait a moment... your QR code is printing!\n")
		print("\n")
	
		#QR code process	
		import os
		os.system("qrencode -o " + userEmail + ".png " + " '" + userName + "     " + userEmail + "' " )
	
		#printing process
		p = open("printCurrentUser.txt", "w")
		p.write("Hello My Name Is:")
		p.write("\n")
		p.write("\n")
		p.write(userName)
		p.close()
		import os
		os.system("lpr -o landscape -o lpi=2 -o cpi=5 -o  PageSize=Custom.50x100mm printCurrentUser.txt")
		os.system("lpr -o landscape -o PageSize=Custom.60x100mm " + userEmail + ".png")	
	
		loop = 0
		
	if newUser == "y":
		
		import sys

		#User input process
		os.system("clear")
		print("Hi!\n")

		correctName = "n"
		
		while correctName == "n":
			userName = input("What's your name? ")
			print("Is your name correct?")
			correctName = input("[y]\[n]")

		os.system ("clear")
		print("Thank you for checking in " + userName + "!")
		print("Please scan your QR code!")
		print("\n")

		#printing process
		p = open("printCurrentUser.txt", "w")
		p.write("Hello My Name Is:")
		p.write("\n")
		p.write("\n")
		p.write(userName)
		p.close()
		import os
		os.system("lpr -o landscape -o lpi=2 -o cpi=5 -o  PageSize=Custom.50x100mm printCurrentUser.txt")

		#QR scan process
		os.system("sudo modprobe bcm2835-v4l2")
		os.system("v4l2-ctl --overlay=1")
		x = os.popen("zbarcam -v --nodisplay --prescale=640x480","r")
		y = open("returningUser.txt", "a")
			
		barcode = x.readline()
		barcodedata = str(barcode)
		
		y.write(barcode)

		if barcodedata:
			print("{0}".format(barcodedata))
			os.system("/home/pi/kill.sh")
			os.system("v4l2-ctl --overlay=0")
			y.close()
		os.system("clear\n")
	
		loop = 0
