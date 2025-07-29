from sys import stdout

from ..consts import *
from .api.client import *
from .api.enums import *
from .models import *
from .scraper.client import *

logger.remove()
logger.add(stdout, level="INFO")
