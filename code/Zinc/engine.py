import utils
import sys
import os

peers = []
names = {}


def add_peers():
    if raw_input('Would you like to add Peers Now(y/n)?: ').upper()=='Y':
        adding = True
        while adding:
            peer = raw_input('Enter IP: ')
            hname = raw_input('Enter Hostname: ')
            pw = 'Result: '+raw_input('Enter Password: ')  # TODO: black out tty
            file_name = peer.replace('.', '') + '.txt'
            key_file = peer.replace('.', '') + '.key'
            os.system('python aes.py -e %s' % pw)
            os.system('mv encrypted.txt KEYS/%s' % file_name)
            os.system('mv key.txt KEYS/%s' % key_file)
            if hname not in utils.names:
                names[peer] = hname
                peers.append(peer)
            print '============================='

            if raw_input('Add More (y/n)?: ').upper() != 'Y':
                adding = False
            print 'Added the Following Peers: '
            for p in peers:
                print '[*] %s' % p


if os.path.isdir('KEYS/'):
    print ''
else:
    print 'You Have NO Peers Registered Yet.'
    os.mkdir('KEYS/')

add_peers()
