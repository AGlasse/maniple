from jwst import datamodels
import numpy as np
import matplotlib as plt
from matplotlib import style, pyplot as plt
from matplotlib import rcParams
from matplotlib.pyplot import figure
from photutils import centroid_2dg as c2dg

def readImage(path):
    from astropy.io import fits

    hduList = fits.open(path, mode='readonly')
    im = hduList[1].data
    return im
#------------------------------------------------------------------------------
def plotImage(frame, **kwargs):

    suppressPlot = kwargs.get('suppressplot', False)
    if suppressPlot:
        return

    vmin = kwargs.get('vmin', 0.0)
    vmax = kwargs.get('vmax', 1.0)
    shape = frame.shape
    xrange = kwargs.get('xrange', [0, shape[0]])
    yrange = kwargs.get('yrange', [0, shape[1]])

    title = kwargs.get('title', ' - ')
    rcParams['figure.figsize'] = [10., 8.]
    plt.rcParams.process_move({'font.size': 18})
    fig, ax = plt.subplots()
    subframe = frame[xrange[0]:xrange[1], yrange[0]:yrange[1]]

    fig = plt.imshow(subframe, interpolation='nearest', cmap='hot',
                     vmin=vmin, vmax=vmax, origin='lower')
    plt.title(title, fontsize='medium')
    plt.colorbar()
    plt.show()
#------------------------------------------------------------------------------
def normalise(frame):
    import numpy as np

    vmed = np.median(frame)
    vmax = np.max(frame)
    vrange = vmax - vmed
    frame = frame - vmed
    frame = frame / vrange
    return frame
#------------------------------------------------------------------------------
def process(path, xyCentre, **kwargs):

    full = readImage(path)
    h = 40
    r1 = xyCentre[1] - h
    r2 = xyCentre[1] + h
    c1 = xyCentre[0] - h
    c2 = xyCentre[0] + h
    im = full[r1:r2, c1:c2]
    im = normalise(im)

    plotImage(im, vmin=0.0, vmax=1.0, **kwargs)
    xyMax = np.unravel_index(np.argmax(im, axis=None), im.shape)
    x1 = xyMax[0]-10
    y1 = xyMax[1]-10

    subIm = im[x1:x1+20, y1:y1+20]
    centroid = c2dg(subIm)
    rowcen = x1 + centroid[0]
    colcen = y1 + centroid[1]
    return (colcen, rowcen)
#------------------------------------------------------------------------------
def plotDitherPattern(cenList, fnList, idList, **kwargs):

    cenArray = np.asarray(cenList)
    xDataMin = min(cenArray[:,0])
    xDataMax = max(cenArray[:,0])
    xDataLim = [xDataMin, xDataMax]
    yDataMin = min(cenArray[:,1])
    yDataMax = max(cenArray[:,1])
    yDataLim = [yDataMin, yDataMax]
    xLim = kwargs.get('xlim', xDataLim)
    yLim = kwargs.get('ylim', yDataLim)
    title = kwargs.get('title', ' - ')

    fig, ax = plt.subplots(1, 1)
    ax.set_xlim(xLim)
    ax.set_ylim(yLim)
    fig.suptitle(title)

    nPoints = len(cenList)
    for i in range(0, nPoints):
        colour = 'black'
        mk = 'x'
        filterName = fnList[i]
        id = idList[i]
        if (filterName == 'F560W'):
            colour = 'blue'
            mk = 'o'
        if (filterName == 'F1000W'):
            colour = 'green'
            mk = 'x'
        if (filterName == 'F1130W'):
            colour = 'red'
            mk = '+'
        if (filterName == 'F1280W'):
            colour = 'orange'
            mk = 'D'
        if (filterName == 'F1500W'):
            colour = 'magenta'
            mk = 'd'
        if (filterName == 'F1800W'):
            colour = 'orange'
            mk = '+'

        ax.plot(cenList[i][0], cenList[i][1], clip_on=True,
                fillstyle='none', color=colour,
                marker=mk, ms=15.0, mew=1.0)
    plt.show()
    return
#==============================================================================
from photutils import centroid_2dg as c2dg
from os.path import join
import glob

folder = './MirisimData/'

nLocations = 4
for i in range(0, 4):
    xyCentre = xyCentreList[i]
    cenList = []
    fnList = []
    idList = []
    fileList = glob.iglob(join(folder, '**/*_cal.fits'), recursive=True)
    for f in fileList:
        tokenList = f.split('_')
        filterName = tokenList[2][0:-4]
        isImager = tokenList[1] == 'IMA'
        isSW = filterName != 'F2550W' and filterName != 'F2100W'
        if isImager and isSW:
            print(f)
            fnList.append(filterName)
            id = tokenList[4]
            idList.append(id)
            fmt = '{:10s}{:10s}'
            title = fmt.format(filterName, id)
            cen = process(f, xyCentre, suppressplot=True, title=title)
            cenList.append(cen)
            fmt = '{:10s}{:10s}{:10.3f}{:10.3f}'
            print(fmt.format(filterName, id, cen[0], cen[1]))

    title = 'Centre (col,row) = ({:4d},{:4d})'.format(xyCentre[0], xyCentre[1])
    plotDitherPattern(cenList, fnList, idList, title=title)

#==============================================================================