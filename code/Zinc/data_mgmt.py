import utils
import time
import os
tic = time.time()


if __name__ == '__main__':
    if not os.path.isdir('Shared'):
        print '[*] Creating Shared-Sync Folder'
        os.mkdir('Shared')
    else:
        # TODO: Catalogue all files in shared folder structure
        shared_data, file_ids = utils.crawl_dir('Shared', True)
        file_tracker = {}
        print '[*] %d Directories Read' % len(shared_data['dir'])
        print '[*] %d Files Indexed' % len(file_ids)
    print '[%ss Elapsed]' % str(time.time()-tic)