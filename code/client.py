import utils
import time
import sys
import os

tic = time.time()

peers = utils.prs
names = utils.names


def update_all(verbose):
    for host in peers:
        name = names[host]
        pwrd = utils.retrieve_credentials(host)
        cmd = 'cd ~/Desktop/RAXion; sudo git pull origin'
        utils.ssh_command(host,name,pwrd,cmd,verbose)


''' RAXION Distributed Computing Architecture: 

_________ - (3) Machine Types - __________
[1] Master [Single instance]
    - Command and Control Device 
[2] Planner/Delegator(s)
    - Best Network Speeds 
[3] Worker(s)
    - Best Computing speeds 
==========================================
'''

if 'init' in sys.argv:
    for host in peers:
        uname = names[host]
        pw = utils.retrieve_credentials(host)
        comp_bench = 'cd ~/Desktop/RAXion/code; python compbench.py'
        utils.ssh_command(host, uname, pw, comp_bench, True)

if 'update_all' in sys.argv:
    update_all()

