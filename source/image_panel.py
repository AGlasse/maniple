#!/usr/bin/python
import time
from tkinter import *
from valuePanel import ValuePanel
from panel import Panel
from source.command.crop_command import CropCommand
from globals import Globals
import matplotlib as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backend_bases import MouseButton
from slider import Slider
import numpy as np

plt.use("TkAgg")


class ImagePanel(Panel):

    xmin_control, xmax_control, ymin_control, ymax_control = None, None, None, None
    active_command = None
    frame, image, value_panel = None, None, None
    b_scale, c_scale, z_scale = None, None, None

    def __init__(self, parent):
        Panel.__init__(self, parent)

        fs = self.fig_size
        f = Figure(figsize=(fs, fs), dpi=100)
        self.imax = f.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(f, self)
        self.canvas.mpl_connect('button_press_event', self._mouse_button_pressed)
        self.canvas.mpl_connect('button_release_event', self._mouse_button_released)
        self.canvas.mpl_connect('motion_notify_event', self._mouse_motion)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=3, columnspan=4)
        self.canvas.draw()

        ip = ImagePanel
        ip.xmin_control = Slider(self, text='X min', orient=HORIZONTAL,
                                 row=3, column=0, sticky="new")
        ip.xmax_control = Slider(self, text='X max', orient=HORIZONTAL,
                                 row=3, column=3, sticky="new")

        ip.ymin_control = Slider(self, text='Y min', orient=VERTICAL,
                                 row=2, column=4, sticky="nsw")
        ip.ymax_control = Slider(self, text='Y max', orient=VERTICAL,
                                 row=0, column=4, sticky="nsw")

        ip.z_scale = Slider(self, text='Z layer', orient=VERTICAL, row=3, column=4)
        ip.c_scale = Slider(self, text='Cube', orient=VERTICAL, row=3, column=5)
        ip.b_scale = Slider(self, text='Buffer', orient=VERTICAL,
                            row=3, column=6, textvals=['A', 'B'])

        self.make_button(icon_name='im_uncrop', row=3, column=2,
                         tt='Restore image to full frame',
                         lcom=lambda: self.uncrop())

        ip.value_panel = ValuePanel(self)
        ip.value_panel.grid(row=1, column=4, columnspan=2, sticky="nsew")
        return

    def start_command(self, command):
        self.active_command = command
        self.active_command.start()
        return

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

    @staticmethod
    def _toxy(event):
        is_valid, x, y, c, r = False, -1.0, -1.0, -1, -1
        if event.xdata is not None and event.ydata is not None:
            x, y = event.xdata, event.ydata
            c, r = int(x + 0.5) - 1, int(y + 0.5) - 1
            is_valid = True
        return is_valid, x, y, c, r

    def _mouse_motion(self, event):
        is_valid, x, y, c, r = ImagePanel._toxy(event)
        if is_valid:                        # Cursor is moving in image panel
            val = self.frame[r, c]          # Update position and value labels in phot_panel
            base = self.get_base()
            base.phot_panel.set_hover(x, y, val)
            if self.active_command is not None:             # Update any active image commands
                self.active_command.mouse_motion(x, y)
            self.refresh()
        return

    def _mouse_button_released(self, event):
        return

    def _mouse_button_pressed(self, event):
        is_cancelled = event.button == MouseButton.RIGHT
        is_done = False
        if not is_cancelled:
            is_valid, xc, yc, c, r = self._toxy(event)
            if is_valid:
                if self.active_command is not None:
                    is_done = self.active_command.mouse_button_pressed(event, xc, yc, self)
                else:
                    if event.key == 'shift':
                        self.active_command = CropCommand()
                        self.active_command.start(xc, yc)
                    else:                    # Update pixel coordinate widgets.
                        base = self.get_base()
                        base.phot_panel.set_cursor(xc, yc)
                        # Globals.cursor_position = xc, yc
        if is_done or is_cancelled:
            self.active_command = None
            self.refresh()
        return

    @staticmethod
    def _reset_bounds():
        """ Restore image display bounds to include all pixels. """
        ip = ImagePanel
        buffer_id = ip.b_scale.get_val()
        Globals.set_display_buffer(buffer_id)
        buffer = Globals.get_display_buffer()
        cmax, zmax, ymax, xmax = buffer.get_bounds()
        ip.xmin_control.set_bounds(xmax-1, 0)
        ip.xmin_control.set_val(0)
        ip.xmax_control.set_bounds(xmax-1, 0)
        ip.xmax_control.set_val(xmax-1)
        ip.ymin_control.set_bounds(0, ymax-1)
        ip.ymin_control.set_val(0)
        ip.ymax_control.set_bounds(0, ymax-1)
        ip.ymax_control.set_val(ymax-1)
        return buffer, cmax, zmax

    def slider_changed(self):
        return

    def reset(self, _=None):
        buffer, cmax, zmax = self._reset_bounds()
        ip = ImagePanel
        ip.c_scale.set_bounds(0, cmax - 1)
        ip.c_scale.set_val(0)
        ip.z_scale.set_bounds(0, zmax - 1)
        ip.z_scale.set_val(0)
        frame = buffer.get_frame(0, 0)
        vmin = np.nanmin(frame)
        vmax = np.nanmax(frame)
        ip.value_panel.setplotlimits(vmin, vmax)
        vmin = np.nanmin(frame)
        vmax = np.nanmax(frame)
        ip.value_panel.setlimits(vmin, vmax)
        self.frame = frame
        return

    def refresh(self):
        ip = ImagePanel
        buffer_name = ip.b_scale.get_val()
        Globals.set_display_buffer(buffer_name)
        buffer = Globals.get_display_buffer()
        cube = int(self.c_scale.get_val())
        zslice = int(self.z_scale.get_val())
        self.frame = buffer.get_frame(cube, zslice)

        xmin = ip.xmin_control.get_val()
        xmax = ip.xmax_control.get_val()
        ymin = self.ymin_control.get_val()
        ymax = self.ymax_control.get_val()
        vpmin, vpmax = ip.value_panel.getplotlimits()

        self.image = self.frame[ymin:ymax+1, xmin:xmax+1]
        ax = self.imax
        ax.clear()            # Clear or else you get artifacts when resizing
        ax.set_xlim(xmin-1, xmax+1)
        ax.set_ylim(ymin-1, ymax+1)
        ax.set_aspect('equal', 'box')
        ax.imshow(self.image, extent=(xmin-0.5, xmax+0.5, ymin-0.5, ymax+0.5),
                  interpolation='nearest', cmap='hot', vmin=vpmin, vmax=vpmax, origin='lower')
        if Globals.cursor_position is not None:
            xc, yc = Globals.cursor_position
            ax.plot(xc, yc, marker='+', color='green')
        if self.active_command is not None:
            self.active_command.plot(ax)
        self.canvas.draw()
        return
