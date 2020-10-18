from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
import base64
import utils
import sys
import os


def which_nodes(ip_address):
    if not os.path.isdir('Pool'):
        print '[!!] No POOL Created...'
        exit()
    substr = ip_address.replace('.', '')
    os.system('ls Pool/*.key >> keys.txt')
    keys = utils.swap('keys.txt', True)
    for line in keys:
        name = line.split('/')[1].split('.')[0]
        if len(name.split(substr)) > 1:
            return line.split('/')[1]


def register_node():
    """
    Log the information/credentials for a peer to it's own unique file.
    This function will create a local directory for storing credentials,
    if one is not present already.
    :return:
    """
    name = raw_input('Enter Name: \n')
    ip = raw_input('Enter IP Address: \n')
    passwd = raw_input('Enter Password:\n')
    credentials = '%s@%s:%s' % (name, ip, passwd)
    if not os.path.isdir('Pool'):
        os.mkdir('Pool')

    node_file = 'Pool/' + name + ip.replace('.','') +'.pool'
    key_file = 'Pool/'  + name + ip.replace('.','') + '.key'

    if os.path.isfile(node_file):
        if raw_input('%s Already Exists. Overwrite? (y/n):\n').upper() == ('Y' or 'YES'):
            os.remove(node_file)
            try:
                os.remove(key_file)
            except OSError:
                pass
    # Encrypt the data and write to file
    key = get_random_bytes(32)
    cipher = AES.new(key)
    open(node_file, 'wb').write(utils.EncodeAES(cipher, credentials))
    open(key_file, 'wb').write(base64.b64encode(key))
    return node_file, key


def load_credentials(name, ip):
    """
    Given a hostname and IP, load the encrypted credentials for that machine.
    If the files are not present the function gives an error and exits.
    :param name:
    :param ip:
    :return:
    """
    # Make sure everything is present to decrypt credentials
    if not os.path.isdir('Pool'):
        print '[!!] No POOL Created...'
        exit()
    node_file_name = 'Pool/' + name + ip.replace('.','') + '.pool'
    node_key_file = 'Pool/' + name + ip.replace('.','') + '.key'
    if not os.path.isfile(node_file_name) or not os.path.isfile(node_key_file):
        print '[!!] No Credentials Found for %s...' % name
        exit()
    # Initialize Crypto Objects
    cipher = AES.new(base64.b64decode(open(node_key_file, 'rb').read()))
    # Load Credentials
    raw_data = utils.DecodeAES(cipher, open(node_file_name, 'rb').read())
    # Parse the Data
    name = raw_data.split('@')[0]
    try:
        ip = raw_data.split(':')[0].split('@')[1]
        passwd = raw_data.split(':')[1]
    except IndexError:
        print '[!!] Failed to Load Credentials for %s' % name
        exit()
    return {'name': name, 'ip': ip, 'password': passwd}


def quick_load(k, c):
    try:
        # Initialize Cipher
        cipher = AES.new(base64.b64decode(open('Pool/' + k, 'rb').read()))
        # Load Encrypted Data
        raw_data = utils.DecodeAES(cipher, open('Pool/' + c, 'rb').read())
    except IOError:
        print '[!!] Unable to load Credentials from %s' % k
        exit()

    try:    # Parse Data s
        name = raw_data.split('@')[0]
        ip = raw_data.split(':')[0].split('@')[1]
        passwd = raw_data.split(':')[1]
    except IndexError:
        print '[!!] Failed to Load Credentials for %s' % name
        exit()
    return {'name': name, 'ip': ip, 'password': passwd}


if __name__ == '__main__':
    if 'add' in sys.argv:
        register_node()

    if 'cmd' in sys.argv and len(sys.argv) >= 3:
        if len(sys.argv[2].split('.'))>=3:
            ip = sys.argv[2]
            ip_str = ip.replace('.', '')
            os.system('ls Pool | grep %s >> files.txt' % ip_str)
            creds = utils.swap('files.txt', True)
            if len(creds) == 2:
                if 'key' in creds[0].split('.'):
                    key_file = creds[0]
                    cred_file = creds[1]
                else:
                    key_file = creds[1]
                    cred_file = creds[0]
            else:
                print '[!!] More than one Peer has registered with IP %s...' % ip

            hostname = key_file.split(ip.replace('.',''))[0]
            credentials = load_credentials(hostname, ip)
        else:
            name = sys.argv[2]
            # Make sure there is only ONE node with this name,
            # Otherwise tell user they must be more specific (use IP instead)
            os.system('ls Pool | grep %s >> files.txt' % name)
            creds = utils.swap('files.txt', True)
            if len(creds) == 2:
                if 'key' in creds[0].split('.'):
                    key_file = creds[0]
                    cred_file = creds[1]
                else:
                    key_file = creds[1]
                    cred_file = creds[0]
            else:
                print '[!!] More than one Peer has registered with Hostname %s...' % name
            credentials = quick_load(key_file, cred_file)

        if len(sys.argv) >= 4:
            CMD = utils.arr2str(sys.argv[3:])

            # EXECUTE COMMAND
            ip = credentials['ip']
            hostname = credentials['name']
            password = credentials['password']
            output = utils.ssh_command(ip, hostname, password, CMD, True)

    if 'destroy_keys' in sys.argv and os.path.isdir('Pool/'):
        os.system('rm -rf Pool/')
