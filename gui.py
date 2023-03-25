from math import ceil
from tkinter import *
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from os import walk, path
from PIL import Image, ImageTk
import json
from checkBlacklist import isNotBlacklisted

textures = sorted(next(walk('filtered'), (None, None, []))[2])
window = tk.Tk()


horizontalItems = 10
verticalItems = ceil(len(textures) / horizontalItems)

blocks = []
blockTextureNameToId = {}

with open("textureNameToId.json", "r") as inFile:
    oldJson = json.loads(inFile.read())

    for textureName in oldJson:
        if (isNotBlacklisted(textureName)):
            blockTextureNameToId[textureName] = oldJson[textureName]


class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    """

    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = tk.Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)


class Block:
    def __init__(self, root, imagePath, x, y):
        displayText = imagePath

        try:
            displayText = blockTextureNameToId[imagePath]
        except:
            pass

        if displayText[-4:] == ".png":
            displayText = displayText[:-4]

        self.textureName = imagePath
        self.index = y * horizontalItems + x

        if (self.index >= len(textures)):
            self.index = -1

        self.frame = tk.Frame(root)
        self.frame.grid(column=x, row=y, sticky="news")
        self.image = ImageTk.PhotoImage(Image.open(
            path.join('filtered', imagePath)).resize((32, 32), Image.Resampling.NEAREST))

        self.imageLabel = tk.Label(self.frame, image=self.image)
        self.imageLabel.grid()
        self.imageLabel.image = self.image

        self.id = StringVar()
        self.entry = tk.Entry(
            self.frame, textvariable=self.id)
        self.entry.grid(column=0, row=1)

        self.id.set(displayText)

        self.id.trace_add('write', self.manageIdChange)
        blockTextureNameToId[self.textureName] = self.id.get()

    def manageIdChange(self, *args):
        blockTextureNameToId[self.textureName] = self.id.get()


def createTextureGenerator():
    for texture in textures:
        yield texture


def saveBlockTextureNameToId():
    with open("textureNameToId.json", 'w') as outFile:
        outFile.write(json.dumps(blockTextureNameToId))


scrollableFrame = ScrolledText(window, state='disable')
scrollableFrame.pack(fill='both', expand=True)

mainFrame = tk.Frame(scrollableFrame, width=300)
mainFrame.columnconfigure(tuple(range(10)), weight=1)
mainFrame.grid()

scrollableFrame.window_create('1.0', window=mainFrame)

window.columnconfigure(1, weight=1)
window.rowconfigure(1, weight=1)

textureGenerator = createTextureGenerator()

for y in range(verticalItems):
    for x in range(horizontalItems):
        if ((y * horizontalItems) + x >= len(textures)):
            break
        blocks.append(Block(mainFrame, next(textureGenerator), x, y))

window.bind("<Return>", lambda e: saveBlockTextureNameToId())

window.mainloop()
