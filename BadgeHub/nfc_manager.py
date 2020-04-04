#
# Takes portions of code from:
# https://github.com/nfcpy/nfcpy/blob/a302ac4c803c1c0857ad9b1ed1fb967f5c66d1d3/examples/tagtool.py
#
# TODO: might want to check record.type and pass the type along
#  or handle text records (urn:nfc:wkt:T) differently from URI records (urn:nfc:wkt:U)
#  see https://nfc-forum.org/our-work/specification-releases/specifications/nfc-forum-assigned-numbers-register/
#
import logging
import os
import errno
import redis
import nfc
import time

from BadgeHub.redis_helper import set_nfc_status, push_nfc_card_read, get_nfc_card_queue_count, peek_nfc_queue, \
    pop_nfc_card_read, get_default_profile
from BadgeHub.config import REDIS_HOST, REDIS_PORT
from BadgeHub.image_creator import Nametag
from BadgeHub.printer_manager import send_to_printer
from BadgeHub.redis_helper import get_preferences
from BadgeHub.utils import get_script_path

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, charset="utf-8", db=0, decode_responses=True)

logger = logging.getLogger(__name__)

debounce_min_ms = 10 * 1000

# set to true to empty the card queue, for testing.
clear_card_queue = False


def cleanup_cache(cache: dict) -> dict:
    """
    Keep only the items which are recent enough to be useful.
    """
    current_time_ms = int(round(time.time() * 1000))
    cleaned_cache = dict(filter(lambda x: current_time_ms - x[1] < debounce_min_ms, cache.items()))
    logger.info(f'cleaning up cache:\noriginal: {cache}\nclean:{cleaned_cache}')
    return cleaned_cache


class NfcHandler:

    def __init__(self):
        self.firmware_info = {}
        self.status_message = None
        self.clf = nfc.ContactlessFrontend()
        self.init_nfc()
        self.debounced = {}

    def __exit__(self, exc_type, exc_value, traceback):
        logger.debug('closing NFC connection.')
        self.clf.close()

    def init_nfc(self):
        connection_types = ['tty', 'usb']
        for connection_type in connection_types:
            try:
                self.clf = nfc.ContactlessFrontend(connection_type)
            except IOError as error:
                if error.errno == errno.ENODEV:
                    logger.info(f'no contactless reader found on {connection_type}')
                elif error.errno == errno.EACCES:
                    logger.info(f'access denied for device with path {connection_type}')
                elif error.errno == errno.EBUSY:
                    logger.info(f'the reader on {connection_type} is busy')
                else:
                    logger.debug(f'{repr(error)} when trying {connection_type}')
            else:
                logger.debug(f'opened connection with NFC reader over {connection_type}')
                return

        logger.error("no contactless reader available")
        raise SystemExit(1)

    def send_nfc_to_printer(self, nfc_serial_no, data):
        current_profile = get_default_profile(r)
        nametag = Nametag(text_line1=nfc_serial_no,
                          text_line2=None,
                          logo_scale=current_profile.logo_scale,
                          logo_x_offset_pct=current_profile.logo_x_offset_pct,
                          logo_y_offset_pct=current_profile.logo_y_offset_pct,
                          qr_max_width_pct=current_profile.qr_max_width_pct,
                          qr_x_offset_pct=current_profile.qr_x_offset_pct,
                          qr_y_offset_pct=current_profile.qr_y_offset_pct,
                          text_x_offset_pct=current_profile.text_x_offset_pct,
                          text_y_offset_pct=current_profile.text_y_offset_pct,
                          ttf_file=current_profile.font_file,
                          show_diag=False)

        img_file = os.path.join(os.sep, get_script_path(), 'nfc_test.png')
        nametag.save(filepath=img_file)

        logger.debug('Saved nametag image as "{}"'.format(img_file))
        send_to_printer(img_file)

    def get_board_info(self):
        if self.clf.device is None:
            self.init_nfc()
        current_time_ms = int(round(time.time() * 1000))
        self.firmware_info = {
            'vendor': self.clf.device.vendor_name,
            'product': self.clf.device.product_name,
            'chipset': self.clf.device.chipset_name,
            'path': self.clf.device.path,
            'last_seen_utc_ms': current_time_ms
        }
        set_nfc_status(r, self.firmware_info)

    def listen_for_cards(self):
        if self.clf.device is None:
            self.init_nfc()

        groups = ['rdwr', 'card', 'dbg', 'clf']
        llcp_options = None
        rdwr_options = {
            'on-startup': self.on_rdwr_startup,
            'on-connect': self.on_rdwr_connect,
        }
        card_options = {
            'on-startup': self.on_card_startup,
            'on-connect': self.on_card_connect,
            'on-release': self.on_card_release,
            'targets': [],
        }
        kwargs = {
            'llcp': llcp_options,
            'rdwr': rdwr_options,
            'card': card_options
        }
        # while True:
        #     self.clf.connect(**kwargs)
        tag = None
        while tag is None:
            tag = self.clf.connect(**kwargs)
            if tag is not None:
                logger.info('activated as {}'.format(tag))
                if tag.ndef is not None:
                    for record in tag.ndef.records:
                        logger.info(record)
                tag = None

    def on_rdwr_startup(self, targets):
        return targets

    def on_rdwr_connect(self, tag):
        logger.info(f'connected to tag {tag}')

        if tag.ndef:
            logger.info("NDEF Capabilities:")
            identifier = ':'.join(format(x, '02x') for x in tag.identifier).upper()
            logger.info(f"ID: {identifier}")
            current_time_ms = int(round(time.time() * 1000))

            # FIXME: pull this out into its own class
            if identifier in self.debounced:
                time_elapsed = current_time_ms - self.debounced[identifier]
                if time_elapsed < debounce_min_ms:
                    logger.info(f"ignoring recently seen tag with ID {identifier}")
                    return
            self.debounced[identifier] = current_time_ms
            self.debounced = cleanup_cache(self.debounced)

            readable = tag.ndef.is_readable
            writeable = tag.ndef.is_writeable
            logger.info(f"  readable  = {'yes' if readable else 'no'}")
            logger.info(f"  writeable = {'yes' if writeable else 'no'}")
            logger.info(f"  capacity  = {tag.ndef.capacity} byte")
            logger.info(f"  message   = {tag.ndef.length} byte")
            if tag.ndef.length > 0:
                logger.info("NDEF Message:")
                records = []
                for i, record in enumerate(tag.ndef.records):
                    record_text = record.text.replace('\x00', '')
                    logger.info(f"record {i + 1}")
                    logger.info(f"  type = {record.type}")
                    logger.info(f"  text = '{record_text}'")
                    logger.info(f"  name = {repr(record.name)}")
                    logger.info(f"  data = {repr(record.data)}")
                    records.append({
                        'record_number': i,
                        'text': record_text,
                        'type': record.type
                    })
                push_nfc_card_read(r, {
                    'id': identifier,
                    'timestamp': current_time_ms,
                    'records': records
                })

    def on_card_startup(self, target):
        # logger.warning('on_card_startup should be customized')
        return None

    def on_card_connect(self, tag):
        logger.info('activated as {}'.format(tag))
        if tag is not None:
            return tag
        return None

    def on_card_release(self, tag):
        return tag


def init_nfc():
    cards_queued = get_nfc_card_queue_count(r)
    logger.info(f'currently {cards_queued} unprocessed tags in queue')
    if clear_card_queue:
        for i in range(0, cards_queued):
            logger.info(f'popped card: {pop_nfc_card_read(r)}')
    if cards_queued > 0:
        card_queue = peek_nfc_queue(r)
        for card in card_queue:
            logger.info(f'{card}')
    handler = NfcHandler()
    handler.get_board_info()
    handler.listen_for_cards()


if __name__ == '__main__':
    from BadgeHub.log_helper import setup_logging

    setup_logging()
    init_nfc()
