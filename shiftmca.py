
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

RX_SHIFT = 20           # region x shift - 0,0 -> 20,0
X_SHIFT = RX_SHIFT * 32 * 16

root = "../bukkit/SERVER-beta-firstworld-anvil1.2.5/New World/region/renamed/"
for filename in os.listdir(root):
    path = root + filename
    
    print filename
    _, new_rx, rz, _ = filename.split(".")
    new_rx = int(new_rx)
    rz = int(rz)
    old_rx = new_rx - RX_SHIFT

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

    for cx, cz in itertools.product(range(32), range(32)):
        chunk = readChunk(cx, cz)
        if chunk is None:
            continue
        print cx,cz,chunk

        # Global
        chunk["Level"]["xPos"].value += X_SHIFT

        # Entities, Pos
        entities = chunk["Level"]["Entities"]
        print entities,len(entities)
        for entity in entities:
            entity["Pos"][0].value += X_SHIFT

        # TileEntities, x
        tes = chunk["Level"]["TileEntities"]
        for te in tes:
            te["x"].value += X_SHIFT

        print cx,cz,chunk


