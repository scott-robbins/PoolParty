# <: *ZINC* :>
#### *A DIY P2P File Sharing Network* 
This is not a robust software, it's a small project for me
to teach myself some fundamentals. However, if you find anything
here useful feel free to use/download however you want!
 
I'm always looking to learn, so if you want to contribute or give
feedback feel free to email me at tyl3r5durd3n@protonmail.com or 
make a pull request. 

# Setup
Zinc is written for POSIX/LINUX operating systems, as it relies 
pretty heavily on low level networking functions that I'm not sure
if/how one implements on windows (netcat, ssh, sftp, raw sockets, etc.)

Clone the repo

`` git clone https://github.com/scott-robbins/PoolParty``

Add Peers (Machines you want to share files with)

``PoolParty/code$ python engine.py add ``

## File Sharing 
First we want to create a folder of shared resources that all registered
peers can synchronize with. To do this, locally create folder in the 
directory where you've installed Zinc called 'Shared'.

By running a DFS through this Shared Folder file structure, the first part
of synchronization will be to link a hash of every file with it's name. 
Once we have the complete set, or rather for every instance we see a complete
set, of files in the shared folder we can determine how to allocate them among
peers. 

## Distributed Computing 
I want to run a task as fast as possible. I have multiple machines who can
communicate at relatively quick speeds with pretty solid bandwidth. 

Can I find a way to achieve a task FASTER with this network, than with my single machine?
Let's find out!

#### [1] More Basic Problem(s) [Many Operations in Sequence - linear time scaling?]: 
   
    * the hash of every word in a fairly large dictionary? or every file in a shared folder?
    
    * doing a large loop of any operation where the next step doesn't depend on the previous step
#### [2] Somewhat hard Problem(s) [Single Process based on sequential operations]:
    
    * Processing a single object like a video in a frame by frame fashion
    
    * Analyzing a single song to generate a spectrogram or animated FFT

#### [3] Challenging to Make Parallel, and Challenging generally [Many operations which depend on the results of iterations]:
    
    * Computing a simulation and saving frames to a single video file
    
    * Solving an optimization of a single problem across nodes (find shortest path between
      a LARGE set of given verts and edges) 