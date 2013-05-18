from collections import OrderedDict
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


class GeoIPLookupError(Exception):
    pass


class DistanceCalculator(object):
    _geoip4 = None
    _geoip6 = None

    def __init__(self):
        # Load the GeoIP databases into class attributes since they each need 20+ MB in memory
        if not self.__class__._geoip4:
            self.__class__._geoip4 = GeoIP(Config.GEOIP_PATH_V4, MEMORY_CACHE)
        if not self.__class__._geoip6:
            self.__class__._geoip6 = GeoIP(Config.GEOIP_PATH_V6, MEMORY_CACHE)
        self.redis = StrictRedis(Config.REDIS['HOST'], Config.REDIS['PORT'], Config.REDIS['DB'])

    @staticmethod
    def _haversine(lon1, lat1, lon2, lat2):
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
        km = 6367 * c  # convert to km
        return km

    def get_mirror_distances(self, address):
        key = MIRROR_KEY.format(address)
        distances = OrderedDict(self.redis.zrange(key, 0, -1, withscores=True, score_cast_func=int))
        if not distances:
            try:
                if ":" in address:
                    record = self._geoip6.record_by_addr(address)
                else:
                    record = self._geoip4.record_by_addr(address)
            except socket.error:
                raise GeoIPLookupError()
            if not record:
                raise GeoIPLookupError()
            lat = record['latitude']
            lon = record['longitude']

            distances = OrderedDict(
                (mirror.name, self._haversine(lon, lat, mirror.lon, mirror.lat))
                for mirror in Mirror.objects.filter(age__lt=3601)
            )
            if distances:
                self.redis.zadd(key, **distances)
                self.redis.expire(key, 60 * 60 * 24)  # one day
        return distances

    def get_nearest_mirror(self, address):
        try:
            distances = self.get_mirror_distances(address)
            if distances:
                return next(distances.iteritems())[0]
            return FALLBACK_MIRROR
        except GeoIPLookupError:
            return FALLBACK_MIRROR


if __name__ == "__main__":
    m = DistanceCalculator()
    m.get_nearest_mirror("5.9.5.200")
