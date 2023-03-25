# Sorter and averager for minecraft texturs

[filterBlocks](filterBlocks.py) is the main script who is in charge of filtering, sorting and generating the spritemaps, json files with positions and average color for the textures

[checkBlacklist](checkBlacklist.py) is a helper function used in [gui](gui.py) and [filterBlocks](filterBlocks.py) for the filtering of blocks

[gui](gui.py) is used to manually update the blocks name for generating setblock commands

## Block name structure

The produced texture's ids are in the following format: `block name`*~*`state`