import utils
import time
import os
tic = time.time()


if __name__ == '__main__':
    if not os.path.isdir('Shared'):
        print '[*] Creating Shared-Sync Folder'
        os.mkdir('Shared')
    else:
        # Catalogue all files in shared folder structure
        shared_data, hashes = utils.crawl_dir('Shared', True, True)
        print '[*] %d Directories Read' % len(shared_data['dir'])
        print '[*] %d Files Indexed' % len(shared_data['dir'])
    print '[%ss Elapsed]' % str(time.time()-tic)