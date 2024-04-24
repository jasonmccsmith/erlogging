import sys
from errutils import erlogging
logger = erlogging.setup(lambda depth: sys._getframe(depth), debug=True)

print("Level 1: %s" % (logger.name))