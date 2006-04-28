"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#!/usr/bin/env python
import os
import sys

type, name, action = sys.argv[1:4]
path = "/apps/px/bin/%s" % type
pid = os.spawnl(os.P_NOWAIT, path, type, name, action)
