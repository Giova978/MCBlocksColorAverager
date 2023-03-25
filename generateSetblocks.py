import json
from math import ceil
import re


commandBase = "execute as @s run setblock ~%d ~%d ~%d minecraft:%s"

textureNameToId = {}
commands = []

with open("textureNameToId.json", "r") as inFile:
    textureNameToId = json.loads(inFile.read())

horizontalSpan = 10
verticalSpan = ceil(len(textureNameToId) / 10)

xOffset = 0
yOffset = 0
zDepth = 10


def id():
    for id in textureNameToId.values():
        yield id


idGenerator = id()

result = re.split("~", "ancient_debris~side")

for y in range(verticalSpan):
    for x in range(horizontalSpan):
        if ((y * horizontalSpan) + x >= len(textureNameToId)):
            break

        id = next(idGenerator)

        result = re.split("~", id)

        commands.append(commandBase %
                        (x+xOffset, y+yOffset, zDepth, result[0]))

with open("commands.txt", "w") as outFile:
    outFile.write("\n".join(commands))
