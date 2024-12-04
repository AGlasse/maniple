from panel import Panel
from tkinter import StringVar, IntVar
from command.phot_command import PhotCommand


class PhotPanel(Panel):

    def __init__(self, parent, image_panel):
        Panel.__init__(self, parent)

        self.image_panel = image_panel
        self.config(width=9)

        self.config(row=0)              # Display signal value at cursor
        self.x_hover = StringVar()
        self.make_label(textvariable=self.x_hover, column=4, tt='x')
        self.y_hover = StringVar()
        self.make_label(textvariable=self.y_hover, column=5, tt='y')
        self.v_hover = StringVar()
        self.make_label(textvariable=self.v_hover, column=6, tt='value')
        self.set_hover(0., 0., 0.)

        self.config(row=1)              # Define photometric measurement
        aper_button = self.make_button(icon_name='im_aper', width=5,
                                       tt='Define photometric aperture')

        rtgt_txt, ksky_inner_txt = '10.0', '1.1'
        self.rtgt_sv, self.ksky_inner_sv = StringVar(self, rtgt_txt), StringVar(self, ksky_inner_txt)
        rtgt_entry = self.make_entry(textvariable=self.rtgt_sv,
                                     fmt='{:5.1f}', column=1,
                                     tt='Aperture radius / pix.')
        rtgt_entry.bind("<Return>", self.on_change)
        ksky_inner_entry = self.make_entry(textvariable=self.ksky_inner_sv,
                                           fmt='{:5.1f}', column=2,
                                           tt='Inner sky annulus radius / aperture radius')
        ksky_inner_entry.bind("<Return>", self.on_change)
        phot_command = PhotCommand(self.rtgt_sv, self.ksky_inner_sv)
        aper_button.config(command=lambda: image_panel.start_command(phot_command))

        self.make_label(textvariable=phot_command.x_cen, column=4, tt='centroid x')
        self.make_label(textvariable=phot_command.y_cen, column=5, tt='centroid y')
        self.make_label(textvariable=phot_command.v_phot, column=6, tt='sum of signal in aperture')

        self.config(row=2)
        self.x_cursor = StringVar()
        self.make_label(textvariable=self.x_cursor, column=4, tt='x cursor')
        self.x_cursor.set('{:6d}'.format(0))
        self.y_cursor = StringVar()
        self.make_label(textvariable=self.y_cursor, column=5, tt='y cursor')
        self.y_cursor.set('{:6d}'.format(0))

        self.config(row=3)
        self.centroid_flag = StringVar()
        text = 'Snap to centroid'
        self.do_centroid = IntVar()
        self.make_button(text=text, is_checkbutton=True, intvar=self.do_centroid,
                         tt=text, column=0, columnspan=3)

        self.config(row=4)
        text = 'Subtract sky annulus'
        self.do_skysub = IntVar()
        self.make_button(text=text, is_checkbutton=True, intvar=self.do_skysub,
                         tt=text, column=0, columnspan=3)
        phot_command.do_centroid = self.do_centroid
        phot_command.do_skysub = self.do_skysub
        phot_command.update_aperture_coords(float(self.rtgt_sv.get()),
                                            float(self.ksky_inner_sv.get()))
        self.phot_command = phot_command
        return

    def on_change(self, event):
        r_tgt = float(self.rtgt_sv.get())
        ksky_inner = float(self.ksky_inner_sv.get())
        self.phot_command.update_aperture_coords(r_tgt, ksky_inner)
        self.image_panel.on_change()
        return

    def set_cursor(self, xc, yc):
        self.x_cursor.set('{:6d}'.format(int(xc + 0.5)))
        self.y_cursor.set('{:6d}'.format(int(yc + 0.5)))
        return

    def set_hover(self, x, y, val):
        self.x_hover.set('{:6.2f}'.format(x))
        self.y_hover.set('{:6.2f}'.format(y))
        self.v_hover.set('{:10.3e}'.format(val))
        return
