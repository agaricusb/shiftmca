import sys
sys.path.append("..")
import pymclevel

root = "../bukkit/SERVER-beta-firstworld-anvil1.2.5/New World/region/renamed/"
filename = root + "r.17.0.mca"

region = pymclevel.infiniteworld.MCRegionFile(filename, (17, 0))
print region
