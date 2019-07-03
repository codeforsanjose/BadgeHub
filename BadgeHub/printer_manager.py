import os
import sys
import time

import redis

from BadgeHub.config import REDIS_HOST, REDIS_PORT, PRINT_CHECK_DELAY_SECONDS
from BadgeHub.utils import get_script_path

PAGE_SIZE = "Custom.54x100mm"
IMAGE_FILE = os.path.join(os.sep, get_script_path(), "temp.png")

PRINT_MANAGER_REDIS_KEY = 'print_jobs'

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, charset="utf-8", db=0, decode_responses=True)


def send_to_printer(filepath=IMAGE_FILE, page_size=PAGE_SIZE):
    print('image data: {}'.format(filepath))
    os.system("lpr -o landscape -o PageSize={} -o fit-to-page  {}".format(page_size, filepath))


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
    from BadgeHub.log_helper import setup_logging

    setup_logging()
    listen_for_print_requests()
