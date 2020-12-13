from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
import socket
import utils
import time
import sys
import os


def ephemeral_keygen(verbose):
    have_pk = False
    if not os.path.isfile('key.pem'):
        pk = utils.generate_private_key('key.pem')
        have_pk = True
    if not os.path.isfile('tmp.pem'):
        if not have_pk:
            pk = utils.generate_private_key('key.pem')
        pbk = utils.generate_public_key(pk, 'tmp.pem')

    else:
        pbk = utils.load_key('tmp.pem')

    if verbose:
        print '[*]\tPrivate Key Generated\t [%d Bytes]' % (pk.size() + 1)
        print '[*]\tPublic Key Generated\t [%d Bytes]' % (pbk.size() + 1)
    # os.remove('tmp.pem'); os.remove('key.pem')
    return pbk


def send_key(pbk, peer, port):
    if os.path.isfile('key.pem'):
        data = ''
        for line in utils.swap('key.pem',False):
            data += line + '\n'
    else:
        print '[!!] No Public Key to Send.'
        return -2

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((peer, port))
        s.send(data)
        reply = s.recv(1024)
        if len(reply) > 1:
            print reply
        s.close()
    except socket.error:
        print '[!!] Connection Error'
        reply = -1
        s.close()
    return reply


def recv_peers_key(peer, port):
    pfile = peer.replace('.', '')+'.pem'
    os.system('nc -l %d >> peer' % (pfile, port))


def recv_remote_keyfile(port, timeout):
    if os.path.isfile('tmp.pem'):
        session_key = utils.load_key('tmp.pem')
    else:
        print '[!!] No Session Key Loaded. Cannot create a secure connection.'
        return -2
    pubkey = ''
    for line in utils.swap('tmp.pem', False):
        pubkey += line
    try:
        # Start Listening Endpoint
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', port))
        s.settimeout(timeout)
        s.listen(timeout)

        # Initiate a connection
        client, addr = s.accept()
        print '[*] Connection - %s:%s' % (client.getpeername()[0], str(addr[1]))
        # Send client server side session eky
        sessKeyFile = addr[0].replace('.', '')+'.pem'
        # Get the client's session token
        session_token = client.recv(1024)
        open(sessKeyFile,'w').write(session_token)
        print '[*] Client Session Key Received'
        client.close()
        s.close()

    except socket.error:
        print '[!!] Connection Error'
        return -1


def create_secure_handshake(peer):
    secured = False
    content = 'HELLO'
    for element in list(get_random_bytes(8)):
        content += element
    pbkey = utils.load_key('key.pem')
    # Use RSA key to encrypt secret and send it
    secret = pbkey.encrypt(content, 1)
    pbkey.decrypt(secret)
    # Determine Known Peers and see if given peer is known
    local_files = os.listdir(os.getcwd())
    if peer in utils.prs or (peer.replace('.','')+'.pem') in local_files:
        print '[*] %s is a known Peer' % peer
    # If so make connection
    while not secured:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((peer, 41414))
            s.send(secret[0])
            reply = s.recv(1024)
            if reply == content:
                print '[*] Secure Handshake Success [1/2]'
                s.send(pbkey.encrypt('SUCCESS', 2)[0])
                s.close()
                secured = True
        except socket.error:
            print '[!!] Connect \033[1mBROKEN\033[0m with %s' % peer
            return 0

    ''' ^^ OUTBOUND TRAFFIC TO PEER HAS BEEN SECURED [1/2] ^^'''
    # Other end will do the same (you receive their encrypted secret)
    # Use each others keys to decrypt nonce secret and reply w. decrypted answers
    # Append the actual messages to replies, and if the secret is correct
    # Read the message (cut down on # of cnx/packets total!)


def secret_listener(timeout):
    data = []
    tic = time.time()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', 41414))
        s.listen(5)
        while time.time() - tic < timeout:
            client, addr = s.accept()
            print '[*] %s Has Connected' % addr[0]
            query = client.recv(1024)
            result, client = decode_secret(query, client)
            print '[*] Query Decoded into:\n %s' % result
            client.send(result)
            ackd, client = decode_secret(client.recv(1024), client)
            if 'SUCCESS' in ackd.split('SUCCESS')[0]:
                print ackd
                client.send('TRUE')
    except socket:
        s.close()
        print 'Connection Broken!'
        return data
    s.close()


def decode_secret(data_in, peer):
    ip = peer.getpeername()[0]
    keyfilename = ip.replace('.', '') + '.pem'
    print 'Decoding with %s' % keyfilename
    rmt_pbk = utils.load_key(keyfilename)
    reply = rmt_pbk.decrypt(data_in)
    return reply, peer


'''                 ______<(|[ MAIN ]|)>______                '''
verb = True
if 'keygen' in sys.argv:
    public_key = ephemeral_keygen(verbose=verb)

if 'send_pub_key' in sys.argv:
    send_key(ephemeral_keygen(False), sys.argv[2], 6666)

if 'rcv_key' in sys.argv:
    recv_peers_key(6666, 5)

if 'listen' in sys.argv:
    secret_listener(30)

if 'hello' in sys.argv:
    rmt = sys.argv[2]
    create_secure_handshake(rmt)

# create_secure_handshake('192.168.1.200')

# EOF
