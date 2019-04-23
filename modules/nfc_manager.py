#
# Uses The Adafruit PN532 NFC library
# https://github.com/adafruit/Adafruit_CircuitPython_PN532
#
import board
import busio
import sys
from digitalio import DigitalInOut

from adafruit_pn532.spi import PN532_SPI


def getBoardInfo():
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


def listenForCards():
    # SPI connection:
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    cs_pin = DigitalInOut(board.D5)
    pn532 = PN532_SPI(spi, cs_pin, debug=False)
    # Configure PN532 to communicate with MiFare cards
    pn532.SAM_configuration()

    print('Waiting for RFID/NFC card...')
    while True:
        # Check if a card is available to read
        uid = pn532.read_passive_target(timeout=0.5)
        print('.', end="")
        sys.stdout.flush()
        # Try again if no card is available.
        if uid is not None:
            print('Found card with UID: {}'.format([hex(i) for i in uid]))
