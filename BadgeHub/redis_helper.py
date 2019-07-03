import json
from redis import Redis
import logging

from BadgeHub.config import DEFAULT_PREFERENCES

logger = logging.getLogger(__name__)


def get_preferences(redis_instance: Redis):
    prefs_dict = DEFAULT_PREFERENCES
    stored_preferences = redis_instance.get('preferences')
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
