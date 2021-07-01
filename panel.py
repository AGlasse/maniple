#!/usr/bin/python
from tkinter import *
from tkinter import ttk
from icon import Icon
from tooltip import Tooltip
import tkinter as tk


class Panel(ttk.Frame):

    def __init__(self, parent, **kwargs):
        ttk.Frame.__init__(self, parent, borderwidth=10.0)
        self.parent = parent
        screen_width = ttk.Frame.winfo_screenwidth(self)
        idx = int(screen_width / 1000)
        fontsize = [10, 12, 24][idx]
        self.LARGE_FONT = ('Helvetica', fontsize)
        self.ICON_HEIGHT = [15, 20, 50][idx]
        self.IMAGE_SIZE = [8, 8, 18][idx]
        pw = [5, 5, 12][idx]
        ph = [3, 3, 8][idx]
        self.PLOT_SIZE = (pw, ph)
        self.BUTTON_PAD = [1, 1, 3][idx]
        self.width = [4, 5, 12][idx]
        style = ttk.Style()
        style.configure("TFrame", borderwidth=5.0, relief=GROOVE)
        self.row = 0
        self.column = 0
        self.config(**kwargs)

    def get_base(self):
        from base import Base

        parent = self.parent
        is_base = isinstance(parent, Base)
        while not is_base:
            parent = parent.parent
            is_base = isinstance(parent, Tk)
        return parent

    @staticmethod
    def stylename_elements_options(stylename):
        """ Function to expose the options of every element associated to a
            widget stylename.
        :param stylename:
        :return:
        """
        try:
            # Get widget elements
            style = ttk.Style()
            layout = str(style.layout(stylename))
            print('Stylename = {}'.format(stylename))
            print('Layout    = {}'.format(layout))
            elements = []
            for n, x in enumerate(layout):
                if x == '(':
                    element = ""
                    for y in layout[n + 2:]:
                        if y != ',':
                            element = element + str(y)
                        else:
                            elements.append(element[:-1])
                            break
            print('\nElement(s) = {}\n'.format(elements))
            # Get options of widget elements
            for element in elements:
                print('{0:30} options: {1}'.format(
                    element, style.element_options(element)))
        except tk.TclError:
            print('_tkinter.TclError: "{0}" in function'
                  'widget_elements_options({0}) is not a regonised stylename.'
                  .format(stylename))

    def config(self, **kwargs):
        """ Configure common panel parameters
        """
        self.width = kwargs.get('width', self.width)
        self.row = kwargs.get('row', self.row)
        self.column = kwargs.get('column', self.column)
        return

    def make_label(self, **kwargs):
        textvariable = kwargs.get('textvariable', None)
        text = kwargs.get('text', None)
        tt = kwargs.get('tt', 'Tooltip text')
        row = kwargs.get('row', self.row)
        column = kwargs.get('column', self.column)
        font = kwargs.get('font', self.LARGE_FONT)
        minsize = kwargs.get('minsize', 1200)
        label = ttk.Label(self, font=font, style='Man.TLabel', justify=RIGHT)
        if text is not None:
            label.config(text=text)
        if textvariable is not None:
            label.config(textvariable=textvariable)
        label.grid(row=row, column=column)
        label.columnconfigure(1, minsize=minsize)
        Tooltip(label, text=tt, wraplength=200)
        return label

    def make_button(self, **kwargs):
        icon_name = kwargs.get('icon_name', None)
        text = kwargs.get('text', None)
        width = kwargs.get('width', self.width)
        icon_height = kwargs.get('icon_height', self.ICON_HEIGHT)
        row = kwargs.get('row', self.row)
        column = kwargs.get('column', self.column)
        pad = kwargs.get('pad', self.BUTTON_PAD)
        lcom = kwargs.get('lcom', None)
        tt = kwargs.get('tt', 'Tooltip text')

        if icon_name is not None:
            icon = Icon(icon_name, height=icon_height)
            button = ttk.Button(self, image=icon.image, command=lcom)
            button.image = icon.image
        else:
            if text is not None:
                button = ttk.Button(self, text=text, width=width)
            else:
                button = ttk.Button(self, width=width)
        button.grid(row=row, column=column,
                    sticky=W, padx=pad, pady=pad)
        Tooltip(button, text=tt, wraplength=200)
        return button

    def make_entry(self, **kwargs):
        textvariable = kwargs.get('textvariable', None)
        val = kwargs.get('val', 0.0)
        width = kwargs.get('width', self.width)
        fmt = kwargs.get('fmt', '{:f5.1}')
        font = kwargs.get('font', self.LARGE_FONT)
        row = kwargs.get('row', self.row)
        column = kwargs.get('column', self.column)
        pad = kwargs.get('pad', self.BUTTON_PAD)
        tt = kwargs.get('tt', 'Tooltip text')
        entry = ttk.Entry(self, width=width, justify=RIGHT, font=font, style='M.TEntry')
        if textvariable is not None:
            entry.config(textvariable=textvariable)
        else:
            entry.insert(0, fmt.format(val))
            entry.xview(0)
        entry.grid(row=row, column=column, sticky=W, padx=pad, pady=pad)
        Tooltip(entry, text=tt, wraplength=200)
        return entry
