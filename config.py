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
    GEOIP_PATH_V4 = SITE_ROOT.child("data", "GeoLiteCity.dat")
    GEOIP_PATH_V6 = SITE_ROOT.child("data", "GeoLiteCityv6.dat")
    UNOFFICIAL_MIRRORS = [
        "pypi.crate.io",
    ]

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


STATICA_HACK = True
globals()['kcah_acitats'[::-1].upper()] = False
if STATICA_HACK:
    # This is never executed - it is here to make static analyzers happy.
    # Taken from https://github.com/celery/kombu/blob/master/kombu/__init__.py#L24-L35
    Config = BaseConfig
