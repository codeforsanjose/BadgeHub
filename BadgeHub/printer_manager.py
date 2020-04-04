import os
import sys
import time
from subprocess import PIPE, run
import cups
import redis

from BadgeHub.redis_helper import set_printer_status
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


def get_printer_info():
    printer_device_info = []
    conn = cups.Connection()
    printers = conn.getPrinters()
    cups_default = conn.getDefault()
    for printer in printers:
        classes = conn.getClasses()
        printer_attrs = conn.getPrinterAttributes(name=printer,
                                                 requested_attributes=['job-sheets-supported', 'job-sheets-default'])
        print(printer, printers[printer]["printer-info"], printers[printer]['printer-make-and-model'])

        # FIXME: this should return a list of every printer connected, not just the default.
        #   Look into doing this as a C function so that we can tie directly into the CUPS API.

        # Now get which PageSize/Media Size is set as default
        result = run(["lpoptions", "-l", "-p", printer], stdout=PIPE, stderr=PIPE, universal_newlines=True)
        if result.returncode is not 0:
            print('Error getting PageSize/Media Size default values:\n{}'.format(result.stderr))
            # TODO: update Redis with the printer error
            return

        default_page_size = False
        for line in result.stdout.splitlines():
            if line.strip().startswith('PageSize/Media Size:'):
                media_type_list = line.split(':')[1]
                media_type_list = media_type_list.strip().split(' ')
                for media_type in media_type_list:
                    if media_type.strip().startswith('*'):
                        default_page_size = media_type.replace('*', '')
        current_time_ms = int(round(time.time() * 1000))
        printer_device_info.append({
            'printer_model': printers[printer]['printer-make-and-model'],
            'default_printer': True,
            'online': False,
            'default_media_size': default_page_size,
            'last_seen_utc_ms': current_time_ms
        })

    return printer_device_info


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
    # from BadgeHub.log_helper import setup_logging

    # setup_logging()
    # listen_for_print_requests()
    p_info = get_printer_info()
    set_printer_status(r, p_info)
