from skimage import data, io, segmentation, color
from matplotlib.animation import FFMpegWriter
import matplotlib.animation as animation
from skimage.future import graph
import matplotlib.pyplot as plt
import scipy.ndimage as ndi
from tqdm import tqdm
import numpy as np
import picam
import utils
import time
import sys
import os


def edge_detect(im, show):
    iavg = np.zeros(im.shape)
    b = [[1,2,1],[-1,0,-1],[1,2,1]]
    iavg[:,:,0] = im[:,:,0] - im[:,:,0].mean()
    iavg[:,:,1] = im[:,:,1] - im[:,:,1].mean()
    iavg[:,:,2] = im[:,:,2] - im[:,:,2].mean()

    if show:
        f,ax = plt.subplots(1,2)
        ax[0].imshow(im)
        ax[1].imshow(iavg)
        plt.show()

    return iavg


if 'detect' in sys.argv:
    tic = time.time()
    pic = picam.snap_save()
    pic_in = np.array(plt.imread(pic))

    print '================================================================='
    print '\033[1mAnalyzing \033[3m\033[31mPi-Cam\033[0m\033[1m Image\033[0m'

    out = edge_detect(pic_in, True)

    print 'FINISHED [%ss Elapsed]' % str(time.time() - tic)


if 'watch' in sys.argv:
    f = plt.figure()
    raw_images = {}
    reel = []
    id = 0
    os.system('ls PiCamImages/ | while read n; do echo $n >> names.txt; done')
    image_names = utils.swap('names.txt', True)
    ''' Because of naming convention, ls will have these images time sorted '''
    bar = tqdm(total=len(image_names))
    for line in image_names:
        raw_images[id] = np.array(plt.imread('PiCamImages/'+line))
        im = raw_images[id]
        # if id > 0:
        #     im = im - raw_images[id-1]
        # im = ndi.gaussian_laplace(im, sigma=im.mean())
        id += 1
        bar.update(1)
        reel.append([plt.imshow(im-im.mean())])
    bar.close()
    a = animation.ArtistAnimation(f,reel,interval=100,blit=True,repeat_delay=900)
    plt.show()

