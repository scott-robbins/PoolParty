from multiprocessing.pool import ThreadPool
from threading import Thread
import numpy as np
import utils
import time
import sys
import os

tic = time.time()
file_hashes = {}
DEBUG = True


def load_hashes():
    if os.path.isfile('sharedfiles.txt'):
        for line in utils.swap('sharedfiles.txt', False):
            file_name = line.split(' : ')[0]
            file_hash = line.split(' : ')[1]
            file_hashes[int(file_hash, 32)] = file_name

    hash_nums = np.array(file_hashes.keys())
    minima = hash_nums.min()
    maxima = hash_nums.max()

    if DEBUG:
        print '%d Hashes Total' % len(file_hashes.values())
        print 'HashMax: %d' % maxima
        print 'HashMin: %d' % minima
    return hash_nums, minima, maxima, file_hashes


def build_distributed_hashtable(nodes):
    # Load Hashes of Shared Files
    hashes, minimum, maximum, table = load_hashes()
    buckets = np.linspace(minimum, maximum, len(nodes))

    delta = np.diff(buckets)[0]
    hash_table = {}
    distributor = {}
    for b in buckets:
        distributor[b] = nodes.pop()
        hash_table[distributor[b]] = list()
    for value in hashes:
        for bin in buckets:
            if bin-delta/2 <= value <= bin +delta/2:
                hash_table[distributor[bin]].append(value)
    print hash_table.keys()
    total_sorted = 0
    for k in hash_table.keys():
        total_sorted += len(hash_table[k])
    print '%d Files Sorted into %d Bins [%d Files Given]' %\
          (total_sorted, len(hash_table.keys()), len(hashes))
    return hash_table, table


def create_manifest(ip, hashes, table):
    manifest = ''
    file_name = ip.replace('.', '') + '.txt'
    for h in hashes[ip]:
        manifest += str(h) + ' : '+table[h]+'\n'
    open(file_name, 'a').write(manifest)
    return file_name, os.path.isfile(file_name)


def distribute_resources(distributed_hash_table, table_keys):
    for key in distributed_hash_table:
        print 'Sending %s %d Files' % (key, len(distributed_hash_table[key]))
        file_list, status = create_manifest(key,distributed_hash_table, table_keys)
        if status:
            if key != utils.get_local_ip():
                print 'Distributing...'
                utils.ssh_command(key, utils.names[key],
                                  utils.retrieve_credentials(key),
                                  'mkdir /tmp/Shared',False)
                utils.send_file('/tmp/Shared', key, file_list)


if __name__ == '__main__':
    # Load Hashes of Shared Files
    hs, mini, maxi = load_hashes()
