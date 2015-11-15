# CFSJ-Login-System
Raspberry Pi, Dymo Turbo Writer 450 badge printing service that logs user information such as name and email and prints a name badge and QR code associated with that information.

Repositories used:

QR Scanner:
zbar
shell script to terminate zbar and camera

QR Encoder:

Printer:
CUPS - edited filter.conf file... changed ps_accounting:1 to ps_accounting:0
      sudo nano /etc/foomatic/filter.conf
