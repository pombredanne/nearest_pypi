from math import radians, cos, sin, asin, sqrt
import socket
from pygeoip import GeoIP, MEMORY_CACHE
from redis.client import StrictRedis
from config import Config
from models import Mirror
from logging import getLogger

log = getLogger(__name__)


FALLBACK_MIRROR = "a.pypi.python.org"
MIRROR_KEY = "mirror:{}"


class MirrorDistance(object):
    _geoip4 = None
    _geoip6 = None

    def __init__(self):
        if not self.__class__._geoip4:
            self.__class__._geoip4 = GeoIP(Config.GEOIP_V4_PATH, MEMORY_CACHE)
        if not self.__class__._geoip6:
            self.__class__._geoip6 = GeoIP(Config.GEOIP_V6_PATH, MEMORY_CACHE)
        self.redis = StrictRedis(Config.REDIS['HOST'], Config.REDIS['PORT'], Config.REDIS['DB'])

    def _haversine(self, lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(lambda v: radians(float(v)), [lon1, lat1, lon2, lat2])
        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        km = 6367 * c # convert to km
        return km

    def get_nearest_mirror(self, address):
        key = MIRROR_KEY.format(address)
        mirror = self.redis.get(key)
        if not mirror:
            try:
                if ":" in address:
                    record = self._geoip6.record_by_addr(address)
                else:
                    record = self._geoip4.record_by_addr(address)
            except socket.error:
                return FALLBACK_MIRROR
            if not record:
                return FALLBACK_MIRROR
            lat = record['latitude']
            lon = record['longitude']

            distance = 99999
            for candidate in Mirror.objects.filter(age__lt=3601):
                if candidate.name == "a.pypi.pyton.org":
                    # we don't want to use a.pypi in general
                    continue
                new_distance = self._haversine(lon, lat, candidate.lon, candidate.lat)
                if new_distance < distance:
                    distance = new_distance
                    mirror = candidate.name

            if mirror:
                self.redis.set(key, mirror)
                self.redis.expire(key, 60 * 60 * 24 * 120)  # 120 days
        return mirror


if __name__ == "__main__":
    m = MirrorDistance()
    m.get_nearest_mirror("5.9.5.200")
