import numpy as np
import storage
import socket
import utils
import setup
import time
import sys
import os


class Node:
    # Need to define peers in different classes of worker. Different machines have different levels of connectivity,
    # will be sitting in different network topologies, and have different levels of computational power. Utilizng nodes
    # effecively will require knowing this about each peer and organizing their coordination around these profiles.
    TALKER = False
    ROUTER = False
    HOARDER = True
    WORKER = False      # node style (WORKER, TALKER, ROUTER, HOLDER, etc...)
    internal_ip = []    # Not all machines will only have one active adapter?
    external_ip = ''    # IP seen outisde of NAT
    cpu_rating = 0.0    # computational power rating
    trx_rating = 0.0    # network connectivity rating
    PEERS = []
    name = ''

    def __init__(self, nickname):
        self.name = nickname
        self.get_internal_addr()
        self.external_ip = utils.get_ext_ip().replace('$','').replace(' ','')
        if self.external_ip in self.internal_ip:
            self.ROUTER = True
        self.cpu_rating = self.test_cpu_power()

        # Choosing based on an arbistrary value of 100ms
        if self.cpu_rating < 0.1:
            self.WORKER = True
        self.initialize()

    def initialize(self):
        # Create Folder for Shared Data
        if not os.path.isdir(os.getcwd()+'/PoolData'):
            os.mkdir(os.getcwd()+'/PoolData')
        if not os.path.isdir(os.getcwd()+'/PoolData/Shares'):
            os.mkdir(os.getcwd()+'/PoolData/Shares')
            # create file for initializing peer list
            peers = os.getcwd()+'/PoolData/Shares/peerlist.txt'
            open(peers,'wb').write('%s\n' % self.name)
        else: # LOAD Shares and prep hashtables 
            local_shares = {}
            local_shares['files'] = os.listdir(os.getcwd()+'/PoolData/Shares')
            for sharefile in local_shares['files']:
                filehash = utils.get_sha256_sum(os.getcwd()+'/PoolData/Shares/'+sharefile,False)
                filesize = os.path.getsize(os.getcwd()+'/PoolData/Shares/'+sharefile)
                local_shares[sharefile] = {}
                local_shares[sharefile]['hash'] = filehash
                local_shares[sharefile]['size'] = filesize
            # this will be useful for quickly telling peer about what this node has
            print local_shares # FOR DEBUGGING 
        # Each node also has a folder for outputing data/messaging 
        if not os.path.isdir(os.getcwd()+'/PoolData/NX'):
            os.mkdir(os.getcwd()+'/PoolData/NX')
            open(os.getcwd()+'/PoolData/NX/requests.txt', 'wb').write('')
        # node is a worker it needs folder for  JOBS
        if self.WORKER:
            if not os.path.isdir(os.getcwd()+'/PoolData/Jobs'):
                os.mkdir(os.getcwd()+'/PoolData/Jobs')
        # indicate whether node needs peer creds for encrypted communication
        if not os.path.isdir(os.getcwd()+'/PoolData/Creds'):
            os.mkdir(os.getcwd()+'/PoolData/Creds')
            self.add_job_flag('? CREDS\n')

    def check_jobs(self):
        if not self.WORKER:
            return -1
        else:
            return len(utils.cmd('ls %s' % (os.getcwd()+'/PoolData/Jobs'), False))

    def get_internal_addr(self):
        addrs = utils.cmd('hostname -I',False).pop().split(' ')
        addrs.pop(-1)
        self.internal_ip = addrs

    def test_cpu_power(self):
        t0 = time.time()
        l0 = []
        l1 = 0
        for i in range(10000):
            l0.append(np.random.randint(0,1,1)[0])
        l0 = np.array(l0).reshape(100, 100)
        for i in range(99):
            l1 += np.array(l0[i,:]).sum()
        dt = time.time() - t0
        return dt

    def show(self):
        traits = {'TALKER': self.TALKER,
                  'ROUTER': self.ROUTER,
                  'HOARDER': self.HOARDER,
                  'WORKER': self.WORKER}
        ipstr = '\n'
        n = 1
        for addr in self.internal_ip:
            ipstr += '    [%d] %s\n' % (n, addr)
            n += 1
        result = '[* --- < Node Details > --- *]\n'
        result += '  - Internal IP(s): %s' % ipstr
        result += '  - External IP: %s\n' % self.external_ip
        result += '  - CPU Test Timing: %ss\n' % str(self.cpu_rating)
        for ability in traits:
            if traits[ability]:
                result += '  - Node is a %s\n' % ability
        return result

    def add_job_flag(self, flag_message):
        if os.path.isfile(os.getcwd()+'/PoolData/NX/requests.txt'):
            open(os.getcwd()+'/PoolData/NX/requests.txt', 'a').write(flag_message)
        else:
            open(os.getcwd()+'/PoolData/NX/requests.txt', 'wb').write(flag_message)

def main():
    if len(sys.argv) < 2:
        name = 'Test'
    else:
        name = sys.argv[1]
    node = Node('Test')
    if '-show' in sys.argv:
        print node.show()

    if '-dump_info' in sys.argv:
        open(os.getcwd()+'/PoolData/NX/self.txt', 'wb').write(node.show())

    if node.WORKER:
        JOB_LIMIT = 10
        # notify that it's available for jobs if none are present 
        active = node.check_jobs()
        if JOB_LIMIT > active >= 0: # TODO: What is the job limit?
            N = JOB_LIMIT - active
            node.add_job_flag('! Can take %d more jobs\n' % N) 

    if node.HOARDER:
        # Resynchronize Local Hashtable/Files 
        node.add_job_flag('? Files/Data\n')
    
    if node.ROUTER:
        has_routes = False
        # not only ping peers, but request from master ext ips of nodes too
        # even better would be to try and create a direct connection to test
        if os.path.isfile(os.getcwd()+'/PoolData/NX/nat.txt'):
            has_routes = True
        if not has_routes:
            # print '[*] Requesting Network Routing Info'
            node.add_job_flag('? NAT Info\n')



    


if __name__ == '__main__':
    main()

