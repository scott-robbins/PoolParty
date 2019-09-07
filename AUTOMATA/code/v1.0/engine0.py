from matplotlib.animation import FFMpegWriter
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import scipy.ndimage as ndi
import scipy.misc as misc
import numpy as np
import imutils
import time
import os


ani_cmd = 'ffmpeg -loglevel quiet -r 2 -i pic%d.png -vcodec libx264' \
          ' -pix_fmt yuv420p cas1.mp4'
clean = 'ls *.png | while read n; do rm $n; done'

tic = time.time()
k0 = [[1,1,1],[1,0,1],[1,1,1]]
k1 = [[1,1,1,1],[1,0,0,1],[1,0,0,1],[1,1,1,1]]
k2 = [[0,0,0,0],[0,1,1,0],[0,1,1,0],[0,0,0,0]]


def simulate(world, depth, save):
    dims = world.shape
    f = plt.figure()
    simulation = []
    simulation.append([plt.imshow(world)])
    mapping = imutils.LIH_flat_map_creator(np.zeros((dims[0], dims[1])))
    for step in range(depth):
        rch = world[:,:,0]
        gch = world[:,:,1]
        bch = world[:,:,2]

        rc1 = ndi.convolve(rch,k0,origin=0).flatten()
        gc1 = ndi.convolve(gch,k0,origin=0).flatten()
        bc1 = ndi.convolve(bch,k0,origin=0).flatten()

        rc2 = ndi.convolve(rch, k1, origin=0).flatten()
        gc2 = ndi.convolve(gch, k1, origin=0).flatten()
        bc2 = ndi.convolve(bch, k1, origin=0).flatten()

        N = dims[0]*dims[1]

        for ii in range(N):
            [x, y] = mapping[ii]
            if (rch[x, y] and gch[x, y] and bch[x, y]) == 0:
                if gc1[ii] % 6 == 0:
                    world[x, y, 0] = 0
                    world[x, y, 1] = 1
                    world[x, y, 2] = 0
            if gc2[ii] >= 4 and rc1[ii] == 3:
                world[x, y, 0] = 1
                world[x, y, 1] = 0
                world[x, y, 2] = 1
            if gc1[ii] < rc1[ii] and bc1[ii] == 0:
                world[x, y, 0] = 1
                world[x, y, 1] = 0
                world[x, y, 2] = 0
            if gc2[ii] == 4 and rch[x, y]:
                world[x, y, 0] = 0
                world[x, y, 1] = 1
                world[x, y, 2] = 0
            if rc1[ii] > 6 and rch[x,y]==0 and gch[x,y]:
                world[x, y, 2] = 1
            if rc2[ii] > 4 and (gch[x, y] and bch[x, y]) and rc1[ii] % 5 == 0:
                world[x, y, 0] = 1
                world[x, y, 1] = 0
                world[x, y, 2] = 0
            if rch[x,y]==1 and bch[x,y]==1:
                if gc1[ii] > 5 and gc2[ii]==4:
                    world[x,y,:] = 0
            if save['save']:
                misc.imsave('pic'+str(step)+'.png', world)

        simulation.append([plt.imshow(world)])
    a = animation.ArtistAnimation(f,simulation,interval=100,blit=True,repeat_delay=900)
    if save:
        writer = FFMpegWriter(fps=save['frame_rate'], metadata=dict(artist='Me'), bitrate=1800)
        a.save(save['file_name'], writer=writer)
    print 'Simulation FINISHED [%ss Elapsed]' % str(time.time()-tic)
    plt.show()


width = 250
height = 250
depth = 10
state = np.zeros((width, height, 3))
# Green Grass
state[:,:,1] = imutils.draw_centered_box(state[:,:,1],100,1, False)
state[:,:,0] = imutils.draw_centered_box(state[:,:,0],110,1, False)
# Small Fire
state[:,:,0] = imutils.draw_centered_box(state[:,:,0],35,1, False)
state[:,:,1] -= imutils.draw_centered_box(state[:,:,0],35,1, False)

# f,ax = plt.subplots(1, 2)
# ax[0].imshow(ndi.convolve(state[:,:,0],k1))
# ax[1].imshow(ndi.convolve(state[:,:,1],k1))
# plt.show()

print 'Starting Simulation'
opts = {'save': False, 'frame_rate': 100, 'file_name': 'basic_square.mp4'}
simulate(state, depth, opts)
if opts['save']:
    os.system(ani_cmd)
    os.system(clean)
