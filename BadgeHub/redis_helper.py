import json
from redis import Redis, ConnectionError
from typing import Dict

import logging

from BadgeHub.config import REDIS_HOST, REDIS_PORT
from BadgeHub.utils import convert_to_dict
from BadgeHub.models.badge_profile import BadgeProfile

logger = logging.getLogger(__name__)

REDIS_KEY_PREFERENCES = 'preferences'
REDIS_KEY_PRINTER_INFO = 'printer_info'
REDIS_KEY_NFC_INFO = 'nfc_info'
REDIS_KEY_NFC_INTAKE = 'nfc_cards_intake'
REDIS_KEY_PROFILE_ID_COUNTER = 'profile_id_counter'

__cached_redis_instance = None


def redis_instance() -> Redis or None:
    global __cached_redis_instance
    if __cached_redis_instance is not None:
        return __cached_redis_instance
    try:
        r = Redis(host=REDIS_HOST, port=REDIS_PORT, charset="utf-8", db=0, decode_responses=True)
        __cached_redis_instance = r
        return __cached_redis_instance
    except ConnectionError:
        logger.error("No connection to Redis instance.")
    return None


def get_preferences_for_id(redis_instance: Redis, profile_id: int) -> BadgeProfile or None:
    try:
        stored_preferences = get_preferences(redis_instance)
    except ConnectionError:
        logger.error("No connection to Redis instance.")
        return None
    if profile_id in stored_preferences:
        return stored_preferences[profile_id]
    return None


def get_default_profile(redis_instance: Redis) -> BadgeProfile or None:
    try:
        prefs = get_preferences(redis_instance)
    except ConnectionError:
        logger.error("No connection to Redis instance.")
        return None
    for p in prefs.keys():
        if prefs[p].is_current_profile:
            return prefs[p]
    return None


def get_preferences(redis_instance: Redis) -> Dict[int, BadgeProfile]:
    try:
        stored_preferences = redis_instance.get(REDIS_KEY_PREFERENCES)
    except ConnectionError:
        logger.error("No connection to Redis instance.")
        return {}
    logger.debug('redis returned {}'.format(str(stored_preferences)))

    # load these into proper BadgeProfile objects
    dict_result = {}
    if stored_preferences is not None:
        prefs = json.loads(stored_preferences)
        logger.debug('Read preferences as:')
        for p in prefs.keys():
            profile = BadgeProfile.from_dict(prefs[p])
            dict_result[profile.profile_id] = profile
            logger.debug('profile #{}'.format(profile.profile_id))
    return dict_result

def get_next_profile_id(redis_instance: Redis) -> int:
    try:
        # TODO: potential issue here with reloading profiles, we'd have to set this as well and export the value out with any backup.
        profile_id = redis_instance.incr(REDIS_KEY_PROFILE_ID_COUNTER)
        return profile_id
    except ConnectionError:
        logger.error("No connection to Redis instance.")
        return None


def set_profile(redis_instance: Redis, profile: BadgeProfile) -> None:
    try:
        stored_preferences = get_preferences(redis_instance)
    except ConnectionError:
        logger.error("No connection to Redis instance.")
        return None
    stored_preferences[profile.profile_id] = profile
    logger.debug("setting preferences")
    json_prefs = json.dumps(stored_preferences, sort_keys=True, default=convert_to_dict)
    redis_instance.set(REDIS_KEY_PREFERENCES, json_prefs)


def get_printer_status(redis_instance: Redis) -> dict:
    try:
        stored_printer_info = redis_instance.get(REDIS_KEY_PRINTER_INFO)
    except ConnectionError:
        logger.error("No connection to Redis instance.")
        return {}
    if stored_printer_info is None:
        return {}
    return json.loads(stored_printer_info)


def set_printer_status(redis_instance: Redis, info_dict: dict) -> None:
    printer_status_json = json.dumps(info_dict, sort_keys=True, default=convert_to_dict)
    logger.debug("updating printer status: {}".format(printer_status_json))
    try:
        redis_instance.set(REDIS_KEY_PRINTER_INFO, printer_status_json)
    except ConnectionError:
        logger.error("No connection to Redis instance.")
        return None


def get_nfc_status(redis_instance: Redis) -> dict:
    try:
        stored_nfc_info = redis_instance.get(REDIS_KEY_NFC_INFO)
    except ConnectionError:
        logger.error("No connection to Redis instance.")
        return {}
    if stored_nfc_info is None:
        return {}
    return json.loads(stored_nfc_info)


def set_nfc_status(redis_instance: Redis, info_dict) -> None:
    nfc_status_json = json.dumps(info_dict, sort_keys=True, default=convert_to_dict)
    logger.debug("updating nfc status: {}".format(nfc_status_json))
    try:
        redis_instance.set(REDIS_KEY_NFC_INFO, nfc_status_json)
    except ConnectionError:
        logger.error("No connection to Redis instance.")


def push_nfc_card_read(redis_instance: Redis, nfc_data_dict) -> None:
    nfc_card_data_json = json.dumps(nfc_data_dict, sort_keys=True, default=convert_to_dict)
    logger.debug("posting nfc data: {}".format(nfc_card_data_json))
    try:
        redis_instance.rpush(REDIS_KEY_NFC_INTAKE, nfc_card_data_json)
    except ConnectionError:
        logger.error("No connection to Redis instance.")


def pop_nfc_card_read(redis_instance: Redis) -> int:
    try:
        stored_nfc_card_data = redis_instance.lpop(REDIS_KEY_NFC_INTAKE)
    except ConnectionError:
        logger.error("No connection to Redis instance.")
        return 0
    if stored_nfc_card_data is None:
        return 0
    return json.loads(stored_nfc_card_data)


def get_nfc_card_queue_count(redis_instance: Redis) -> int:
    try:
        stored_nfc_card_count = redis_instance.llen(REDIS_KEY_NFC_INTAKE)
    except ConnectionError:
        logger.error("No connection to Redis instance.")
        return 0
    if stored_nfc_card_count is None:
        return 0
    return stored_nfc_card_count


def peek_nfc_queue(redis_instance: Redis) -> list:
    card_count = get_nfc_card_queue_count(redis_instance)
    try:
        nfc_queue = redis_instance.lrange(REDIS_KEY_NFC_INTAKE, 0, card_count)
    except ConnectionError:
        logger.error("No connection to Redis instance.")
        return 0
    if nfc_queue is None:
        return 0
    card_list = []
    for card in nfc_queue:
        card_list.append(json.loads(card))
    return card_list