#!/usr/bin/python
import numpy as np
import math
from source.command.command import Command
from tkinter import StringVar
from photutils import CircularAperture, aperture_photometry
from photutils.centroids import centroid_com


class PhotCommand(Command):

    def __init__(self, r1, rratio):
        Command.__init__(self)
        self.ap_coords = self.update_aperture_coords(float(r1.get()), float(rratio.get()))
        self.do_centroid, self.do_skysub = None, None

        self.x_cursor = 0
        self.y_cursor = 0
        self.x_cen = StringVar()
        self.y_cen = StringVar()
        self.v_phot = StringVar()
        self.x_cen.set('{:6.2f}'.format(0.))
        self.y_cen.set('{:6.2f}'.format(0.))
        self.v_phot.set('{:10.3f}'.format(0.))
        return

    def start(self):
        self.state = self.EDITING
        return

    def mouse_button_pressed(self, event, x, y, image_panel):
        is_done = False
        if self.state is self.EDITING:
            print('running photometry')
            self.do_photometry(image_panel.image)
            self.state = self.STANDBY
            is_done = True
        else:
            print('phot_command.process_click - no valid state')
        return is_done

    def mouse_motion(self, xc, yc):
        self.x_cursor, self.y_cursor = xc, yc
        return

    def plot(self, ax):
        """ Overplot annulus on image.
        """
        _, _, _, xys = self.ap_coords
        cols = ['green', 'blue', 'blue']
        for i in range(0, 3):
            x = xys[i][0] + self.x_cursor
            y = xys[i][1] + self.y_cursor
            ax.plot(x, y, color=cols[i])
        return

    @staticmethod
    def update_aperture_coords(r_tgt, ksky_inner):
        ksky_outer = math.sqrt(1 + ksky_inner * ksky_inner)
        r_inner = r_tgt * ksky_inner
        r_outer = r_tgt * ksky_outer
        arad = np.arange(0.0, 2.0 * math.pi + 0.1, 0.1)       # Angle coordinate
        sin_a, cos_a = np.sin(arad), np.cos(arad)
        # Photometric aperture coordinates
        xys = []
        for r in [r_tgt, r_inner, r_outer]:
            x, y = np.multiply(sin_a, r), np.multiply(cos_a, r)
            xys.append([x, y])
        ap_coords = r_tgt, r_inner, r_outer, xys
        return ap_coords

    def do_photometry(self, image):

        r_tgt, r_inner, r_outer, xys = self.ap_coords

        position = [(self.x_cursor, self.y_cursor)]
        if self.do_centroid:
            position = centroid_com(image)

        radii = [r_tgt]
        if self.do_skysub:
            radii.append(r_inner)
            radii.append(r_outer)
        vals = []
        for r in radii:
            aperture = CircularAperture(position, r=r)
            phot_table = aperture_photometry(image, aperture)
            val = phot_table['aperture_sum'][0]
            vals.append(val)
        vphot = vals[0]
        if self.do_skysub:
            vsky = vals[2] - vals[1]
            vphot -= vsky
        self.x_cen.set('{:6.2f}'.format(position[0]))
        self.y_cen.set('{:6.2f}'.format(position[1]))
        self.v_phot.set('{:10.3f}'.format(vphot))
        return

    def do_eed(self, image, **kwargs):
        """ Generate EED curve of growth plots relative to the current centroid
        position.
        Calculate the enslitted energy along an axis.
        :param axis: Variable axis, 'spectral' or 'spatial'
        :param kwargs: is_log = True for samples which are uniform in log space
        :return radii: Sampled axis
                ees_mean: Mean enslitted energy profile
                ees_rms:
                ees_all: EE profile averaged for all images
        """
        from photutils import CircularAperture, aperture_photometry

        debug = kwargs.get('debug', False)
        is_log = kwargs.get('log10sampling', True)  # Use sampling equispaced in log10

        r_sample = 0.1
        r_start = r_sample
        r_max = 60.0   # Maximum radial size of aperture (a bit less than 1/2 image size)

        xc = float(self.x_cen.get())
        yc = float(self.y_cen.get())
        centroid = (xc, yc)

        radii = np.arange(r_start, r_max, r_sample)
        n_points = radii.shape[0]
        if is_log:      # Remap the same number of points onto a log uniform scale.
            k = math.log10(r_max / r_start) / n_points
            lr = math.log10(r_start)
            for i in range(0, n_points):
                radii[i] = math.pow(10., lr)
                lr += k

        ees_all = np.zeros((n_points))
        imin = np.amin(image)
        imax = np.amax(image)

        for i in range(0, n_points):        # One radial point per row
            r = radii[i]      # Increase aperture width to measure spectral cog profile
            position = [(self.x_cursor, self.y_cursor)]
            aperture = CircularAperture(position, r=self.r_tgt)
            phot_table = aperture_photometry(image, aperture)
#            ees_all[i,j] = LMSIQAnalyse.exact_rectangular(image, aperture)
        return

    def make_mask(self, image, position, r_aper):
        shape = image.shape
        xc = int(position[0][1])
        yc = int(position[0][0])
        rbox = int(r_aper + 1.0)
        mask = np.zeros(shape, dtype=bool)
        for x in range(xc-rbox, xc+rbox):
            dx = x - xc
            for y in range(yc-rbox, yc+rbox):
                dy = y - yc
                r2 = dx*dx + dy*dy
                r = math.sqrt(r2)
                mask[y, x] = True if r <= r_aper else False
        return mask
