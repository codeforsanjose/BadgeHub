import os, multiprocessing
from multiprocessing import Process
import json
import logging
import logging.config
from modules.sheets_uploader import main
from nametag_server import start_webserver
# from printer_manager import listen_for_print_requests

logger = logging.getLogger(__name__)

def sheets_uploader():
    logger.info('Starting the uploader...{0}'.format(os.getpid()))
    main()

def login_server():
    logger.info('Starting the web server...{0}'.format(os.getpid()))
    start_webserver()

# def print_listener():
#   logger.info('Starting the printer manager...{0}'.format(os.getpid()))
#   listen_for_print_requests()

def parent():
    multiprocessing.freeze_support()
    p1 = Process(target = sheets_uploader, args = ())
    p2 = Process(target = login_server, args = ())
    # p3 = Process(target = print_listener, args = ())
    p1.start()
    p2.start()
    # p3.start()

def setup_logging( default_path='logging.json', default_level=logging.INFO, env_key='LOG_CFG'):
    """
    Setup logging configuration
    see https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

if __name__ == "__main__":
    setup_logging()
    parent()