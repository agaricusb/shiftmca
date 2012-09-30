
import itertools
import zlib
import os
import struct
import logging
logging.basicConfig(level=logging.DEBUG)

import sys
sys.path.append("..")
import pymclevel

import numpy

root = "../bukkit/SERVER-beta-firstworld-anvil1.2.5/New World/region/renamed/"
for filename in os.listdir(root):
    path = root + filename
    
    print filename
    _, new_rx, rz, _ = filename.split(".")
    new_rx = int(new_rx)
    rz = int(rz)
    old_rx = new_rx - 20

    print "Processing",(old_rx,rz),"->",(new_rx,rz)

    f = file(path, "rb")
    SECTOR_BYTES = 4096
    offsets = numpy.fromstring(f.read(SECTOR_BYTES), dtype='>u4')   # infiniteworld.py __init__
    modtimes = numpy.fromstring(f.read(SECTOR_BYTES), dtype='>u4')

    print offsets,modtimes

    def getOffset(cx, cz):
        return offsets[cx + cz * 32]

    def readChunkRaw(cx, cz):
        offset = getOffset(cx, cz)
        sectorStart = offset >> 8
        numSectors = offset & 0xff

        f.seek(sectorStart * SECTOR_BYTES)
        data = f.read(numSectors * SECTOR_BYTES)
        if data is None or len(data) == 0:
            return None
        return data

    def readChunk(cx, cz):
        rawData = readChunkRaw(cx, cz)
        if rawData is None:
            print "No chunk ",cx,cz
            return None
        length = struct.unpack_from(">I", rawData)[0]
        compressionFormat = struct.unpack_from("B", rawData, 4)[0]
        compressedData = rawData[5:length + 5]
        VERSION_GZIP = 1
        VERSION_DEFLATE = 2
        if compressionFormat == VERSION_GZIP:
            tag = pymclevel.nbt.load(buf=pymclevel.nbt.gunzip(compressedData))
        elif compressionFormat == VERSION_DEFLATE:
            tag = pymclevel.nbt.load(buf=zlib.decompress(compressedData))
        else:
            raise Exception("Unrecognized compression format: "+compressionFormat)

        return tag

    def allChunks():
        for cx, cz in itertools.product(range(32), range(32)):
            chunk = readChunk(cx, cz)

            print cx,cz,chunk

    print [allChunks()]

    #region = pymclevel.infiniteworld.MCRegionFile(path, (new_rx,rz))
    #print region
    #region.repair()
    #region.close()

