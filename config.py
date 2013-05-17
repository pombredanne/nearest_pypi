import logging
import socket
from unipath import Path


class BaseConfig(object):
    DEBUG = False
    TESTING = False
    LOG_LEVEL = logging.INFO

    SITE_ROOT = Path(__file__).absolute().parent
    STDNET_DB_URL = "redis://localhost:6379?db=0"
    GEOIP_DB_URL_IPV4 = "http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz"
    GEOIP_DB_URL_IPV6 = "http://geolite.maxmind.com/download/geoip/database/GeoLiteCityv6-beta/GeoLiteCityv6.dat.gz"
    GEOIP_V4_PATH = SITE_ROOT.child("data", "GeoLiteCity.dat")
    GEOIP_V6_PATH = SITE_ROOT.child("data", "GeoLiteCityv6.dat")

    REDIS = {
        'HOST': "localhost",
        'PORT': 6379,
        'DB': 0,
    }


class Live(BaseConfig):
    pass


class Devel(BaseConfig):
    DEBUG = True
    TESTING = True
    LOG_LEVEL = logging.DEBUG


config_map = {
    "oxygen.ulo.pe": Live,
    "argon": Devel,
    "argon.local": Devel,
}

current_hostname = socket.getfqdn()
Config = config_map.get(current_hostname, Live)
