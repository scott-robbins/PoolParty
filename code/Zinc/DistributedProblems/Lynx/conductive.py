from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
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


def send_public_key(pbk, peer, port):
    reply = ''
    if os.path.isfile('tmp.pem'):
        data = ''
        for line in utils.swap('tmp.pem',False):
            data += line
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


if 'keygen' in sys.argv:
    public_key = ephemeral_keygen(False)

if 'send_pub_key' in sys.argv:
    send_public_key(ephemeral_keygen(False), sys.argv[2], 6666)

if 'rcv_key' in sys.argv:
    recv_peers_key(6666, 5)
