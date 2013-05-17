from datetime import datetime, timedelta
import socket
from pygeoip import GeoIP
from pypimirrors.pypimirrors import mirror_statuses
from redis.client import StrictRedis
from stdnet.exceptions import ObjectNotFound
import time
from models import Mirror
from logging import getLogger
from config import Config

log = getLogger(__name__)


KEY_LAST_UPDATE = "nearest_pypi:last_update:{}"


class Command(object):
    def __init__(self):
        self.redis = StrictRedis(Config.REDIS['HOST'], Config.REDIS['PORT'], Config.REDIS['DB'])

    def run(self):
        log.info("Updating mirror database")
        geoip = GeoIP(Config.GEOIP_V4_PATH)

        last_update = None
        for status in mirror_statuses():
            name = status['mirror']
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
            last_update = datetime.now()

        self.redis.set(KEY_LAST_UPDATE.format(socket.getfqdn()), time.time())
        log.info("Finished updating mirror database")


if __name__ == "__main__":
    Command().run()
