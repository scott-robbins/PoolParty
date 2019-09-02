import numpy as np
import utils
import time
import sys
import os

peers = []
names = {}
tic = time.time()


def add_peers():
    if raw_input('Would you like to add Peers Now(y/n)?: ').upper()=='Y':
        adding = True
        while adding:
            peer = raw_input('Enter IP: ')
            hname = raw_input('Enter Hostname: ')
            pw = raw_input('Enter Password: ')  # TODO: black out tty
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


def test_connectivity():
    # Test Network Connectivity
    connections = {}
    for addr in utils.prs:
        connections[addr] = []
    print 'Testing Network Connectivity '
    for p in utils.prs:
        if p in utils.names.keys():
            uname = utils.names[p]
            utils.cmd('ls KEYS/*.txt | while read n; do echo $n >> peers.txt; done')
            print '\033[1m\033[35mTesting %s\033[0m' % p
            for n in utils.swap('peers.txt', True):
                name = 'KEYS/' + p.replace('.', '') + '.txt'
                if name == n:
                    pw = utils.retrieve_credentials(p)
                    for node in utils.prs:
                        if node != p:
                            cmd = 'ping -c 1 %s >> ping.txt' % node
                            utils.ssh_command(p, uname, pw, cmd, True)
                            utils.get_file_untrusted(p, uname, pw, '~/ping.txt', True)  # TODO: Breaks if false
                            utils.ssh_command(p, uname, pw, 'rm ~/ping.txt', False)
                            dt = []
                            for line in utils.swap('ping.txt', True):
                                try:
                                    dt.append(float(line.split('time=')[1].split(' ')[0]))
                                except:
                                    pass
                            try:
                                print '(%s->%s) %f ms' % (p, node, dt[0])
                                connections[p].append([node, dt[0]])
                            except IndexError:
                                pass
    os.system('clear')
    print '\033[36m\033[1m========= \033[0m\033[1mConnectivity \033[32m========= \033[0m'
    priority = {}
    # Find Best Connections
    for Node in connections.keys():
        timer = []
        links = {}
        if len(connections[Node]):
            for link in connections[Node]:
                endpt = link[0]
                delay = link[1]
                timer.append(delay)
                links[delay] = endpt
            best = np.array(links.keys()).min()
            fastest = links[best]
            priority[Node] = fastest
            print '%s -> %s is Fastest [%s ms]' % (Node, fastest, best)
    return priority, connections


def initialize():
    if os.path.isdir('KEYS/'):
        print ''
    else:
        print 'You Have NO Peers Registered Yet.'
        os.mkdir('KEYS/')
        add_peers()
    if 'add' in sys.argv:
        add_peers()


if __name__ == '__main__':
    ''' Initialize Keys and assorted things'''
    initialize()

    '''[1] Test Network Connectivity '''
    local_addr = utils.get_local_ip()
    user = os.getlogin()
    utils.prs.append(local_addr)
    # TODO: Multi-thread this to show effectiveness of parallel p2p processes
    #  because it takes about 30s looping through and sending p2p ping commands
    best_cnxs, p2p_links = test_connectivity()
    # Best Connections stored as <k:Sender>--<v:Receiver>
    # pairs that were found to be fastest
    # meant to indicate best links for future use

    '''[2] Check Shared Resources Folder and Synchronize '''
    if not os.path.isdir('Shared'):
        print '[*] Creating "Shared" Folder'
        os.mkdir('Shared')
        # TODO: Step User through adding files? Or explain it maybe?
    else:
        if os.path.isfile('shared_files.txt'):
            print '[*] Shared Resources Found'
        else:  # Crawl Through shared files and index them by sha256sum
            shared, hashes = utils.crawl_dir('Shared',True,True)
            content = ''
            os.system('touch shared_files.txt')  # Might not be needed but open sometimes fails
            for file_name in hashes.keys():
                uid = hashes[file_name].replace('\n', '').replace(' ','')+'\n'
                content += file_name+' : '+uid
            open('shared_files.txt', 'w').write(content)
    # Organize Files Found
    file_ids = {}
    id = 0
    for line in utils.swap('shared_files.txt', False):
        id += 1
        fid = line.split(' : ')[0].replace('"','')
        file_ids[fid] = (line.split(' : ')[1])

    print '%d Files in Shared Folder' % id

    # Check Peers for their shared folder contents
    find_shared = 'find -iname utils.py >> where.txt'
    install_paths = {}
    for node in best_cnxs.keys():
        uname = utils.names[node]
        utils.ssh_command(node,uname,utils.retrieve_credentials(node),find_shared,True)
        time.sleep(2) # Allow Remote machine some time to search for install location
        utils.get_file_untrusted(node,uname,utils.retrieve_credentials(node),'where.txt',True)
        os.system('cat where.txt | grep PoolParty/code | cut -b 3- >> loc.txt;cat loc.txt')
        utils.ssh_command(node, uname, utils.retrieve_credentials(node), 'rm where.txt', True)
        install_paths[node] = utils.swap('loc.txt', True).pop().replace('\n', '').replace(' ', '')
    os.system('clear')
    print install_paths
    # TODO: DEBUG TEST THIS LOCATION
    for m in best_cnxs.keys():
        uname = utils.names[m]
        test = 'cd %s; git pull origin' % install_paths[m].split('utils.py')[0]
        utils.ssh_command(m, uname, utils.retrieve_credentials(m), test, True)

print '\033[1m\033[31m[%ss Elapsed]\033[0m' % str(time.time()-tic)
