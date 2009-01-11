from tg.controllers import TGController
from catwalk.tg2 import Catwalk

from catwalk.test.model import DBSession, metadata

class RootController(TGController):
    catwalk = Catwalk(DBSession, metadata)
