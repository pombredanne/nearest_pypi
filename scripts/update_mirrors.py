from datetime import timedelta
import logging
from pygeoip import GeoIP
from pypimirrors.pypimirrors import mirror_statuses
from redis.client import StrictRedis
from stdnet.exceptions import ObjectNotFound
import time
from models import Mirror
from logging import getLogger
from config import Config

log = getLogger(__name__)
logging.basicConfig(level=Config.LOG_LEVEL)


class Command(object):
    def __init__(self):
        self.redis = StrictRedis(Config.REDIS['HOST'], Config.REDIS['PORT'], Config.REDIS['DB'])

    def run(self):
        log.debug("Updating mirror database")
        geoip = GeoIP(Config.GEOIP_PATH_V4)

        for status in mirror_statuses(unofficial_mirrors=Config.UNOFFICIAL_MIRRORS):
            name = status['mirror']
            if name == "a.pypi.python.org":
                # don't include 'a' in the list of mirrors - it's no mirror after all
                continue
            time_diff = status['time_diff']
            if not isinstance(time_diff, timedelta):
                continue

            log.debug("  Processing mirror '%s'", name)
            record = geoip.record_by_name(name)
            lat = record['latitude']
            lon = record['longitude']

            log.debug("    Age: %d, Lat: %0.5f, Lon: %0.5f", time_diff.total_seconds(), lat, lon)

            try:
                mirror = Mirror.objects.get(name=name)
            except ObjectNotFound:
                mirror = Mirror(name=name)
            mirror.age = time_diff.total_seconds()
            mirror.lat = lat
            mirror.lon = lon

            mirror.save()

        self.redis.set(Config.KEY_LAST_UPDATE, time.time())
        log.debug("Finished updating mirror database")


if __name__ == "__main__":
    Command().run()
