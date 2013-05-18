from stdnet import odm
from stdnet.odm.fields import SymbolField, CharField, IntegerField, DateTimeField
from stdnet.odm.models import StdModel
from config import Config
from distance import MirrorDistance


class Mirror(StdModel):
    name = SymbolField(unique=True)
    age = IntegerField(index=True)
    lat = CharField()
    lon = CharField()

    def __unicode__(self):
        return u"{self.name} -> {self.lat}:{self.lon}".format(self=self)

    def get_nearest_mirror(self, address):
        return MirrorDistance().get_nearest_mirror(address)


odm.register(Mirror, Config.STDNET_DB_URL)
