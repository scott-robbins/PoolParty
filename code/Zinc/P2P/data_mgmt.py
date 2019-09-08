import numpy as np
import utils
import time
import os

tic = time.time()


def print_table_distribution(hashtable):
    buckets = hashtable.keys()
    total = 0
    for bin in buckets:
        print '%d elements in bin %d' % (len(hashtable[bin]), bin)
        total += len(hashtable[bin])
    return total


if __name__ == '__main__':
    if not os.path.isdir('Shared'):
        print '[*] Creating Shared-Sync Folder'
        os.mkdir('Shared')
    if not os.path.isfile('shared_files.txt'):
        # Catalogue all files in shared folder structure
        shared_data, hashes = utils.crawl_dir('Shared', True, True)
        print '[*] %d Directories Read' % len(shared_data['dir'])
        print '[*] %d Files Indexed' % len(shared_data['file'])
        # LOG Hashes to determine allocation among nodes
        content = ''
        for file_name in hashes.keys():
            uid = hashes[file_name]
            content += file_name + ' : ' + uid + '\n'
        open('shared_files.txt', 'w').write(content)
        os.system('clear')

    ''' Determine how to distribute shared data '''
    N_Nodes = len(utils.prs)
    hash_map = {}
    hash_range = []
    for line in utils.swap('shared_files.txt', False):
        try:
            hash = int(line.split(' : ')[1],16)/1.
            file_name = str(line.split(' : ')[0])
            hash_map[file_name] = hash
            hash_range.append(hash)
        except:
            pass
    minima = np.array(hash_range).min()
    maxima = np.array(hash_range).max()
    hash_domain = np.linspace(minima, maxima, N_Nodes+1)
    print 'MIN: %d' % (minima)
    print 'MAX: %d' % (maxima)
    print 'HashMap Ex: %s %s' % (str(hash_map.keys().pop()),str(hash_map.values().pop()))
    print '\n==== DISTRIBUTION TABLE ===='
    print hash_domain
    print '\033[31m\033[1mFINISHED\t[%ss Elapsed]\033[0m' % str(time.time()-tic)

    bins = {}
    for n in range(N_Nodes):
        bins[n] = list()
    for hval in hash_map.keys():
        val = hash_map[hval]
        if hash_domain[0] <= int(val) <= hash_domain[1]:
            bins[0].append(hval)
        if hash_domain[1] < int(val) <= hash_domain[2]:
            bins[1].append(hval)
        if hash_domain[2] <= int(val) < hash_domain[3]:
            bins[2].append(hval)
    total_files = print_table_distribution(bins)
    print 'Distributing %d Files to %d Peers' % (total_files, N_Nodes)

    ''' Make Records, and then distribute files accordingsly '''
    for node in bins.keys():
        file_list = bins[node]
        fname = 'node%d.txt' % node
        open(fname, 'w')
        os.system('mkdir ARCHIVE')
        ii = 0
        for f in file_list:
            cp = 'cp %s ARCHIVE/' % f
            os.system(cp)
            open(fname, 'a').write(f+'\n')

        os.system('tar -zcvf archive.tar.gz ARCHIVE/ ')
        utils.send_file(os.getcwd()+'/',utils.prs[node],'archive.tar.gz')
        os.system('rm archive.tar.gz; ls ARCHIVE/ | while read n; do rm ARCHIVE/$n; done; rmdir ARCHIVE')
    print 'FINISHED Distributing Files to Peers [%ss Elapsed]' % str(time.time()-tic)

