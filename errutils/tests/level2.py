import sys
from errutils import erlogging
logger = erlogging.setup(lambda depth: sys._getframe(depth), debug=True)

import level1

print("Level 2: %s" % (logger.name))
