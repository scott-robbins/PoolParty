import utils
import time
import sys
import os

tic = time.time()


class Cloud:
    files = {}
    n_nodes = 0
    nodes = utils.names

    def __init__(self):
        self.initialize()

    def initialize(self):
        if not os.path.isdir('Shared'):
            os.mkdir('Shared')
            if os.name == 'nt':
                os.system('explorer .')
            elif os.name == 'posix':
                os.system('nautilus .')
            elif os.name == 'unix':
                os.system('open .')
        if not os.path.isfile('sharedfiles.txt'):
            # Now Digest the files in Shared
            shared_data, hashes = utils.crawl_dir('Shared', hash=True, verbose=True)
            if os.name == 'posix':
                os.system('clear')
            if os.name == 'nt':
                os.system('cls')
            print '[*] %d Files Logged in Shared Folder  [%ss Elapsed]' % \
                  (len(hashes.keys()), str(time.time() - tic))

            hash_data = ''
            for file_name in hashes.keys():
                hash_data += file_name + ' : ' + hashes[file_name]+'\n'
            open('sharedfiles.txt', 'a').write(hash_data)
            self.files = hashes
        else:
            n_files = 0
            for line in utils.swap('sharedfiles.txt', False):
                file_name = line.split(' : ')[0]
                file_hash = line.split(' : ')[1]
                self.files[file_name] = file_hash
                n_files += 1
            print '[*] %d Files Logged in Shared Folder  [%ss Elapsed]' % \
                  (len(self.files.keys()), str(time.time() - tic))


if __name__ == '__main__':
    myCloud = Cloud()

