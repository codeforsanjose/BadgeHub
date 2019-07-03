import logging.config
import multiprocessing
import os
import argparse
from multiprocessing import Process

from BadgeHub.log_helper import setup_logging
from BadgeHub.nfc_manager import init_nfc
from BadgeHub.sheets_uploader import main
from app.nametag_server import start_webserver

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='BadgeHub: print name tags for visitors at your events!')
parser.add_argument('-w', action='store_true', help='Run just the web server')


def sheets_uploader():
    logger.info('Starting the uploader...{0}'.format(os.getpid()))
    main()


def login_server():
    logger.info('Starting the web server...{0}'.format(os.getpid()))
    start_webserver()


def nfc_listener():
    logger.info('Starting the NFC listener...{0}'.format(os.getpid()))
    init_nfc()


def init_all():
    multiprocessing.freeze_support()
    p1 = Process(target=sheets_uploader, args=())
    p2 = Process(target=login_server, args=())
    p3 = Process(target=nfc_listener, args=())
    p1.start()
    p2.start()
    p3.start()


if __name__ == "__main__":
    args = parser.parse_args()
    setup_logging()

    if args.w:
        login_server()
    else:
        init_all()
