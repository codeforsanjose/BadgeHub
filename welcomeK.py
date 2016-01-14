import os
import sys
import time
import csv
import datetime
		
os.system("clear")

def printNameBadge(name): #prints name badge from user's inputted information
	p = open("printNameBadge.txt", "w")
	p.write("Hello My Name Is:")
	p.write("\n")
	p.write("\n")
	p.write(name)
	p.close()
	os.system("lpr -o landscape -o lpi=2 -o cpi=5 -o  PageSize=Custom.48x100mm printNameBadge.txt")

def printQRCode(name, email): #prints QR code from user's inputted information
	os.system("qrencode -o " + email + ".png " + "'"+ name + ";" + email +"'" )
	os.system("lpr -o landscape -o PageSize=Custom.45x100mm " + email + ".png")

def surveyQuestions(name): #survey questions segment, can be expanded to more than one question
	print "Why did you come out here tonight?"
	response = raw_input("")
	g = open("userInformation.csv", "a")
	g.write(name)
	g.write(";")
	g.write(response)
	g.write("\n")
	os.system("clear")

def csvInitialization(): #initializes the CSV file and creates fields and names them
	with open("userInformation.csv","a") as csvfile:
		fieldnames = [ 'Name', 'Email', 'Time Stamp', 'User Response 1', 'User Response 2', 'User Response 3']
		writer = csv.DictWriter (csvfile, fieldnames=fieldnames)
		writer.writeheader()

def userInput():#newuser function
	correctName = "no"
	while correctName == "no":
		userName = raw_input("What's your name? ")
		userEmail = raw_input("What's your email? ")
		print "Is the information you see above entered correctly?"
		correctName = raw_input("[yes]\[no]\n")
	userInformation(userName, userEmail)
	thankYouMessage(userName)
	printNameBadge(userName)
	printQRCode(userName, userEmail)

def userInformation(name, email): #puts information such as name, email and when they logged in into the CSV file
	with open("userInformation.csv", "a") as csvfile:
		fieldnames = ['Name', 'Email', 'Time Stamp', 'User Response 1', 'User Response 2', 'User Response 3']
		writer = csv.DictWriter (csvfile, fieldnames=fieldnames)
		writer.writerow({'Name': name, 'Email': email, 'Time Stamp': datetime.datetime.now()})

def thankYouMessage(name): #takes name parameter and puts it in a thank you message
	os.system("clear")
	print "Thank you for checking in, " + name + "!"
	print "Please wait a moment, your Name Badge and/or QR code are printing!\n"
	print "\n"

def qrScanProcess():#returning user function
#QR scan process - turns on the camera, then calls functions userinformation to store information into CSV file, qrTurnOffProcess to turn off camera and thankYouMessage to say thanks
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

        splitPosition = barcodedata.find(";");
        if splitPosition != -1:
                userEmail = barcodedata[splitPosition + 1:]

	userInformation(userName, userEmail)
	qrTurnOffProcess(barcodedata)
	printNameBadge(userName)
	thankYouMessage(userName)

def qrTurnOffProcess(barcodedata): #turns off camera
        if barcodedata:
                print "{0}".format(barcodedata)
                os.system("/home/pi/kill.sh")
                os.system("v4l2-ctl --overlay=0")
        os.system("clear\n")



csvInitialization()
while True:
	print "Do you have your QR code?" 
	newUser = raw_input("[yes]\[no]\n") #for administrator - enter 0 to exit program

	if newUser  == "no": #New User
		os.system("clear")
        	print "Hi! We are going to ask you for your name and email here - don't worry  we won't send you any messages!"
        	print "You will be asked to verify your information before anything is printed so don't worry about making any mistakes!\n"

		userInput()
		#surveyQuestions(userName)
		
	if newUser == "yes": #Returning user
		os.system("clear")
		print "Hi!\n"
		print "Please scan your QR code!\n"
				
		qrScanProcess()
		#surveyQuestions(userName)

	if newUser == "0":
 		#End program
		print "Thank you, and goodbye!"
		exit()
