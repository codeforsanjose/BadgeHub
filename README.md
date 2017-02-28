The **Code For San Jose Log-In** system prints out nametags which contain the guests' name and email address as a QR code, name in plain text, and the Code For San Jose Brigade logo.

![creating a nametag](static/images/nametag_web.gif)

Pre-requisites
--------------
* Raspberry Pi 2 or 3 running Raspbian in desktop mode.  
* DYMO LabelWriter 450 printer connected to the Raspberry Pi via USB.
For a complete list of equipments, pricing, and links to recommended products, see the [Bill of Materials](Bill of Materials.xlsx).

Setting up your Raspberry Pi as a nametag kiosk
-------------------------------------------------
1. Open terminal and create a new folder called "GitHub". Run: `mkdir ~/GitHub`
    **NOTE:** Ensure that the folder name is "GitHub" since the folder name is referenced in the install script. 
2. Clone the git repository from GitHub. Run:
    ```
    cd ~/GitHub
    git clone https://github.com/codeforsanjose/CFSJ-Login-System.git
    ```
 
3. Run the install script: `chmod +x ./install/install_deps.sh`

Adding the DYMO LabelWriter 450 printer
-------------------------------------------
1. Open Chromium and browse to [http://localhost:631/](http://localhost:631/).
2. Click **Administration** tab at the top and then click **Add Printer** under Printers.
3. In the **Authentication Required** dialog box, enter `pi` as the user name and `raspberry` as the password.
4. Click **Log In**.
5. In the Add Printer page, select **DYMO LabelWriter 450 (DYMO LabelWriter 450)** and then click **Continue**.
6. On the Add Printer page, review the Name and Description. Click **Continue**.
7. Select **DYMO LabelWriter 450** from the Model list.
8. Click **Add Printer**.
9. In the Set Default Options for DYMO_LabelWriter_450 page, set the following:
	* Media size: **30857 Badge Label**
	* Output Resolution: **300x600 DPI**
	* Halftoning: **Error Diffusion**
	* Print Density: **Normal**
	* Print Quality: **Barcodes and Graphics**
10. Click **Set Defaut Options**. You will be redirected to the Printers tab.
11. Click the **Administration** drop-down and select **Set As Server Default**.
12. Finally, close the browser and reboot the device.
After the Raspberry Pi startsup, Chromium should automatically open and display the login system.

