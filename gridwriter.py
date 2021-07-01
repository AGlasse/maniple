""" Write a mirisim scene file with a 10 x 10 grid of point sources
"""
import numpy as np
from matplotlib import style, pyplot as plt
from matplotlib import rcParams

scene_file = open("/home/achg/Mirisim/grid_scene.ini", "w")
#scene_file.write("[sky]")

fmt = "  {:11s}= {:20s}{:30s}"
scene_file.write('[sky]\n')
scene_file.write(fmt.format('name', 'sky0', '# Name of sky scene\n'))
scene_file.write(fmt.format('loglevel', '0', '# 0: no log, 1: single summary, 2: full report\n'))
scene_file.write('[Background]\n')
scene_file.write(fmt.format('gradient', '5', '# % over 1 arcmin (JWST component only)\n'))
scene_file.write(fmt.format('pa', '15', '# position angle of gradient (background increasing towards PA)\n'))
scene_file.write(fmt.format('centreFOV', '0 0', '# centre of FOV\n'))
scene_file.write(fmt.format('level', 'low', '# Background with the G-component of the model included "high" or missing "low"\n'))
scene_file.write(fmt.format('tconstant', '0', '# time-constant for time-dependent background [minutes]\n'))
scene_file.write(fmt.format('fast', '0', '# Use or not the 2.5D speed up when flux(RA, DEC, WAV) = flux1(RA, DEC) * flux2(WAV)\n'))
scene_file.write('\n')

idx = 1
for i in range(-10, 16):
    dv2 = 5.0 * i
    for j in range(-12, 12):
        dv3 = 5.0 * j
        pointID = '[point_{:d}]\n'.format(idx)
        scene_file.write(pointID)
        fmt1 = "  {:15s}= {:20s}{:30s}"
        scene_file.write(fmt1.format('Type', 'Point',  '# Type of target\n'))
        location = '{:5.1f} {:5.1f}'.format(dv2, dv3)
        scene_file.write(fmt1.format('Cen', location, '# Where to place the target (arcsec offsets from centreFOV).\n'))
        print(fmt1.format('Cen', location, '# Where to place the target (arcsec offsets from centreFOV).\n'))
        scene_file.write('\n')
        scene_file.write('  [[sed]]\n')
        fmt = "    {:17s}= {:20s}{:30s}"
        scene_file.write(fmt.format('Type', 'BB', '# Type of spectral energy distribution (e.g. BlackBody spectrum)\n'))
        scene_file.write(fmt.format('Temp', '10000', '# Representative temperature for the blackbody\n'))
        scene_file.write(fmt.format('flux', '3000.0', '# {optional} Reference flux (in microJy) for scaling the blackbody function\n'))
        scene_file.write(fmt.format('wref', '10', '# {optional} reference wavelength (in micron)\n'))
        scene_file.write('\n')
        idx = idx + 1

scene_file.close()
