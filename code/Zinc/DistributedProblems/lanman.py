from multiprocessing.pool import ThreadPool
from threading import Thread
import numpy as np
import utils 
import time 
import sys 
import os

# To minimize extra outputs to console you can add exceptions here and 
# They won't be displayed as part of the rogue IP detection/tracking
exceptions = ['localhost', 'Fios_Quantum_Gateway', 'fios-router', os.uname()[1]]


def create_logfile(verbose):
    date, localtime = utils.create_timestamp()
    log_data = '< LAN MONITOR STARTED > \t%s - %s' % (date, localtime)
    log_date = date.split('/')[0]+date.split('/')[1]+date.split('/')[2]
    log_time = localtime.split(':')[0]+localtime.split(':')[1] + localtime.split(':')[2]
    log_name = 'LOG_' + log_date + '_' + log_time + '.txt'
    open(log_name,'w').write(log_data+'\n')
    if verbose:
        print '\033[1m'+log_data+'\033[0m'
    return log_name, date, localtime


def start_nx_listener(iface, logfile):
    cmd = 'sudo tcpdump -i %s >> %s' % (iface, logfile)
    print 'Executing: %s' % cmd
    os.system(cmd)


def parse_logs(logfile, verbose):
    cnxs = []
    arps = {'requests': [], 'replies': []}
    file_in = logfile
    for line in utils.swap(file_in, False):
        tstamp = line.split(' ')[0]
        try: # IP Protocol Packets
            IP = line.split('IP')[1].split(' > ')[0]
            cnxs.append([tstamp, IP])
            print IP
            if verbose:
                print '[%s]\t%s' % (tstamp, IP)
        except IndexError:
            pass
        try: # Find ARP (Requests/Replies)
            ARP = line.split('ARP')[1].split(', length')[0]
            print ARP
            if ARP.split(' ')[0]=='Request':
                arps['requests'].append([tstamp, ARP])
                if verbose:
                    print '\033[33m\033[1m[%s]\t%s\033[0m' % (tstamp, ARP)
            else:
                arps['replies'].append([tstamp, ARP])
                if verbose:
                    print '\033[32m\033[1m[%s]\t%s\033[0m' % (tstamp, ARP)
        except IndexError:
            pass
    print '%d Network Connections Logged' % len(cnxs)
    print '%d ARP Requests Logged' % len(arps['requests'])
    print '%d ARP Replies Logged' % len(arps['replies'])
    print '[==========================================================]'
    return cnxs, arps


def run(iface, duration, logfile, verbose):
    tic = time.time()
    conxs = {}

    ''' Start the Packet Capture Parser Thread BEFORE network listener'''
    pool = ThreadPool(processes=1)

    '''  Start the Network Listener  '''
    p = Thread(target=start_nx_listener, args=(iface, logfile))
    p.daemon = True
    p.start()

    while (time.time() - tic) <= duration:
        dt = time.time() - tic
        try:
            if dt > 0 and dt % 5 == 0:
                async_read = pool.apply_async(parse_logs, (logfile, verbose))
                conxs, ARPs = async_read.get()
        except KeyboardInterrupt:
            print '\033[1m\033[31m[!] KILLED [%ss Elapsed]\033[0m' % \
                  str(time.time()-tic)
    kill_daemon = "ps aux | grep 'tcpdump' | cut -b 10-16 |" \
                  "while read proc; do kill -9 $proc > /dev/null;done"
    os.system(kill_daemon)
    return conxs, ARPs


def dump_traffic(traffic):
    unknown_hosts = []
    display = ''
    for data in traffic:
        flagged = False
        for e in exceptions:
            if len(data[1].split(e)) > 1:
                flagged = True
        if not flagged:
            display += data[1] + '\n'
            unknown_hosts.append(data[1])
    print '%d unique IPs observed:' % len(np.unique(unknown_hosts))
    print display
    return unknown_hosts


def discover_niface():
    cmd = 'ls /sys/class/net/ | while read n; do ifconfig | grep $n: >> ifaces.txt; done'
    os.system(cmd)
    iface = ''.replace(' ', '')
    for line in utils.swap('ifaces.txt', True):
        if ('RUNNING' in line.split(',')) and ('BROADCAST' in line.split(',')):
            iface = line.split(':')[0]
    return iface


if __name__ == '__main__':
    DEBUG = False
    log, date, localtime = create_logfile(DEBUG)

    iface = discover_niface()
    traffic, arps = run(iface, 10, log, DEBUG)

    ''' Show Summary of Monitoring Session'''
    os.system('clear')
    unknown_hosts = dump_traffic(traffic)

    ''' Analyze/Record traffic, Monitor ARPs, and Track unknown hosts  '''


# EOF
