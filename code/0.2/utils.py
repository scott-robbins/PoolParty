from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
import paramiko
import base64
import time
import os

# #################### CRYPTOGRAPHIC LAMBDA FUNCTIONS #################### #
BLOCK_SIZE = 16     # the block size for the cipher object; must be 16 per FIPS-197
PADDING = '{'
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING        # pad text to be encrypted
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))            # encrypt with AES
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
# ##############  ###### ~ LAMBDA DEFINITIONS END ~ ######  ############## #


def create_timestamp():
    date = time.localtime(time.time())
    mo = str(date.tm_mon)
    day = str(date.tm_mday)
    yr = str(date.tm_year)

    hr = str(date.tm_hour)
    min = str(date.tm_min)
    sec = str(date.tm_sec)

    date = mo + '/' + day + '/' + yr
    timestamp = hr + ':' + min + ':' + sec
    return date, timestamp


def swap(file_name, destroy):
    data = []
    for line in open(file_name, 'r').readlines():
        data.append(line.replace('\n', ''))
    if destroy:
        os.remove(file_name)
    return data


def cmd(shell):
    os.system('%s >> tmp.txt' % shell)
    return swap('tmp.txt', True)


def arr2str(arr):
    content = ''
    for e in arr:
        content += e + ' '
    return content


def arr2lines(arr):
    content = ''
    for line in arr:
        content += line + '\n'
    return content


def get_local_ip():
    os.system('ifconfig | grep broadcast >> ip.txt')
    raw_line = swap('ip.txt', True).pop()
    ip = raw_line.split('inet ')[1].split(' netmask')[0]
    return ip


def arr2dir(str_arr):
    out = ''
    for element in str_arr:
        out+='%s/' % element
    return out


# ######################## ENCRYPTED COMMUNICATION FUNCTIONS ######################## #
import warnings                                       # SUPRESSING PARAMIKO WARNINGS!
warnings.filterwarnings(action='ignore',module='.*paramiko.*')


def ssh_command(ip, user, passwd, command, verbose):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    response = ''
    try:
        client.connect(ip, username=user, password=passwd)
        ssh_session = client.get_transport().open_session()
        response = ''
        if ssh_session.active:
            ssh_session.exec_command(command)
            response = ssh_session.recv(16777216)  # needed for file sharing
            if verbose:
                print '%s@%s:~$ %s [Executed]' % (user, ip, command)
                print '%s@%s:~$ %s' % (user, ip, response)
                return response

    except paramiko.ssh_exception.NoValidConnectionsError:
        print "Could not connect to %s" % ip
    return response
