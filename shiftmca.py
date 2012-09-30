
import os
import logging
logging.basicConfig(level=logging.DEBUG)

import sys
sys.path.append("..")
import pymclevel

root = "../bukkit/SERVER-beta-firstworld-anvil1.2.5/New World/region/renamed/"
for filename in os.listdir(root):
    path = root + filename
    
    print filename
    _, new_rx, rz, _ = filename.split(".")
    new_rx = int(new_rx)
    rz = int(rz)
    old_rx = new_rx - 20

    print "Processing",(old_rx,rz),"->",(new_rx,rz)

    region = pymclevel.infiniteworld.MCRegionFile(path, (new_rx,rz))
    print region
    region.repair()
    region.close()

