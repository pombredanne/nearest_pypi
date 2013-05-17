import subprocess
from config import Config


class Command(object):
    def run(self):

        subprocess.call([
            'wget',
            '-O',
            Config.GEOIP_PATH_V4,
            Config.GEOIP_DB_URL_IPV4,
        ])

        subprocess.call([
            'wget',
            '-O',
            Config.GEOIP_PATH_V6,
            Config.GEOIP_DB_URL_IPV6,
        ])

