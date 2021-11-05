from panel import Panel
from tkinter import StringVar
from photCommand import PhotCommand


class PhotPanel(Panel):

    def __init__(self, parent, image_panel):
        Panel.__init__(self, parent)

        self.config(row=0)
        self.x_hover = StringVar()
        self.make_label(textvariable=self.x_hover, column=4)
        self.y_hover = StringVar()
        self.make_label(textvariable=self.y_hover, column=5)
        self.v_hover = StringVar()
        self.make_label(textvariable=self.v_hover, column=6)
        self.set_hover(0., 0., 0.)

        self.config(row=1)
        aper_button = self.make_button(icon_name='im_aper', width=5,
                                       tt='Define photometric aperture')
        aper_button.config(command=lambda: image_panel.start_command(phot_command))

        self.config(width=9)
        r1, rratio, aratio = StringVar(self, '10.0'), StringVar(self, '1.1'), StringVar(self, '1.3')
        r_entry = self.make_entry(textvariable=r1,
                                  fmt='{:5.1f}', column=1)
        r_entry.bind("<Return>", image_panel.on_change)
        rratio_entry = self.make_entry(textvariable=rratio,
                                       fmt='{:5.1f}', column=2)
        rratio_entry.bind("<Return>", image_panel.on_change)
        aratio_entry = self.make_entry(textvariable=aratio,
                                       fmt='{:5.1f}', column=3)
        aratio_entry.bind("<Return>", image_panel.on_change)
        phot_command = PhotCommand(r1, rratio, aratio)

        self.config(row=1)
        self.make_label(textvariable=phot_command.x_cen, column=4,
                        tt='centroid x')
        self.make_label(textvariable=phot_command.y_cen, column=5,
                        tt='centroid y')
        self.make_label(textvariable=phot_command.v_phot, column=6,
                        tt='sum of signal in aperture')

        self.phot_command = phot_command

    def set_hover(self, x, y, val):
        self.x_hover.set('{:6.2f}'.format(x))
        self.y_hover.set('{:6.2f}'.format(y))
        self.v_hover.set('{:10.3e}'.format(val))
        return
