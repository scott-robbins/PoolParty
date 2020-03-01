import matplotlib.animation as animation
import matplotlib.pyplot as plt
import scipy.misc as misc
from tqdm import tqdm
import numpy as np
import picam
import utils
import time
import sys
import os


def load_images():
    print '\033[32m================\033[0m \033[1mLoading Images\033[0m\033[32m ================\033[0m'
    f = plt.figure()
    images = {}
    reel = []
    if not os.path.isdir('Classifieds/'):
        os.mkdir('Classifieds')
    x1 = 900
    x2 = 1980
    y1 = 960
    y2 = 1931
    if os.path.isdir('PiCamImages'):
        bar = tqdm(total=len(os.listdir('PiCamImages')))
        for file_name in os.listdir('PiCamImages/'):
            images[file_name] = np.array(plt.imread('PiCamImages/%s' % file_name))
            reel.append([plt.imshow(images[file_name][y1:y2, x1:x2, :])])
            misc.imsave('Classifieds/%s'%file_name,images[file_name][y1:y2, x1:x2, 2])
            bar.update(1)
    bar.close()
    print '%d Images of Shape(s) [%d, %d]' % (len(images),
                                              images[file_name].shape[0],
                                              images[file_name].shape[1])
    a = animation.ArtistAnimation(f,reel,interval=100,blit=True,repeat_delay=900)
    plt.show()
    return images


# Get The Images Logged by the PiCam
camera_snaps = load_images()

ex = camera_snaps.values().pop()
x1 = 960
x2 = 1980
y1 = 960
y2 = 1931
# plt.imshow(ex[y1:y2, x1:x2, :])
# plt.show()
