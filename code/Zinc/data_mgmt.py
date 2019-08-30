import utils
import os

if __name__ == '__main__':
    if not os.path.isdir('Shared'):
        print '[*] Creating Shared-Sync Folder'
        os.mkdir('Shared')
    else:
        # TODO: Catalogue all files in shared folder structure
        shared_data = utils.crawl_dir('Shared', False)
        print '%d Directories Added' % len(shared_data['dir'])
        print '%d Files Added' % len(shared_data['file'])
        