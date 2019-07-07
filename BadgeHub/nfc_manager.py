#
# Uses The Adafruit PN532 NFC library
# https://github.com/adafruit/Adafruit_CircuitPython_PN532
#
import logging
import os

import redis
from adafruit_pn532.spi import PN532_SPI

from BadgeHub.redis_helper import set_nfc_status
from BadgeHub.config import REDIS_HOST, REDIS_PORT
from BadgeHub.image_creator import Nametag
from BadgeHub.printer_manager import send_to_printer
from BadgeHub.redis_helper import get_preferences
from BadgeHub.utils import get_script_path

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, charset="utf-8", db=0, decode_responses=True)

imports_ok = False
try:
    import board
    import busio
    from digitalio import DigitalInOut

    imports_ok = True
except NotImplementedError as e:
    print("Failed to initialize NFC manager; is this running on a Raspberry Pi?\n{}".format(str(e)))

logger = logging.getLogger(__name__)


def send_nfc_to_printer(nfc_serial_no, data):
    current_preferences = get_preferences(r)
    nametag = Nametag(text_line1=nfc_serial_no,
                      text_line2=None,
                      logo_scale=current_preferences['logo_scale'],
                      logo_x_offset_pct=current_preferences['logo_x_offset_pct'],
                      logo_y_offset_pct=current_preferences['logo_y_offset_pct'],
                      qr_max_width_pct=current_preferences['qr_max_width_pct'],
                      qr_x_offset_pct=current_preferences['qr_x_offset_pct'],
                      qr_y_offset_pct=current_preferences['qr_y_offset_pct'],
                      text_x_offset_pct=current_preferences['text_x_offset_pct'],
                      text_y_offset_pct=current_preferences['text_y_offset_pct'],
                      ttf_file=current_preferences['font_file'],
                      show_diag=False)

    img_file = os.path.join(os.sep, get_script_path(), 'nfc_test.png')
    nametag.save(filepath=img_file)

    logger.debug('Saved nametag image as "{}"'.format(img_file))
    send_to_printer(img_file)


def get_board_info():
    try:
        # SPI connection:
        spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
        cs_pin = DigitalInOut(board.D5)
        pn532 = PN532_SPI(spi, cs_pin, debug=False)
        ic, ver, rev, support = pn532.get_firmware_version()
        # print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
        return {'ic': ic, 'ver': ver, 'rev': rev, "support": support}
    except RuntimeError as e:
        print('NFC runtime error {}'.format(str(e)))
        return None


def listen_for_cards():
    # SPI connection:
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    cs_pin = DigitalInOut(board.D5)
    nfc_status = {}
    try:
        pn532 = PN532_SPI(spi, cs_pin, debug=False)
        ic, ver, rev, support = pn532.get_firmware_version()
        nfc_status = {'ic': ic, 'ver': ver, 'rev': rev, "support": support}
        set_nfc_status(r, nfc_status)
        # Configure PN532 to communicate with MiFare cards
        pn532.SAM_configuration()
    except RuntimeError as re:
        print(re)
        nfc_status['message'] = 'Failed to initialize the NFC reader. Check the connection to the reader.'
        set_nfc_status(r, nfc_status)
        logger.error(nfc_status['message'])
        return

    logger.debug('Waiting for RFID/NFC card...')
    while True:
        # Check if a card is available to read
        uid = pn532.read_passive_target(timeout=2.0)

        # Try again if no card is available.
        if uid is None:
            continue

        print('Found card with UID: {}'.format([hex(i) for i in uid]))

        mifare_contents = bytearray()
        block_no = 0
        while True:
            mifare_read_output = pn532.mifare_classic_read_block(block_no)
            if mifare_read_output is None or len(mifare_read_output) is 0:
                break
            mifare_contents.extend(mifare_read_output)
            block_no += 4
        print('mifare_contents read: {}'.format(mifare_contents.hex()))

        send_nfc_to_printer(nfc_serial_no=':'.join([hex(i) for i in uid]), data=mifare_contents.hex())


def init_nfc():
    if not imports_ok:
        logger.error("Cannot start NFC.")
        set_nfc_status(r, {'message': "Cannot start NFC."})
        return
    listen_for_cards()


if __name__ == '__main__':
    from BadgeHub.log_helper import setup_logging

    setup_logging()
    init_nfc()
