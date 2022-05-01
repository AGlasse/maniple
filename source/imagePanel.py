#!/usr/bin/python
from tkinter import *
from tkinter import ttk
from valuePanel import ValuePanel
from panel import Panel
from command import Command
from cropCommand import CropCommand
from globals import Globals
import matplotlib as plt

plt.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class ImagePanel(Panel):

    def __init__(self, parent):
        Panel.__init__(self, parent)

        self.command = Command()
        fs = self.IMAGE_SIZE
        f = Figure(figsize=(fs, fs), dpi=100)
        self.image_axes = f.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(f, self)
        self.canvas.draw()
        self.canvas.mpl_connect('button_press_event', self._on_click)
        self.canvas.mpl_connect('motion_notify_event', self._on_move)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=3, columnspan=5)

        IP = ImagePanel
        IP.xmin_control = Slider(self, text='X min', orient=HORIZONTAL,
                                 row=3, column=0, rowspan=2, sticky="new")
        IP.xmax_control = Slider(self, text='X max', orient=HORIZONTAL,
                                 row=3, column=4, rowspan=2, sticky="new")

        IP.ymin_control = Slider(self, text='Y min', orient=VERTICAL,
                                 row=2, column=5, sticky="nsw")
        IP.ymax_control = Slider(self, text='Y max', orient=VERTICAL,
                                 row=0, column=5, sticky="nsw")

        IP.z_scale = Slider(self, text='Z layer', orient=VERTICAL, row=3, column=5, rowspan=2)
        IP.c_scale = Slider(self, text='Cube', orient=VERTICAL, row=3, column=6, rowspan=2)
        IP.b_scale = Slider(self, text='Buffer', orient=VERTICAL,
                            row=3, column=7, rowspan=2,
                            textvals=['A', 'B'], val='A')

        self.make_button(icon_name='im_uncrop', row=3, column=2,
                tt='Restore image to full frame',
                lcom=lambda: self.uncrop())

        crop_command = CropCommand()
        self.make_button(icon_name='im_crop',  row=3, column=3,
                tt='Click to select the crop box ',
                lcom=lambda: self.start_command(crop_command))
        self.crop_command = crop_command

        IP.value_panel = ValuePanel(self)
        IP.value_panel.grid(row=1, column=5, columnspan=2, sticky="nsew")
        return

    def start_command(self, command):
        self.command = command
        self.command.start()

    def on_change(self):
        base = self.get_base()
        base.refresh()
        return

    def uncrop(self):
        self._reset_bounds()
        base = self.get_base()
        base.refresh()
        return

    def croptobox(self, box):
        xa = int(box[0] + 0.5)
        xb = int(box[2] + 0.5)
        (xmin, xmax) = (xa, xb) if xa < xb else (xb, xa)
        self.xmin_control.set_val(xmin)
        self.xmax_control.set_val(xmax)

        ya = int(box[1] + 0.5)
        yb = int(box[3] + 0.5)
        (ymin, ymax) = (ya, yb) if ya < yb else (yb, ya)
        self.ymin_control.set_val(ymin)
        self.ymax_control.set_val(ymax)
        base = self.get_base()
        base.refresh()
        return

    def _toxy(self, event):
        is_valid = False
        x, y, c, r = -1.0, -1.0, -1, -1

        if event.xdata is not None and event.ydata is not None:
            x, y = event.xdata, event.ydata
            c, r = int(x + 0.5), int(y + 0.5)
            xmax = self.xmax_control.get_val()
            ymax = self.ymax_control.get_val()
            if c < xmax and r < ymax:
                is_valid = True
        return is_valid, x, y, c, r

    def _on_move(self, event):
        is_valid, x, y, c, r = self._toxy(event)
        if is_valid:
            val = self.frame[r, c]
            base = self.get_base()
            base.phot_panel.set_hover(x, y, val)
            self.command.process_move(x, y)
        self.refresh()
        return

    def _on_click(self, event):
        is_cancelled = event.button == 3
        is_done = False
        if not is_cancelled:
            is_valid, xc, yc, c, r = self._toxy(event)
            if is_valid:
                is_done = self.command.process_click(event, xc, yc, self)
        if is_done or is_cancelled:
            self.command = Command()
            self.refresh()
        return

    def _reset_bounds(self):
        """ Restore image display bounds to include all pixels. """
        buffer_id = ImagePanel.b_scale.get_val()
        print('iP._rb - Resetting display for buffer ' + buffer_id)
        buffer = Globals.get_buffer(buffer_id)
        cmax, zmax, ymax, xmax = buffer.get_bounds()
        IP = ImagePanel
        IP.xmin_control.set_bounds(xmax-1, 0)
        IP.xmin_control.set_val(0)
        IP.xmax_control.set_bounds(xmax-1, 0)
        IP.xmax_control.set_val(xmax-1)
        IP.ymin_control.set_bounds(0, ymax-1)
        IP.ymin_control.set_val(0)
        IP.ymax_control.set_bounds(0, ymax-1)
        IP.ymax_control.set_val(ymax-1)
        return buffer, cmax, zmax

    def reset(self, _=None):
        buffer, cmax, zmax = self._reset_bounds()
        IP = ImagePanel
        IP.c_scale.set_bounds(0, cmax - 1)
        IP.c_scale.set_val(0)
        IP.z_scale.set_bounds(0, zmax - 1)
        IP.z_scale.set_val(0)
        frame = buffer.get_frame(0, 0)
        vmin = np.nanmin(frame)
        vmax = np.nanmax(frame)
        IP.value_panel.setplotlimits(vmin, vmax)
        vmin = np.nanmin(frame)
        vmax = np.nanmax(frame)
        IP.value_panel.setlimits(vmin, vmax)
        self.frame = frame
        return

    def refresh(self):
        buffer_name = self.b_scale.get_val()
        buffer = Globals.get_buffer(buffer_name)
        cube = int(self.c_scale.get_val())
        zslice = int(self.z_scale.get_val())
        self.frame = buffer.get_frame(cube, zslice)

        xmin = self.xmin_control.get_val()
        xmax = self.xmax_control.get_val()
        ymin = self.ymin_control.get_val()
        ymax = self.ymax_control.get_val()

        vpmin, vpmax = self.value_panel.getplotlimits()

        self.image = self.frame[ymin:ymax+1, xmin:xmax+1]

        vmin = np.nanmin(self.image)
        vmax = np.nanmax(self.image)
        self.value_panel.setlimits(vmin, vmax)


        axes = self.image_axes
        axes.clear()            # Clear or else you get artifacts when resizing
        axes.set_xlim(xmin-1, xmax+1)
        axes.set_ylim(ymin-1, ymax+1)
        axes.set_aspect('equal', 'box')
        axes.imshow(self.image,
              extent=(xmin-0.5, xmax+0.5, ymin-0.5, ymax+0.5),
              interpolation='nearest', cmap='inferno',  #'binary',
              vmin=vpmin, vmax=vpmax, origin='lower')
        self.command.plot(axes)
        self.canvas.draw()
        return


class Slider(Panel):

    def __init__(self, parent, **kwargs):
        Panel.__init__(self, parent)
        self.parent = parent
        text = kwargs.get('text', 'slider')
        textvals = kwargs.get('textvals', None)
        if textvals == None:
            minval = kwargs.get('minval', 0)
            maxval = kwargs.get('maxval', 1)
        else:
            minval = 0
            maxval = len(textvals) - 1
        self.textvals = textvals
        self.value = kwargs.get('val', 0)
        self.loText = StringVar()
        self.hiText = StringVar()
        self.val_text = StringVar(parent, self.value)
        row = kwargs.get('row', 0)
        column = kwargs.get('column', 0)
        sticky = kwargs.get('sticky', 'nw')
        self.grid(row=row, column=column, sticky=sticky)
        orient = kwargs.get('orient', HORIZONTAL)

        self.make_label(textvariable=self.loText, width=10, row=3, column=0)
        self.make_label(textvariable=self.hiText, width=10, row=0, column=0)
        val_entry = self.make_entry(textvariable=self.val_text, row=1, column=0)
        val_entry.bind("<Return>", self._on_entry_changed)

        self.make_label(text=text, row=4, column=0)
        self.scale = ttk.Scale(self, orient=orient, command=self._on_slider_changed)
        self.scale.grid(row=2, column=0)
        self.set_bounds(minval, maxval)
        return

    def get_val(self):
        val = int(self.scale.get())
        if self.textvals != None:
            val = self.textvals[val]
        return val

    def set_val(self, val):
        self.val_text.set('{:3d}'.format(val))
        self.scale.set(val)
        return

    def set_bounds(self, minval, maxval):
        self.scale.configure(from_=maxval, to=minval)
        if self.textvals == None:
            self.loText.set('{:6d}'.format(minval))
            self.hiText.set('{:6d}'.format(maxval))
        else:
            self.loText.set("{:6s}".format(self.textvals[0]))
            self.hiText.set("{:6s}".format(self.textvals[-1]))
        return

    def get_bounds(self):
        lo = int(self.loText.get())
        hi = int(self.hiText.get())
        return lo, hi

    def _on_slider_changed(self, event):
        val = int(float(event))
        if self.textvals == None:
            self.val_text.set('{:3d}'.format(val))
        else:
            self.val_text.set("{:3s}".format(self.textvals[val]))
        base = self.get_base()
        base.refresh()
        return

    def _on_entry_changed(self, event):
        val = int(float(self.val_text.get()))
        if self.textvals == None:
            self.scale.set(val)
        else:
            self.scale,set(self.textvals[val])
        base = self.get_base()
        base.refresh()
        return
