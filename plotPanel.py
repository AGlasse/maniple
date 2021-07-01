from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from panel import Panel


class PlotPanel(Panel):

    modes = [('histogram', 'h'), ('row', 'r'), ('column', 'c')]
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
            button = self.make_button(text=text, tt='Henry' + text)        #, value=mode)
            r += 1
            button.grid(row=r, column=0, sticky=E)
            button.configure(command=lambda m=mode: self.select_mode(m))
            self.mode_buttons.append(button)
        self.con_entry = self.make_entry(val=0.0, fmt='{:5.1f}',
                                         tt='Enter constant')
        self.con_entry.grid(row=1, column=1, sticky=W)

    def select_mode(self, mode):
        for b, m in zip(self.mode_buttons, self.modes):
            if m[1] is mode:
                b.state(['pressed'])
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
            row = 10
            xb = np.arange(0, nx)
            yb = image[:, row]
            axes.set_xlim(0, nx)
            axes.set_ylim(vmin, vmax)
            axes.plot(xb, yb, color='green')
        self.canvas.draw()
