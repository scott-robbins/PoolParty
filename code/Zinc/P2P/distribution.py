import matplotlib.pyplot as plt
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
            file_hashes[file_name] = int(file_hash, 16)

    hash_nums = np.array(file_hashes.values())
    minima = hash_nums.min()
    maxima = hash_nums.max()

    if DEBUG:
        print '%d Hashes Total' % len(file_hashes.values())
        print 'HashMax: %d' % maxima
        print 'HashMin: %d' % minima
    return hash_nums, minima, maxima


def build_distributed_hashtable(nodes):
    # Load Hashes of Shared Files
    hashes, minimum, maximum = load_hashes()
    buckets = np.linspace(minimum, maximum, len(nodes))
    delta = np.diff(buckets)[0]
    hash_table = {}
    for b in buckets:
        hash_table[b] = list()
    for value in hashes:
        for bin in buckets:
            if bin-delta/2 <= value <= bin +delta/2:
                hash_table[bin].append(value)
    print hash_table.keys()
    total_sorted = 0
    for k in hash_table.keys():
        total_sorted += len(hash_table[k])
    print '%d Files Sorted into %d Bins [%d Files Given]' %\
          (total_sorted, len(nodes), len(hashes))


if __name__ == '__main__':
    # Load Hashes of Shared Files
    hs, mini, maxi = load_hashes()
