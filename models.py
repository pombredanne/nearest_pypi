from stdnet import odm
from stdnet.odm.fields import SymbolField, CharField, IntegerField, DateTimeField
from stdnet.odm.models import StdModel
from config import Config


class Mirror(StdModel):
    name = SymbolField(unique=True)
    age = IntegerField(index=True)
    lat = CharField()
    lon = CharField()

    def __unicode__(self):
        return u"{self.name} -> {self.lat}:{self.lon}".format(self=self)

    @staticmethod
    def get_nearest_mirror(address):
        from distance import DistanceCalculator
        return DistanceCalculator().get_nearest_mirror(address)

    @staticmethod
    def get_mirror_distances(address):
        from distance import DistanceCalculator, GeoIPLookupError
        try:
            return DistanceCalculator().get_mirror_distances(address)
        except GeoIPLookupError:
            return {}


odm.register(Mirror, Config.STDNET_DB_URL)
