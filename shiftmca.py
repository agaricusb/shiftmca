
import logging
logging.basicConfig(level=logging.DEBUG)

import sys
sys.path.append("..")
import pymclevel

root = "../bukkit/SERVER-beta-firstworld-anvil1.2.5/New World/region/renamed/"
filename = root + "r.20.0.mca"

region = pymclevel.infiniteworld.MCRegionFile(filename, (20, 0))
#region.extractAllChunks("/tmp/2")
print region
region.repair()
region.close()

