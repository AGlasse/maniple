#!/usr/bin/python
import numpy as np
import math

import photutils

from command import Command
from tkinter import StringVar
from imagePanel import ImagePanel


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
        return

    def start(self):
        self.state = self.EDITING
        return

    def set_aperture(self, r1_sv, rratio_sv, aratio_sv):
        arad = np.arange(0.0, 2.0*math.pi + 0.1, 0.1)
        # Photometric aperture
        r1, rratio, aratio = float(r1_sv.get()), float(rratio_sv.get()), float(aratio_sv.get())
        x1 = r1 * np.sin(arad)
        y1 = r1 * np.cos(arad)
        # Inner circumference of sky annulus
        x2 = np.multiply(x1, rratio)
        y2 = np.multiply(y1, rratio)
        # Outer circumference of sky annulus
        k = math.sqrt(aratio + rratio*rratio)
        x3 = np.multiply(x1, k)
        y3 = np.multiply(y1, k)
        self.r1_sv, self.rratio_sv, self.aratio_sv = r1_sv, rratio_sv, aratio_sv
        self.xys = np.asarray((x1, y1, x2, y2, x3, y3))
        return

    def plot(self, axes):
        cols = ['red', 'green', 'green']
        for i in range(0, 3):
            x = self.xys[2*i] + self.xc
            y = self.xys[2*i+1] + self.yc
            axes.plot(x, y, color=cols[i])
        return

    def process_click(self, event, x, y, image_panel):
        is_done = False
        self.xc, self.yc = x, y
        if self.state is self.EDITING:
            self.do_photometry(image_panel.image)
            self.state = self.STANDBY
            is_done = True
        else:
            print('command.process_click - no valid state')
        return is_done

    def process_move(self, x, y):
        if self.state is self.EDITING:
            self.xc = x
            self.yc = y
        return

    def do_photometry(self, image):
        """ Analyse the nearest star-like object to the cursor. """

        from photutils import CircularAperture, aperture_photometry, centroid_2dg

        xbl = ImagePanel.xmin_control.get_val()
        ybl = ImagePanel.ymin_control.get_val()
        r1 = float(self.r1_sv.get())

        position = [(self.xc-xbl, self.yc-ybl)]
        aperture = CircularAperture(position, r=r1)
        xb, yb, vb = self._find_brightest_pixel_in_aperture(image, aperture)
        print("Brightest pixel at x,y ={:8.2f}, {:8.2f}, v= {:8.1f}".format(xb, yb, vb))

        x1, y1 = xb - int(r1), yb - int(r1)
        x2, y2 = x1 + 2*int(r1), y1 + 2*int(r1)
        sub_image = image[y1:y2, x1:x2]

        dsf = photutils.DAOStarFinder(threshold=vb/10.0, fwhm=2.00)
        stars = dsf(sub_image)
        print(stars)
        print()
        fmax = 0.0
        bstar = None
        for star in stars:
            f = star['flux']
            if f > fmax:
                bstar = star
                fmax = f

        xcen = bstar['xcentroid'] + xbl + x1
        ycen = bstar['ycentroid'] + ybl + y1
        vphot = bstar['flux']
        print(xcen, ycen, vphot)

        fmt = "pC.do_phot xcursor, ycursor | xcen, ycen= {:8.2f}, {:8.2f} {:8.2f}, {:8.2f}"
        print(fmt.format(self.xc, self.yc, xcen, ycen))
        self.x_cen.set('{:6.2f}'.format(xcen))
        self.y_cen.set('{:6.2f}'.format(ycen))
        self.v_phot.set('{:10.3f}'.format(vphot))
        return

    @staticmethod
    def _find_brightest_pixel_in_aperture(image, aperture):
        vb = -10000.0
        x1f, x2f, y1f, y2f = aperture.bbox[0].extent
        x1, x2, y1, y2 = int(x1f + 1.0), int(x2f + 1.0), int(y1f + 1.0), int(y2f + 1.0)
        r = aperture.r
        xc, yc = aperture.positions[0][0], aperture.positions[0][1]
        xb, yb = -1, -1
        for x in range(x1, x2):
            dx = x - xc
            for y in range(y1, y2):
                dy = y - yc
                dr = dx * dx + dy * dy
                v = image[y, x]
                if dr < r and v > vb:
                    xb, yb, vb = x, y, v
        return xb, yb, vb

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

    def make_mask(self, image, position, xbl, ybl, r_aper):
        shape = image.shape
        row_cen = int(position[0][1]) - ybl
        col_cen = int(position[0][0]) - xbl
        rbox = int(r_aper + 1.0)
        mask = np.zeros(shape, dtype=bool)
        nrows, ncols = mask.shape
        for row in range(0, nrows):
            drow = row_cen - row
            for col in range(0, ncols):
                dcol = col_cen - col
                r2 = dcol * dcol + drow * drow
                r = math.sqrt(r2)
                mask[row, col] = True if r > r_aper else False
        return mask
