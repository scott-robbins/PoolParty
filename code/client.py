import utils
import time
import sys
import os

tic = time.time()
IP = utils.cmd('ifconfig | grep broadcast | cut -b 14-28').replace('\n','').replace(' ','')

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
        result = utils.ssh_command(host, uname, pw, comp_bench, False)
        print result

if 'update_all' in sys.argv:
    update_all(True)

if 'send' in sys.argv and len(sys.argv) == 4:
    peer = sys.argv[2]
    file_in = sys.argv[3]
    bytes_sent, time_elapsed = utils.send_file('~/Desktop/RAXion/code', peer, file_in)

if 'cmd' in sys.argv:
    peer = sys.argv[2]
    cmd  = sys.argv[3]
    name = names[peer] # TODO: Can raise error if unknown peer
    pwrd = utils.retrieve_credentials(peer)
    utils.ssh_command(peer,name,pwrd,cmd,True)

if 'get' in sys.argv:
    peer = sys.argv[2]
    remote_file = sys.argv[3]
    bytes_recvd, time_spent = utils.get_file('~/Desktop/RAXion/code',IP,peer,remote_file)

