#!/usr/bin/python
from mathsPanel import MathsPanel
from ioPanel import IoPanel
from imagePanel import ImagePanel
from plotPanel import PlotPanel
import tkinter as tk
from source.command.photCommand import PhotCommand
from photPanel import PhotPanel


class Base(tk.Tk):

    image_panel = None

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        io_panel = IoPanel(self)
        maths_panel = MathsPanel(self)
        image_panel = ImagePanel(self)
        phot_panel = PhotPanel(self, image_panel)
        plot_panel = PlotPanel(self)

        image_panel.grid(row=0, column=0, rowspan=4, sticky="nsew")
        io_panel.grid(row=0, column=1, sticky="nwe")
        maths_panel.grid(row=1, column=1, sticky="nwe")
        phot_panel.grid(row=2, column=1, sticky="nswe")
        plot_panel.grid(row=3, column=1, sticky="nw")

        self.image_panel = image_panel
        self.plot_panel = plot_panel
        self.phot_panel = phot_panel

        self.reset()
        self.refresh()
        return

    def refresh(self):
        """ Refresh displayed image
        """
        if self.image_panel is not None:
            self.image_panel.refresh()
            self.plot_panel.refresh()
        return

    def reset(self):
        """ Reset displayed image to show buffer A object
        """
        self.image_panel.reset()
        return

    def get_vlimits(self):
        vmin, vmax = self.image_panel.value_panel.getplotlimits()
        return vmin, vmax

    def get_image(self):
        return self.image_panel.image
