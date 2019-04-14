# shiftmca

Shift Minecraft region files (.mca) by a fixed number of regions

Useful to combine multiple worlds into one world, with a region-level granularity
You can't simply rename the `r.#.#.mca` files, because they contain embedded location
information (which will cause "relocating" errors). This script fixes that.

Requires pymclevel - install from https://github.com/mcedit/pymclevel

To use:

1. Rename each `r.<x>.<z>.mca` adding 20 (or whatever needed to avoid overlap) to each `<x>`

Example:

```
mkdir renamed-renamed
ls region-converted/*.mca|perl -pe'chomp;m/r\.([-\d]+)\.([-\d]+)\.mca/;$b="r.@{[ $1 - 50 ]}.$2.mca";$_="cp $_ region-renamed/$b\n"'
```

2. Edit the variables in the script appropriately to match your setup

3. Run the script: `python shiftmca.py`

4. Copy the new outputted .mca files to your second world you want to merge into (no files should be overwritten if shifted by the correct amount)

5. Load the world and teleport to 10240,0,0; it should load without errors

You now have a single unified merged world.

