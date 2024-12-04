#!/usr/bin/python
from tkinter import *
from tkinter import ttk
from icon import Icon
from tooltip import Tooltip
import tkinter as tk


class Panel(ttk.Frame):

    # Define variables accessible to all panels.
    x_cursor, y_cursor = None, None             # Cursor position

    def __init__(self, parent, **kwargs):
        Panel.x_cursor = 10
        Panel.y_cursor = 10

        ttk.Frame.__init__(self, parent, borderwidth=10.0)
        self.parent = parent
        screen_width = ttk.Frame.winfo_screenwidth(self)
        idx = int(screen_width / 1000)
        fontsize = [10, 12, 14][idx]
        self.LARGE_FONT = ('Helvetica', fontsize)
        self.ICON_HEIGHT = [15, 20, 20][idx]
        self.fig_size = [6, 6.5, 7][idx]
        pw = [5, 6, 12][idx]
        ph = [3, 4, 8][idx]
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
                  'widget_elements_options({0}) is not a recognised stylename.'
                  .format(stylename))

    def config(self, **kwargs):
        """ Configure common panel parameters
        """
        self.width = kwargs.get('width', self.width)
        self.row = kwargs.get('row', self.row)
        self.column = kwargs.get('column', self.column)
        return

    def make_label(self, **kwargs):
        label = self._make_text_widget(**kwargs)
        return label

    def make_entry(self, **kwargs):
        entry = self._make_text_widget(**kwargs, is_entry=True)
        return entry

    def _make_text_widget(self, **kwargs):
        is_entry = kwargs.get('is_entry', False)
        style = 'Man.TEntry' if is_entry else 'Man.TLabel'
        textvariable = kwargs.get('textvariable', None)
        val = kwargs.get('val', 0.0)
        width = kwargs.get('width', self.width)
        fmt = kwargs.get('fmt', '{:5.1f}')
        font = kwargs.get('font', self.LARGE_FONT)
        row = kwargs.get('row', self.row)
        column = kwargs.get('column', self.column)
        pad = kwargs.get('pad', self.BUTTON_PAD)
        tt = kwargs.get('tt', 'Tooltip text')
        widget = ttk.Entry(self, width=width, justify=RIGHT, font=font, style=style)
        if textvariable is not None:
            widget.config(textvariable=textvariable)
        else:
            widget.insert(0, fmt.format(val))
            widget.xview(0)
        widget.grid(row=row, column=column, sticky=W, padx=pad, pady=pad)
        Tooltip(widget, text=tt, wraplength=200)
        return widget

    def make_button(self, **kwargs):
        is_checkbutton = kwargs.get('is_checkbutton', False)
        intvar = kwargs.get('intvar', 0)
        icon_name = kwargs.get('icon_name', None)
        text = kwargs.get('text', None)
        width = kwargs.get('width', self.width)
        icon_height = kwargs.get('icon_height', self.ICON_HEIGHT)
        row = kwargs.get('row', self.row)
        column = kwargs.get('column', self.column)
        columnspan = kwargs.get('columnspan', 1)
        pad = kwargs.get('pad', self.BUTTON_PAD)
        lcom = kwargs.get('lcom', None)
        tt = kwargs.get('tt', 'Tooltip text')

        if icon_name is not None:
            icon = Icon(icon_name, height=icon_height)
            button = ttk.Button(self, image=icon.image, command=lcom)
            button.image = icon.image
        else:
            if text is not None:
                if is_checkbutton:
                    button = ttk.Checkbutton(self, text=text, variable=intvar)       # , variable=var0, command=cb)
                else:
                    button = ttk.Button(self, text=text, width=width)
            else:
                button = ttk.Button(self, width=width)
        button.grid(row=row, column=column, columnspan=columnspan,
                    sticky=W, padx=pad, pady=pad)
        Tooltip(button, text=tt, wraplength=200)
        return button
