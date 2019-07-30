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
    Master = IP
    Delegators = ['192.168.1.229']
    Workers = ['192.168.1.217', '192.168.1.200']
    for host in peers:
        uname = names[host]
        pw = utils.retrieve_credentials(host)
        comp_bench = 'cd ~/Desktop/RAXion/code; python compbench.py'
        utils.ssh_command(host, uname, pw, comp_bench, False)
        utils.ssh_command(host, uname, pw, 'ping -c 1 1.1.1.1', False)
        # TODO Use Results to Determine Machines [2] and rest [3]
    for filename in os.listdir(os.getcwd()):
        if 'ion' in filename.split('.'):
            print '*\033[3m Configuration Model Found \033[0m\033[1m< %s >\033[0m' % filename
            # LOAD CONFIGURATION DATA
            raw_config = {'Master':'', 'Schedulers': [], 'Workers': [],
                          'Programs': []}
            for line in utils.swap(filename, False):
                try:
                    raw_config['Master'] = line.split('[1]: ')[1]    # Master Machine
                except IndexError:
                    pass
                try:
                    raw_config['Schedulers'] = line.split('[2]: ')[1].split(',')[:]    # Scheduler Machine(s)
                except IndexError:
                    pass
                try:
                    raw_config['Workers'] =line.split('[3]: ')[1].split(',')[:]    # Worker Machine(s)
                except IndexError:
                    pass
                try:
                    prog1 = line.split('\t<1>')[1].replace(' ','')    # Program 1?
                    raw_config['Programs'].append(prog1)
                except IndexError:
                    pass
                try:
                    prog2 = line.split('\t<2>')[1].replace(' ','')    # Program 1?
                    raw_config['Programs'].append(prog2)
                except IndexError:
                    pass
                try:
                    prog3 = line.split('\t<3>')[1].replace(' ','')    # Program 1?
                    raw_config['Programs'].append(prog3)
                except IndexError:
                    pass
                
            print '\nWorkers: %s' % raw_config['Workers']
            print 'Scheduler(s): %s' % raw_config['Schedulers']
            print 'Master Machine: %s' % raw_config['Master']
            print 'Programs In ION:'
            for prog in raw_config['Programs']:
                print '* %s ' % prog

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

