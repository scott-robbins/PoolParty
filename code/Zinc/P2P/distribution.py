from multiprocessing.pool import ThreadPool
from threading import Thread
import numpy as np
import utils
import time
import sys
import os

tic = time.time()
DEBUG = True


def load_hashes():
    file_hashes = {}
    lookup = {}
    if os.path.isfile('sharedfiles.txt'):
        for line in utils.swap('sharedfiles.txt', False):
            file_name = line.split(' : ')[0]
            file_hash = line.split(' : ')[1]
            file_hashes[int(file_hash, 32)] = file_name
            lookup[file_name] = int(file_hash, 32)
    hash_nums = np.array(file_hashes.keys())
    minima = hash_nums.min()
    maxima = hash_nums.max()

    if DEBUG:
        print '%d Hashes Total' % len(file_hashes.values())
        print 'HashMax: %d' % maxima
        print 'HashMin: %d' % minima
    return hash_nums, minima, maxima, file_hashes, lookup


def build_distributed_hashtable(nodes):
    # Load Hashes of Shared Files
    hashes, minimum, maximum, table, lut = load_hashes()
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
    total_sorted = 0
    for k in hash_table.keys():
        total_sorted += len(hash_table[k])
    print '[*] %d Files Sorted into %d Bins [%d Files Given]' %\
          (total_sorted, len(hash_table.keys()), len(hashes))
    return hash_table, table, lut


def create_manifest(ip, hashes, table):
    manifest = ''
    file_name = ip.replace('.', '') + '.txt'
    for h in hashes[ip]:
        manifest += str(h) + ' : '+table[h]+'\n'
    open(file_name, 'a').write(manifest)
    return file_name, os.path.isfile(file_name)


def compress_and_send(file_list, distributed_hash_table, table_keys, key):
    ipid = file_list.split('.')[0]
    os.mkdir(ipid)
    for file_name in distributed_hash_table[key]:
        fid = table_keys[file_name].replace('"', '')
        if os.name == ('posix' or 'unix'):
            os.system('cp %s %s/' % (fid, ipid))
    if os.name == ('posix' or 'unix'):
        os.system('zip archive'+ipid+'.zip --quiet -r %s' % ipid)
        arch = 'rm %s; ls %s | while read n; do rm %s/$n; done; rm -rf %s' % \
               (file_list, ipid, ipid, ipid)
        os.system(arch)
        utils.send_file('/tmp/Shared', key, 'archive.zip')
        os.remove('archive'+ipid+'.zip')


def distribute_resources(distributed_hash_table, table_keys):
    pool = ThreadPool(processes=3)
    for key in distributed_hash_table:
        has_table = False
        file_list, status = create_manifest(key,distributed_hash_table, table_keys)
        if status:
            if key != utils.get_local_ip():
                reply = utils.ssh_command(key, utils.names[key],
                                  utils.retrieve_credentials(key),
                                  'ls -la /tmp/Shared/%s' % file_list,False).replace('\n', '')
                try:
                    file_size = int(reply.split(' ')[4])
                    if os.path.getsize(file_list) == file_size and file_size>0:
                        print '%s Already Has HashTable' % key
                        has_table = True
                    else:
                        print file_size
                        print os.path.getsize(file_list)
                        print file_list
                except IndexError:
                    pass
                if not has_table:
                    utils.ssh_command(key, utils.names[key],
                                      utils.retrieve_credentials(key),
                                      'mkdir /tmp/Shared', False)
                    utils.send_file('/tmp/Shared', key, file_list)
                os.remove(file_list)
                pool.apply_async(compress_and_send, (file_list, distributed_hash_table, table_keys, key))


if __name__ == '__main__':
    # Load Hashes of Shared Files
    hs, mini, maxi = load_hashes()
