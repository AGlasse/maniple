#!/usr/bin/python
# from tkinter import *
from tkinter import ttk, StringVar, HORIZONTAL
from panel import Panel


class Slider(Panel):

    def __init__(self, parent, **kwargs):
        Panel.__init__(self, parent)
        self.parent = parent
        text = kwargs.get('text', 'slider')
        textvals = kwargs.get('textvals', None)
        if textvals is None:
            minval = kwargs.get('minval', 0)
            maxval = kwargs.get('maxval', 1)
        else:
            minval = 0
            maxval = len(textvals) - 1
        self.textvals = textvals
        self.value = kwargs.get('val', 0)
        self.lo_text = StringVar()
        self.hi_text = StringVar()
        self.val_text = StringVar()
        row = kwargs.get('row', 0)
        column = kwargs.get('column', 0)
        sticky = kwargs.get('sticky', 'nw')
        self.grid(row=row, column=column, sticky=sticky)
        orient = kwargs.get('orient', HORIZONTAL)

        rows, cols, span = [0, 1, 2, 3], [0, 0, 0, 0], 1
        if orient == HORIZONTAL:
            rows, cols, span = [0, 0, 1, 0], [0, 1, 1, 3], 3

        self.make_label(textvariable=self.hi_text, width=5, row=rows[0], column=cols[0])
        val_entry = self.make_entry(textvariable=self.val_text, row=rows[1], column=cols[1])
        val_entry.bind("<Return>", self._on_entry_changed)
        self.scale = ttk.Scale(self, orient=orient, command=self._on_slider_changed)
        self.scale.grid(row=rows[2], column=cols[2], columnspan=span)
        self.make_label(textvariable=self.lo_text, width=5, row=rows[3], column=cols[3])

        self.set_bounds(minval, maxval)
        self.set_val(0)
        return

    def set_bounds(self, minval, maxval):
        self.scale.configure(from_=maxval, to=minval)
        if self.textvals is None:
            self.lo_text.set('{:6d}'.format(minval))
            self.hi_text.set('{:6d}'.format(maxval))
        else:
            self.lo_text.set("{:s}".format(self.textvals[0]))
            self.hi_text.set("{:s}".format(self.textvals[-1]))
        return

    def get_bounds(self):
        lo = int(self.lo_text.get())
        hi = int(self.hi_text.get())
        return lo, hi

    def _on_slider_changed(self, event):
        """ Update the text box in response to a slider change. """
        val = int(float(event))
        val_string = "{:3d}".format(val) if self.textvals is None else "{:3s}".format(self.textvals[val])
        self.val_text.set(val_string)
        base = self.get_base()
        base.refresh()
        return

    def _on_entry_changed(self, _):
        """ Update the scale object in response to a new typed text box value. """
        val = int(float(self.val_text.get()))
        if self.textvals is None:
            self.scale.set(val)
        else:
            self.scale.set(self.textvals[val])
        base = self.get_base()
        base.refresh()
        return

    def set_val(self, val):
        """ Update the slider object and the text box with a new value. """
        self.val_text.set('{:3d}'.format(val))
        self.scale.set(val)
        return

    def get_val(self):
        val = int(self.scale.get())
        if self.textvals is not None:
            val = self.textvals[val]
        return val
