import utils
import time
import sys
import os

tic = time.time()

peers = utils.prs
names = utils.names

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

for host in peers:
    uname = names[host]
    pw = utils.retrieve_credentials(host)
    comp_bench = 'python client.py bench_compute 500'
    utils.ssh_command(host,uname,pw,comp_bench,True)

if 'bench_compute' in sys.argv and len(sys.argv) >= 2:
    N = int(sys.argv[2])
    result = 0
    for i in range(N):
        for j in range(N):
            if i > 0 and i % 3 == 0:
                result += 1
    print 'Result: %d\n%ss Elapsed' % (result, str(time.time()-tic))