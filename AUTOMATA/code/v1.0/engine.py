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
          ' -pix_fmt yuv420p cas.mp4'
clean = 'ls *.png | while read n; do rm $n; done'

tic = time.time()
k0 = [[1,1,1],[1,0,1],[1,1,1]]
k1 = [[1,1,1,1],[1,0,0,1],[1,0,0,1],[1,1,1,1]]
k2 = [[0,0,0,0],[0,1,1,0],[0,1,1,0],[0,0,0,0]]
k3 = [[1,1,1,1,1],
      [1,0,0,0,1],
      [1,0,1,0,1],
      [1,0,0,0,1],
      [1,1,1,1,1]]
k4 = [[1,1,0,1,1],
      [1,1,0,1,1],
      [0,0,1,0,0],
      [1,1,0,1,1],
      [1,1,0,1,1]]
k5 = [[0,0,1,1,0,0],
      [0,1,1,1,1,0],
      [1,1,1,1,1,1],
      [1,1,1,1,1,1],
      [0,1,1,1,1,0],
      [0,0,1,1,0,0]]
k6 = [[1,1,0,0,1,1],
      [1,0,0,0,0,1],
      [0,0,0,0,0,0],
      [0,0,0,0,0,0],
      [1,0,0,0,0,1],
      [1,1,0,0,1,1]]


def sim_0(world, depth, save):
    f = plt.figure()
    simulation = []
    simulation.append([plt.imshow(world)])
    ind2sub = imutils.LIH_flat_map_creator(world[:, :, 0])
    for step in range(depth):
        rch = world[:,:,0]
        gch = world[:,:,1]
        bch = world[:,:,2]
        r1 = ndi.convolve(rch, k0, origin=0).flatten()
        g1 = ndi.convolve(gch, k0, origin=0).flatten()
        b1 = ndi.convolve(bch, k0, origin=0).flatten()
        for ii in range(len(r1)-1):
            [x, y] = ind2sub[ii]
            if b1[ii] % 5 == 0:
                if b1[ii] and rch[x,y]:
                    world[x, y, 2] = 0
                elif b1[ii] and not r1[ii] and not g1[ii]:
                    world[x, y, 1] = 1
            if r1[ii] % 5 == 0:
                world[x,y,0] = 0
            if rch[x,y] and r1[ii] % 7 == 0:
                world[x,y,1] = 1
                world[x, y, 0] = 1
            if (rch[x,y] and bch[x,y]) and b1[ii] % 7 == 0:
                world[x,y,0] = 0
                world[x, y, 2] = 1
            if g1[ii] % 3 or (bch[x,y] and rch[x,y] and r1[ii]%3==0):
                if gch[x,y] and not bch[x,y]:
                    world[x,y,2] = 1
                if not gch[x,y] and bch[x,y]:
                    world[x,y,1] = 1
            if rch[x,y] and gch[x,y] and bch[x,y]:
                if r1[ii] % 5 ==0:
                    world[x,y,1] = 0
            if not rch[x,y] and not gch[x,y] and not bch[x,y]:
                if b1[ii] > 5:
                    world[x, y, 2] = 1
                if r1[ii] % 7 ==0:
                    world[x, y, 0] = 1
        simulation.append([plt.imshow(world)])
        if save:
              misc.imsave('pic%d.png' % step, world)
    print '[*] Simulation Finished. Rendering... [%ss Elapsed]' % str(time.time()-tic)
    a = animation.ArtistAnimation(f, simulation, interval=100, blit=True, repeat_delay=900)
    print '[*] Finished [%ss Elapsed]' % str(time.time()-tic)
    plt.show()


shape_0 = [250, 250]
shape_1 = [480, 360]

save = True
test_state_0 = np.zeros((shape_0[0], shape_0[1], 3))
test_state_0[:, :, 2] = imutils.draw_centered_circle(test_state_0[:, :, 2], 40, 1, False)
test_state_0[:, :, 0] = imutils.draw_centered_box(test_state_0[:, :, 0], 100, 1, False)
print '\033[32m\tStarting Simulation\033[0m'

sim_0(test_state_0, 150, save)
if save:
    os.system(ani_cmd)
    os.system(clean)
