# shiftmca.py - shift Minecraft region files (.mca) by a fixed number of regions

# Useful to combine multiple worlds into one world, with a region-level granularity
# You can't simply rename the r.#.#.mca files, because they contain embedded location
# information (which will cause "relocating" errors). This script fixes that.

# To use:
# 1. rename each r.<x>.<z>.mca adding 20 (or whatever needed to avoid overlap) to each <x>
# 2. edit the variables below appropriately to match your setup
# 3. run this script
# 4. copy the new outputted .mca files to your second world you want to merge into
#  (no files should be overwritten if shifted by the correct amount)
# 5. load the world and teleport to 10240,0,0; it should load without errors

# You now have a single unified merged world.

# Requires pymclevel - https://github.com/mcedit/pymclevel

from cStringIO import StringIO
import gzip
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

# amount to shift X - must be a whole number of regions
RX_SHIFT = 20               # region x coordinate eshift - 0,0 -> 20,0
CX_SHIFT = RX_SHIFT * 32    # chunk x coordinate
X_SHIFT = CX_SHIFT * 16     # world x coordinate
# TODO: option to shift Z

# pre-renamed region files (r.0.0.mca renamed to r.20.0.mca) (TODO: rename in this script)
root = "../bukkit/SERVER-beta-firstworld-anvil1.2.5/New World/region/renamed/"
# output directory
outroot = root + "../shifted/"

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

    VERSION_GZIP = 1
    VERSION_DEFLATE = 2

    def readChunk(cx, cz):
        rawData = readChunkRaw(cx, cz)
        if rawData is None:
            #print "No chunk ",cx,cz
            return None
        length = struct.unpack_from(">I", rawData)[0]
        compressionFormat = struct.unpack_from("B", rawData, 4)[0]
        compressedData = rawData[5:length + 5]
        if compressionFormat == VERSION_GZIP:
            tag = pymclevel.nbt.load(buf=pymclevel.nbt.gunzip(compressedData))
        elif compressionFormat == VERSION_DEFLATE:
            tag = pymclevel.nbt.load(buf=zlib.decompress(compressedData))
        else:
            raise Exception("Unrecognized compression format: "+compressionFormat)

        return tag

    newChunks = []

    currentSector = 2

    for cx, cz in itertools.product(range(32), range(32)):
        chunk = readChunk(cx, cz)
        if chunk is None:
            continue

        # Shift

        # Global
        chunk["Level"]["xPos"].value += CX_SHIFT

        # Entities, Pos
        entities = chunk["Level"]["Entities"]
        for entity in entities:
            entity["Pos"][0].value += X_SHIFT
            try:
                entity["TileX"].value += X_SHIFT    # paintings
            except Exception:
                pass
            print entity

        # TileEntities, x
        tes = chunk["Level"]["TileEntities"]
        for te in tes:
            te["x"].value += X_SHIFT


        # Save

        buf = StringIO()
        chunk.save(buf=gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=2))
        data = buf.getvalue()

        length = len(data)
        header = struct.pack(">I", length)
        header += struct.pack("B", VERSION_GZIP)
        data = header + data

        #print cx,cz,chunk
        CHUNK_HEADER_SIZE = 5
        sectorsNeeded = (len(data) + CHUNK_HEADER_SIZE) / SECTOR_BYTES + 1

        bytesNeeded = sectorsNeeded * SECTOR_BYTES
        excess = bytesNeeded - len(data)
        data += "\0" * excess

        offsets[cx + cz * 32] = currentSector << 8 | sectorsNeeded
        currentSector += sectorsNeeded

        newChunks.append(data)

    of = file(outroot + filename, "wb")
    of.write(offsets.tostring())
    of.write(modtimes.tostring())
    for chunkData in newChunks:
        of.write(chunkData)

    of.close()

        
