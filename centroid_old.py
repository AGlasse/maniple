from jwst import datamodels
import numpy as np
import matplotlib as plt
from matplotlib import style, pyplot as plt
from matplotlib import rcParams
from matplotlib.pyplot import figure
from photutils import centroid_2dg as c2dg

image_folder = '/home/achg/Mirisim/20190129_210959_mirisim/det_images/'
f770w_name = 'det_image_seq1_MIRIMAGE_F770Wexp1.fits'
f770w_name = 'det_image_seq1_MIRIMAGE_F770Wexp1.fits'
image_path = image_folder + image_name

img1 = datamodels.open(image_path)
#img1.data[np.where(img1.dq != 0.0)]=np.nan
img1.data[np.where(img1.pixeldq == 262660)]=np.nan
img1.data[np.where(img1.pixeldq == 262656)]=np.nan
img1.data[np.where(img1.pixeldq == 2359812)]=np.nan
img1.data[np.where(img1.pixeldq == 2359808)]=np.nan

i = 0
f = 5
frame = img1.data[i,f]
rcGuess = [[567,467], [477,460], [560,557],  [470,550],
           [116,993], [116,451], [984,970], [1001,111]]
xyH = 4
xyBox = 2*xyH
mask = np.full((xyBox, xyBox), np.median(frame))
#for i in range(0, 8):
#    rcC = rcGuess[i]
#    x1 = rcC[0] - xyH
#    y1 = rcC[1] - xyH
#    patch = frame[x1:x1+2*xyH, y1:y1+2*xyH]
#    xc, yc = c2dg(frame)
#    print(xc, yc)
#    x = int(xc)
#    y = int(yc)
#    frame[x-xyH:x+xyH, y-xyH:y+xyH] = mask



rcParams['figure.figsize'] = [10., 8.]
plt.rcParams.process_move({'font.size': 18})
fig, ax = plt.subplots()
fig = plt.imshow(frame, interpolation='nearest',
                 cmap='hot',
                 vmin=10000.0, vmax=50000.0, origin='lower')
plt.title(' Image',fontsize='medium')
plt.colorbar()
plt.show()
