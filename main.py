import os, multiprocessing
from multiprocessing import Process
from uploader import main
from nametag_server import start_webserver

def sheets_uploader():
   print('\nStarting the uploader...',  os.getpid())
   main()  

def login_server():
   print('\nStarting the web server...',  os.getpid())
   start_webserver()  

def parent():
  multiprocessing.freeze_support()
  p1 = Process(target = sheets_uploader, args = ())
  p2 = Process(target = login_server, args = ())
  p1.start()
  p2.start()

if __name__ == "__main__":
  parent()