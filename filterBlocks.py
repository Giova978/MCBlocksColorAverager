from PIL import Image
from os import walk, path, mkdir, remove
from shutil import copyfile, rmtree
import re
import json
from checkBlacklist import isNotBlacklisted
from math import floor, ceil


def addHexZero(hex):
    return '0'+hex if len(hex) < 2 else hex


def doesntHasTransparency(filename):
    image = Image.open(f'block/{filename}').convert("RGBA")
    hasTransparency = False
    for color in image.getcolors(image.size[0]*image.size[1]):
        if (color[1][3] == 0):
            hasTransparency = True
            break

    image.close()
    return not hasTransparency


def colorToHex(color):
    colorStringFormatted = '#'
    for value in color:
        colorStringFormatted += addHexZero(f'{value:x}')
    return colorStringFormatted


def average_image_color(image):
    h = image.histogram()

    # split into red, green, blue
    r = h[0:256]
    g = h[256:256*2]
    b = h[256*2: 256*3]

    # perform the weighted average of each channel:
    # the *index* is the channel value, and the *value* is its weight
    avgR = round(sum(i*w for i, w in enumerate(r)) /
                 sum(r)) if sum(r) > 0 else 0
    avgG = round(sum(i*w for i, w in enumerate(g)) /
                 sum(g)) if sum(g) > 0 else 0
    avgB = round(sum(i*w for i, w in enumerate(b)) /
                 sum(b)) if sum(b) > 0 else 0

    return rbg2Lab((avgR, avgG, avgB))

# Creates a dictonary of block and its color average


def mapBlocksToAvgColor(filenames):
    blockToAvgColor = {}
    for filename in filenames:
        image = Image.open(f'filtered/{filename}').convert("RGBA")
        blockToAvgColor.update({filename: average_image_color(image)})
        image.close()

    return blockToAvgColor

# Creates a spritesheet an its corresponding indexes


def mapBlocksToSpritePos(filenames, res=16):
    spritePos = {}
    counterX = 0
    counterY = 0

    imagesInWidth = floor(600 // res)
    spriteImage = Image.new(
        size=(600, ceil(len(filenames) / imagesInWidth) * res), mode="RGBA")

    for filename in filenames:
        with Image.open(f'filtered/{filename}') as sourceImage:
            image = sourceImage

            if (res != 16):
                image = sourceImage.resize(
                    (res, res), Image.Resampling.NEAREST)

            if (counterX * res + image.size[0] >= 600):
                counterY += 1
                counterX = 0

            x = counterX * res
            y = counterY * res

            spritePos.update(
                {filename: [x, y, image.size[0], image.size[1]]})

            spriteImage.paste(image, (x, y))
            counterX += 1

    return (spriteImage, spritePos)

# OLD Divides long images into 16x16 squares
# Gets the first 16x16 texture from long textures


def divideLargerImage(filename, image):
    divisions = round(image.size[1] / 16)
    lastPieceHeight = 16 if image.size[1] % 16 < 1 else image.size[1] % 16

    # for division in range(divisions):
    division = 0
    newImage = Image.new(size=(16, 16), mode="RGBA")

    if (division == divisions-1):
        subImage = image.crop(
            (0, 16*division, 16, lastPieceHeight + image.size[1]))
    else:
        subImage = image.crop((0, 16*division, 16, 16*(division+1)))

    newImage.paste(subImage, (0, 0))
    newImage.save(f'./filtered/{filename[0:-4]}_{division}.png')

    remove(f'filtered/{filename}')


def prepareImages():
    blockFilenames = next(walk('block'), (None, None, []))[2]
    notBlacklisted = filter(isNotBlacklisted, blockFilenames)
    arePNGs = filter(lambda x: x.endswith('.png'), notBlacklisted)
    isNotTransparent = filter(doesntHasTransparency, arePNGs)
    finalList = sorted(list(isNotTransparent))

    if (path.exists('./filtered')):
        rmtree('./filtered')

    mkdir('./filtered')

    for filename in finalList:
        copyfile(f'block/{filename}', f'filtered/{filename}')

    newFileList = next(walk('filtered'), (None, None, []))[2]
    for filename in newFileList:
        with Image.open(f'filtered/{filename}') as image:
            if (image.size[1] > 16):
                divideLargerImage(filename, image)


def matchTextureToId(filenames):
    gameIdToTextureFilename = {}
    with open('blocks.json')as blocksText:
        blocks = json.loads(blocksText.read())
        possibleTextures = list(mapBlocksToAvgColor(filenames).keys())
        for block in enumerate(blocks):
            blockName = block[1]['name']

            if (not isNotBlacklisted(blockName)):
                continue

            match = []

            for texture in possibleTextures:
                if re.match(blockName, texture):
                    match.append(texture)
                    # possibleTextures.remove(texture)
                    # print(f'Match: {blockName} -> {texture}')

            if (match == ''):
                match = 'None Found'

            if (not blockName in gameIdToTextureFilename):
                gameIdToTextureFilename[blockName] = []

            gameIdToTextureFilename[blockName].append(match)

        with open('gameIdToTextureFilename.json', 'w') as outFile:
            outFile.write(json.dumps(gameIdToTextureFilename))


def rbg2Lab(color):
    r = color[0] / 255
    g = color[1] / 255
    b = color[2] / 255

    r = pow((r + 0.055) / 1.055, 2.4) if r > 0.04045 else r / 12.92
    g = pow((g + 0.055) / 1.055, 2.4) if g > 0.04045 else g / 12.92
    b = pow((b + 0.055) / 1.055, 2.4) if b > 0.04045 else b / 12.92

    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047
    y = (r * 0.2126 + g * 0.7152 + b * 0.0722) / 1.0
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883

    x = pow(x, 1 / 3) if x > 0.008856 else 7.787 * x + 16 / 116
    y = pow(y, 1 / 3) if y > 0.008856 else 7.787 * y + 16 / 116
    z = pow(z, 1 / 3) if z > 0.008856 else 7.787 * z + 16 / 116

    return (116 * y - 16, 500 * (x - y), 200 * (y - z))


prepareImages()
outDir = "out"
if (path.exists(outDir)):
    rmtree(outDir)

mkdir(outDir)
sortedFilenames = sorted(next(walk('filtered'), (None, None, []))[2])
# matchTextureToId(sortedFilenames)

(sprite, pos) = mapBlocksToSpritePos(sortedFilenames, 16)
avgColors = mapBlocksToAvgColor(sortedFilenames)
sprite.save(path.join(outDir, "spritemap.png"))

(sprite64, pos64) = mapBlocksToSpritePos(sortedFilenames, 64)
sprite64.save(path.join(outDir, "spritemap64.png"))

with open(path.join(outDir, 'blockPositions64.json'), 'w') as outFile:
    outFile.write(json.dumps(pos64))

with open(path.join(outDir, 'blockPositions.json'), 'w') as outFile:
    outFile.write(json.dumps(pos))

with open(path.join(outDir, 'avgColorPerBlock.json'), 'w') as outFile:
    outFile.write(json.dumps(avgColors))
