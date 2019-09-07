import utils
import time
import os
tic = time.time()


if __name__ == '__main__':
    if not os.path.isdir('Shared'):
        print '[*] Creating Shared-Sync Folder'
        os.mkdir('Shared')
    else:   # Initialize the shared database of files
        if not os.path.isfile('shared_files.txt'):
            # Catalogue all files in shared folder structure
            shared_data, hashes = utils.crawl_dir('Shared', True, True)
            print '[*] %d Directories Read' % len(shared_data['dir'])
            print '[*] %d Files Indexed' % len(shared_data['file'])
        # LOG Hashes to determine allocation among nodes
        content = ''
        for file_name in hashes.keys():
            uid = hashes[file_name]
            content += file_name + ' ' + uid + '\n'
        open('shared_files.txt', 'w').write(content)
    print '\033[31m\033[1m%ss Elapsed]\033[0m' % str(time.time()-tic)