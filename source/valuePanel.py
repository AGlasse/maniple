from tkinter import *
from panel import Panel


class ValuePanel(Panel):

    def __init__(self, parent):
        Panel.__init__(self, parent)

        vmax_label = self.make_label(tt='Maximum pixel value', row=0, column=0)
        self.vmax = StringVar()
        vmax_label.config(textvariable=self.vmax)
        vmax_plot_entry = self.make_entry(val=100.0, fmt='{:10.3e}',
                                          width=9, row=1, tt='Maximum plotted value')
        vmax_plot_entry.bind("<Return>", self._on_change)
        self.vmax_plot_entry = vmax_plot_entry

        v100_button = self.make_button(icon_name='im_plot100', row=2,
                                       tt='Set plot range to min/max')
        v100_button.config(command=lambda: self._clip(0.0))

        v099_button = self.make_button(icon_name='im_plot99', row=3,
                                       tt='Plot 0.5 - 99.5 %')
        v099_button.config(command=lambda: self._clip(0.5))

        v095_button = self.make_button(icon_name='im_plot95', row=4,
                                       tt='Plot 2.5 - 97.5 %')
        v095_button.config(command=lambda: self._clip(2.5))

        vmin_plot_entry = self.make_entry(val=0.0, fmt='{:10.3e}',
                                          width=9, row=5, tt='Minimum plotted value')
        vmin_plot_entry.bind("<Return>", self._on_change)
        self.vmin_plot_entry = vmin_plot_entry

        self.vmin = StringVar()
        self.setlimits(0.0, 1.0)
        self.make_label(textvariable=self.vmin, row=6, tt='Minimum pixel value')
        return

    def setlimits(self, vmin, vmax):
        fmt = '{:10.3e}'
        self.vmin.set(fmt.format(vmin))
        self.vmax.set(fmt.format(vmax))
        return

    def getlimits(self):
        vmin = float(self.vmin_entry.get())
        vmax = float(self.vmax_entry.get())
        return vmin, vmax

    def setplotlimits(self, vmin, vmax):
        fmt = '{:10.3e}'
        self.vmin_plot_entry.delete(0, END)
        self.vmin_plot_entry.insert(0, fmt.format(vmin))
        self.vmax_plot_entry.delete(0, END)
        self.vmax_plot_entry.insert(0, fmt.format(vmax))
        return

    def getplotlimits(self):
        vpmin = float(self.vmin_plot_entry.get())
        vpmax = float(self.vmax_plot_entry.get())
        return vpmin, vpmax

    def _clip(self, clip):
        """ Set plot values to include fraction of pixel values
        """
        import numpy as np

        image = self.parent.image
        clip_lo = clip / 2.0
        clip_hi = 100.0 - clip / 2.0
        vpmin = np.nanpercentile(image, clip_lo)
        vpmax = np.nanpercentile(image, clip_hi)
        self.setplotlimits(vpmin, vpmax)
        base = self.get_base()
        base.refresh()

    def _on_change(self, event):
        base = self.get_base()
        base.refresh()
        return
