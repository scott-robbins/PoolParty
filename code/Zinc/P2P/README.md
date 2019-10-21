# < ZINC_P2P >
This is my own attempt at creating a P2P Cloud Database on LAN with a growing fleet of 
raspberry pi's. This is an ongoing project, as I think of more modular/flexible designs
I'm refactoring/reorganizing the code. 

So Far it works like this. Running `python cloud.py ` will look for a Shared/ folder in your
local installation at ../PoolParty/code/Zinc/P2P. If there is no shared folder you will have 
an initial opportunity to populate it with files (through your native File Explorer UI).

After that, the program gets to work creating a dictionary with each file name and it's 
associated sha256 hash sum. The sums and are then converted to integer numbers. Looking at the 
list of nodes added to network (more on this), the sums are binned based on a linear range
defined by the minimum hash number and maximum hash number. 

The result is a fairly even distribution of file hashes per node, which will dynamically 
rescale bin sizes (and load on each node) as more nodes are added to the network!  

Here is an example of searching for a file once the Shared folder has been indexed and
distributed among available peers.

![search](https://raw.githubusercontent.com/scott-robbins/PoolParty/master/code/Zinc/P2P/distributed_file_search.png)
