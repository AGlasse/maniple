#!/usr/bin/python
import numpy as np
import math
from command import Command
from tkinter import StringVar


class PhotCommand(Command):

    def __init__(self, r1, rratio, aratio):
        Command.__init__(self)
        self.xc = 0
        self.yc = 0
        self.set_aperture(r1, rratio, aratio)
        self.x_cen = StringVar()
        self.y_cen = StringVar()
        self.v_phot = StringVar()
        self.x_cen.set('{:6.2f}'.format(0.))
        self.y_cen.set('{:6.2f}'.format(0.))
        self.v_phot.set('{:10.3f}'.format(0.))


    def start(self):
        self.state = self.EDITING

    def set_aperture(self, r1, rratio, aratio):
        arad = np.arange(0.0, 2.0*math.pi + 0.1, 0.1)
        # Photometric aperture
        x1 = r1 * np.sin(arad)
        y1 = r1 * np.cos(arad)
        # Inner circumference of sky annulus
        x2 = np.multiply(x1, rratio)
        y2 = np.multiply(y1, rratio)
        # Outer circumference of sky annulus
        k = math.sqrt(aratio + rratio*rratio)
        x3 = np.multiply(x1, k)
        y3 = np.multiply(y1, k)
        self.r1 = r1
        self.rratio = rratio
        self.aratio = aratio
        self.xys = np.asarray((x1, y1, x2, y2, x3, y3))

    def plot(self, axes):
        cols = ['red', 'green', 'green']
        for i in range(0, 3):
            x = self.xys[2*i] + self.xc
            y = self.xys[2*i+1] + self.yc
            axes.plot(x, y, color=cols[i])

    def process_click(self, event, x, y, image_panel):
        is_done = False
        if self.state is self.EDITING:
            self.do_photometry(image_panel.image)
            self.state = self.STANDBY
            is_done = True
        else:
            print('command.process_click - no valid state')
        return is_done

    def process_move(self, xc, yc):
        if self.state is self.EDITING:
            self.xc = xc
            self.yc = yc

    def do_photometry(self, image):
        from photutils import CircularAperture, aperture_photometry, centroid_2dg

        position = [(self.xc, self.yc)]
        aperture = CircularAperture(position, r=self.r1)
        phot_table = aperture_photometry(image, aperture)
        vphot = phot_table['aperture_sum'][0]
        mask = self.make_mask(image, position, self.r1)
        (xcen, ycen) = centroid_2dg(image, mask=mask)
        self.x_cen.set('{:6.2f}'.format(xcen))
        self.y_cen.set('{:6.2f}'.format(ycen))
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
        from photutils import CircularAperture, aperture_photometry, centroid_2dg

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
            position = [(self.xc, self.yc)]
            aperture = CircularAperture(position, r=self.r1)
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
                mask[y, x] = True if r > r_aper else False
        return mask
