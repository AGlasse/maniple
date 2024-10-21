from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from panel import Panel
from globals import Globals


class PlotPanel(Panel):

    mode_dict = {'histogram': 'Plot histogram',
                 'xyprofile': 'Plot profiles through row/column',
                 'zprofile': 'Plot pixel z profile'}
    selected_button = None

    def __init__(self, maniple):
        Panel.__init__(self, maniple)
        self.maniple = maniple
        f = Figure(figsize=(self.fig_size, int(self.fig_size/3)), dpi=100)
        self.plotAxes = f.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(f, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=3)

        row = 0
        mode_dict = self.mode_dict
        for key in mode_dict:
            tt = mode_dict[key]
            button = self.make_button(text=key, tt=tt)
            row += 1
            button.grid(row=row, column=2, sticky=E)
            button.configure(command=lambda b=button: self.button_callback(b))

        self.nbins_entry = self.make_entry(val=20.0, fmt='{:5.1f}',
                                           tt='Enter no. of histogram bins')
        self.nbins_entry.grid(row=1, column=0, sticky=W)
        self.col_entry = self.make_entry(val=0.0, fmt='{:5.1f}',
                                         tt='Enter column number')
        self.col_entry.grid(row=2, column=0, sticky=W)
        self.row_entry = self.make_entry(val=0.0, fmt='{:5.1f}',
                                         tt='Enter row number')
        self.row_entry.grid(row=2, column=1, sticky=W)
        return

    def button_callback(self, button):
        self.selected_button = button
        self.refresh()
        return

    def refresh(self):
        import numpy as np

        button = self.selected_button
        image = self.maniple.get_image()
        vmin, vmax = self.maniple.get_vlimits()
        if button is None:
            self.canvas.draw()
            return
        txt = button.cget('text')
        axes = self.plotAxes
        axes.clear()
        if txt == 'histogram':
            try:
                nbins = float(self.nbins_entry.get())
                vstep = (vmax - vmin) / nbins
                bins = np.arange(vmin, vmax, vstep)
            except Exception as e:
                print(e)
                bins = [0.0]
            axes.set_xlim(vmin, vmax)
            axes.hist(image.flatten(), bins)
        if txt == 'xyprofile':
            nr, nc = image.shape
            nrc = nr if nr > nc else nc
            column = int(float(self.col_entry.get()))
            row = int(float(self.row_entry.get()))
            xr = np.arange(0, nr)
            yc = image[row, :]
            xc = np.arange(0, nc)
            yr = image[:, column]
            axes.set_xlim(0, nrc)
            axes.set_ylim(vmin, vmax)
            axes.plot(xr, yr, color='green', ls='dashed')
            axes.plot(xc, yc, color='red')
        if txt == 'zprofile':
            block = Globals.buffers['A'].block
            nx = block.shape[1]
            row = int(float(self.row_entry.get()))
            column = int(float(self.col_entry.get()))
            xp = np.arange(0, nx)
            yp = block[0,:,column,row]
            axes.set_xlim(0, nx)
            axes.set_ylim(vmin, vmax)
            axes.plot(xp, yp, color='red')
        self.canvas.draw()
