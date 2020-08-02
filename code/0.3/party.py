import control 
import setup 
import utils 
import time 
import sys
import os 


# Need to define peers in different classes of worker. Different machines have different levels of connectivity, 
# will be sitting in different network topologies, and have different levels of computational power. Utilizng nodes
# effecively will require knowing this about each peer and organizing their coordination around these profiles. 
