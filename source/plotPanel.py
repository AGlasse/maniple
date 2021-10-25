from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from panel import Panel
from globals import Globals
from imagePanel import ImagePanel

class PlotPanel(Panel):

    modes = [('histogram', 'h'), ('row', 'r'), ('column', 'c'), ('Pixel Select', 'p')]
    entries = [('Enter constant'), ('Enter Row number'), ('Enter column number')]
    mode_buttons = []
    mode_setting = 'h'

    def __init__(self, maniple):
        Panel.__init__(self, maniple)
        self.maniple = maniple
        r = 0
        f = Figure(figsize=(self.IMAGE_SIZE, int(self.IMAGE_SIZE/3)), dpi=100)
        self.plotAxes = f.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(f, self)
        self.canvas.get_tk_widget().grid(row=r, column=0, columnspan=2)

        self.mode_control = StringVar()
        self.mode_control.set('h')
        for text, mode in self.modes:
            button = self.make_button(text=text, tt=text)        #, value=mode)
            r += 1
            button.grid(row=r, column=0, sticky=E)
            button.configure(command=lambda m=mode: self.select_mode(m))
            self.mode_buttons.append(button)

        self.con_entry = self.make_entry(val=0.0, fmt='{:5.1f}',tt='Enter Constant')
        self.con_entry.grid(row=1, column=1, sticky=W)
        self.row_entry = self.make_entry(val=0.0, fmt='{:5.1f}',
                                         tt='Enter row number')
        self.row_entry.grid(row=2, column=1, sticky=W)
        self.col_entry = self.make_entry(val=0.0, fmt='{:5.1f}',
                                         tt='Enter column number')
        self.col_entry.grid(row=3, column=1, sticky=W)

    def select_mode(self, mode):
        for b, m in zip(self.mode_buttons, self.modes):
            if m[1] is mode:
                b.state(['pressed']) #not sure how this works
                self.mode_setting = mode
            else:
                b.state(['!pressed'])
        self.refresh()

    def refresh(self, _=None):
        import numpy as np

        image = self.maniple.get_image()
        vmin, vmax = self.maniple.get_vlimits()
        axes = self.plotAxes
        axes.clear()
        if self.mode_setting is 'h':
            vstep = (vmax - vmin) / 200.0
            try:
                bins = np.arange(vmin, vmax, vstep)
            except:
                print('plotPanel.refresh - Histogram error !!')
                bins = [0.0]
            axes.set_xlim(vmin, vmax)
            axes.hist(image.flatten(), bins)
        if self.mode_setting is 'r':
            nx = image.shape[1]
            row = int(float(self.row_entry.get()))
            xr = np.arange(0, nx)
            yr = image[row,:]
            axes.set_xlim(0, nx)
            axes.set_ylim(vmin, vmax)
            axes.plot(xr, yr, color='green')
        if self.mode_setting is 'c':
            nx = image.shape[0]
            column = int(float(self.col_entry.get()))
            xc = np.arange(0, nx)
            yc = image[:,column]
            axes.set_xlim(0, nx)
            axes.set_ylim(vmin, vmax)
            axes.plot(xc, yc, color='red')
        if self.mode_setting is 'p':
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
