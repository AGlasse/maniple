#!/usr/bin/python
from PIL import Image, ImageTk
from globals import Globals


class Icon:
    """ Load an image which can be used as a tkinter button icon.
    Note - it would be better to inherit Icon from PhotoImage..
    The image can be resized using width and height parameters.

    name - Name of bitmap file containing base image
    kwargs
    width - Width of output image [pixels]
    height - Height of output image [pixels]
    """
    image = ImageTk.PhotoImage

    def __init__(self, name, **kwargs):
        width = kwargs.get('width', -1)
        height = kwargs.get('height', -1)
        exd = Globals.execution_directory
        icon_folder = exd + '\\..\\Icons'
        iconfile = icon_folder + '\\' + name + '.png'
        img = Image.open(iconfile)
        if width > 0:
            wpercent = (width / float(img.size[0]))
            h = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((width, h), Image.ANTIALIAS)
        if height > 0:
            hpercent = (height / float(img.size[1]))
            w = int((float(img.size[0]) * float(hpercent)))
            img = img.resize((w, height), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(img)
