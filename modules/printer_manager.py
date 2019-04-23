import os, sys, base64, logging
import cups
from config import DEBUG, REDIS_HOST, REDIS_PORT, PRINT_CHECK_DELAY_SECONDS
import redis
import json
import time
from utils import get_script_path

PAGE_SIZE = "Custom.54x100mm"
IMAGE_FILE = "temp.png"

PRINT_MANAGER_REDIS_KEY = 'print_jobs'

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, charset="utf-8", db=0, decode_responses=True)


def send_to_printer(filepath=IMAGE_FILE, page_size=PAGE_SIZE):
    # Removing the prefix 'data:image/png;base64,'
    print('image data: {}'.format(filepath))
    img_file = os.path.join(os.sep, get_script_path(), IMAGE_FILE)
    os.system("lpr -o landscape -o PageSize={} -o fit-to-page  {}".format(page_size, img_file))


def add_file_to_print_queue(filename):
    r.rpush(PRINT_MANAGER_REDIS_KEY, filename)
    print('There are currently {} jobs waiting to be printed.'.format(r.llen(PRINT_MANAGER_REDIS_KEY)))


def listen_for_print_requests():
    try:
        while True:
            while r.llen(PRINT_MANAGER_REDIS_KEY) != 0:
                file_to_print = r.lpop(PRINT_MANAGER_REDIS_KEY)
                print('Noticed a file waiting to be printed: {}'.format(file_to_print), file=sys.stderr)
                send_to_printer(filepath=file_to_print)
            time.sleep(PRINT_CHECK_DELAY_SECONDS)

    except Exception as e:
        print("!!!!!!!!!! EXCEPTION IN PRINTER MANAGER !!!!!!!!!")
        print(str(e))


if __name__ == "__main__":
    from main import setup_logging

    setup_logging()
    listen_for_print_requests()
