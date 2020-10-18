from Crypto.Cipher import AES
import base64
import sys
import os


def swap(fname, destroy):
    data = []
    [data.append(line) for line in open(fname, 'r').readlines()]
    if destroy:
        os.remove(fname)
    return data


# the block size for the cipher object; must be 16 per FIPS-197
BLOCK_SIZE = 16
PADDING = '{'

pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING        # pad the text to be encrypted


EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))            # encrypt with AES, encode with base64
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

if '-e' in sys.argv:
    secret = os.urandom(BLOCK_SIZE)             # generate a random secret key
    cipher = AES.new(secret)                    # create a cipher object using the random secret
    encoded = EncodeAES(cipher, sys.argv[2])    # encode string argument
    os.system('echo '+encoded+' >> encrypted.txt')
    os.system('echo '+base64.b64encode(secret)+' >> key.txt')

if '-d' in sys.argv:
    secret = base64.b64decode(swap('key.txt',False).pop())     # generate a random secret key
    encoded = swap('encrypted.txt', False).pop()
    cipher = AES.new(secret)                                   # create a cipher object using the random secret
    decoded = DecodeAES(cipher, encoded)                       # decode the encoded string
    print 'Result: %s' % decoded

if 'clear' in sys.argv:
    os.system('rm encrypted.txt; rm key.txt')
# EOF
