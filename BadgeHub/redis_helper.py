import json
from redis import Redis
import logging

from BadgeHub.config import DEFAULT_PREFERENCES
from BadgeHub.utils import convert_to_dict

logger = logging.getLogger(__name__)

REDIS_KEY_PREFERENCES = 'preferences'
REDIS_KEY_PRINTER_INFO = 'printer_info'
REDIS_KEY_NFC_INFO = 'nfc_info'


def get_preferences(redis_instance: Redis):
    prefs_dict = DEFAULT_PREFERENCES
    stored_preferences = redis_instance.get(REDIS_KEY_PREFERENCES)
    logger.debug('redis returned {}'.format(str(stored_preferences)))
    if stored_preferences is not None:
        prefs_dict = json.loads(stored_preferences)
        logger.debug('Read preferences as:')
        for p in prefs_dict:
            logger.debug('{}:{}'.format(p, prefs_dict[p]))
    else:
        logger.info("Preferences are currently empty; returning defaults")
        return prefs_dict

    for pref in DEFAULT_PREFERENCES:
        if prefs_dict.get(pref) is None:
            logger.info('preference for "{}" is empty, resetting it to "{}"'
                        .format(pref, DEFAULT_PREFERENCES[pref]))
            prefs_dict[pref] = DEFAULT_PREFERENCES[pref]
    return prefs_dict


def set_preferences(redis_instance: Redis, prefs_dict):
    json_prefs = json.dumps(prefs_dict)
    logger.debug("setting preferences: {}".format(json_prefs))
    redis_instance.set(REDIS_KEY_PREFERENCES, json_prefs)


def get_printer_status(redis_instance: Redis):
    stored_printer_info = redis_instance.get(REDIS_KEY_PRINTER_INFO)
    if stored_printer_info is None:
        return {}
    return json.loads(stored_printer_info)


def set_printer_status(redis_instance: Redis, info_dict):
    printer_status_json = json.dumps(info_dict, sort_keys=True, default=convert_to_dict)
    logger.debug("updating printer status: {}".format(printer_status_json))
    redis_instance.set(REDIS_KEY_PRINTER_INFO, printer_status_json)


def get_nfc_status(redis_instance: Redis):
    stored_nfc_info = redis_instance.get(REDIS_KEY_NFC_INFO)
    if stored_nfc_info is None:
        return {}
    return json.loads(stored_nfc_info)


def set_nfc_status(redis_instance: Redis, info_dict):
    printer_status_json = json.dumps(info_dict, sort_keys=True, default=convert_to_dict)
    logger.debug("updating nfc status: {}".format(printer_status_json))
    redis_instance.set(REDIS_KEY_NFC_INFO, printer_status_json)
