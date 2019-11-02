from multiprocessing.pool import ThreadPool
from threading import Thread
import time
import sys
import os
try:
    import paramiko
except ImportError:
    pass
# ##### USERS/NODES HARDCODED FOR NOW ##### #
prs = ['192.168.1.200',
       '192.168.1.217',
       '192.168.1.229']

names = {'192.168.1.200': 'root',
         '192.168.1.217': 'pi',
         '192.168.1.229': 'pi'}


# ########################################### #


def cmd(command):
    os.system(command+' >> cmd.txt')
    return str_builder(swap('cmd.txt',True))


def get_local_ip():
    return cmd('ifconfig | grep broadcast | cut -b 14-28').replace('\n','').replace(' ','')


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


def swap(fname,destroy):
    data = []
    for line in open(fname, 'r').readlines():
        data.append(line.replace('\n', ''))
    if destroy:
        os.remove(fname)
    return data


def str_builder(data):
    content = ''
    for word in data:
        content += word + '\n'
    return content


def arr2string(data):
    content = ''
    for word in data:
        content += word + ' '
    return content


def popup_examples(msg):
    os.system('notify-send "'+str(msg)+'"')


def crawl_dir(file_path, hash, verbose):
    directory = {'dir': [], 'file': []}
    hashes = {}
    folders = [file_path]
    while len(folders) > 0:
        direct = folders.pop()
        if verbose:
            print 'Exploring %s' % direct
        try:
            for item in os.listdir(direct):
                if os.path.isfile(direct + '/' + item):
                    file_name = direct + "/" + item
                    directory['file'].append(file_name)
                    if hash:
                        hashes['"' + file_name + '"'] = get_sha256_sum(file_name, False)
                    if verbose:
                        print '\033[3m- %s Added to Shared Folder\033[0m' % file_name
                else:
                    directory['dir'].append(direct + '/' + item)
                    folders.append(direct + '/' + item)
        except OSError:
            pass
    return directory, hashes


def get_sha256_sum(file_name, verbose):
    if len(file_name.split("'"))>=2:
        file_name = ("{!r:}".format(file_name))
        os.system("sha256sum "+file_name + ' >> out.txt')
    else:
        os.system("sha256sum '%s' >> out.txt" % file_name)
    try:
        sum_data = swap('out.txt', True).pop().split(' ')[0]
    except:
        print file_name
    if verbose:
        print sum_data
    return sum_data


'''                            COMMUNICATION FUNCTIONS                            '''
import warnings                                       # SUPRESSING PARAMIKO WARNINGS!
warnings.filterwarnings(action='ignore',module='.*paramiko.*')
IP = cmd('ifconfig | grep broadcast | cut -b 14-28').replace('\n','').replace(' ','')


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


def get_file_untrusted(ip,user,password,file_name,verbose):
    tic = time.time()
    if len(list(file_name.split('/'))) > 1:
        local_file = list(file_name.split('/')).pop()
    else:
        local_file = file_name
    cmd = 'cat '+file_name
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    response = ''
    try:
        client.connect(ip, username=user, password=password)
        ssh_session = client.get_transport().open_session()
        response = ''
        if ssh_session.active:
            ssh_session.exec_command(cmd)
            response = ssh_session.recv(999999999999999)
    except paramiko.ssh_exception.NoValidConnectionsError:
        print "Could not connect to %s" % ip
    open(local_file, 'w').write(response)
    file_size, file_size_kb = check_file_size(local_file, False)
    if verbose:
        Data_Transferred = '%s B' % str(file_size)
        if 1000000 > file_size > 1000:
            Data_Transferred = '%s KB' % str(file_size_kb)
        print '\033[1m[*] Local File Is \033[31m%s KB\033[0m' % str(file_size_kb)
        print '\033[1m\033[32mFile Transferred!\033[0m\033[1m\t[%s in %ss Elapsed]\033[0m' % \
              (Data_Transferred, str(time.time() - tic))
    return file_size


def retrieve_credentials(node):     # TODO: Keys must be kept in KEYS/ dir
    os.system('cp KEYS/' + node.replace('.', '') + '.txt encrypted.txt')
    os.system('cp KEYS/' + node.replace('.', '') + '.key key.txt')
    os.system('python aes.py -d >> data.txt; rm encrypted.txt key.txt')
    ln = swap('data.txt', True).pop()
    pw = ln.split('Result: ')[1].replace(' ', '')
    return pw


def ftp_put(ip, username, password, local_file, remote_file):
    transport = paramiko.Transport((ip, 22))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.put(local_file, remote_file)


def check_file_size(filename, verbose):
    file_size = int(cmd('ls -la '+filename).split(' ')[4])
    return file_size, file_size/1000.      # Return filesize and filesize in Kb


def send_file(proj_path, target, local_file, quiet):
    tic = time.time()
    """
    Send File to a remote host
    :return:
    """
    rmt_file = local_file
    if '/' in list(rmt_file):
        rmt_file = rmt_file.split('/').pop()
    if not quiet:
        print ' %s Sending %s File %s' % (IP, target, rmt_file)
    host = names[target]
    pw = retrieve_credentials(target)
    # Now Actually do it
    file_size, file_size_kb = check_file_size(local_file, False)
    Data_Transferred = '%s B' % str(file_size)
    if not quiet:
        if 1000000 > file_size > 1000:
            Data_Transferred = '%s KB' % str(file_size_kb)
            print '\033[1m[*] Local File Is \033[31m%s KB\033[0m' % str(file_size_kb)
        elif file_size_kb > 1000:
            Data_Transferred = '%s MB' % str(file_size_kb / 1000.)
            print '\033[1m Local File Is \033[31m%s MB\033[0m' % str(file_size_kb / 1000.)
    ssh_command(target, host, pw, 'cd ' + proj_path + '; echo $PWD; nc -l -p 5000 >> ' + rmt_file, True)
    time.sleep(.3)
    os.system('cat ' + local_file + ' | nc -q 2 ' + target + ' 5000')
    if not quiet:
        print '\033[1m\033[32mFile Transferred!\033[0m\033[1m\t[%s in %ss Elapsed]\033[0m' % \
              (Data_Transferred, str(time.time() - tic))
    return Data_Transferred, time.time() - tic


def get_file(localhost, target, remote_file):
    tic = time.time()
    rmt_file = remote_file
    if '/' in list(rmt_file):
        rmt_file = rmt_file.split('/').pop()
    print ' %s Getting %s File %s' % (IP, target, rmt_file)
    name = names[target]
    pwrd = retrieve_credentials(target)
    filename = rmt_file
    getcmd = 'ls -la %s; sleep 2; cat %s | nc -q 2 %s 5000' % (filename, filename, localhost)
    ssh_command(target, name, pwrd, getcmd, False)
    os.system('nc -l 5000 > '+rmt_file)
    file_size, file_size_kb = check_file_size(rmt_file, False)
    Data_Transferred = '%s B' % str(file_size)
    if 1000000 > file_size > 1000:
        Data_Transferred = '%s KB' % str(file_size_kb)
    print '\033[1m[*] Local File Is \033[31m%s KB\033[0m' % str(file_size_kb)
    print '\033[1m\033[32mFile Transferred!\033[0m\033[1m\t[%s in %ss Elapsed]\033[0m' % \
          (Data_Transferred, str(time.time() - tic))
    return Data_Transferred, time.time()-tic


def get_file_2(local_file, rmt_file):
    cmd = "rm btc_prices.txt; nc -l 6666 >> %s & " \
          "python client.py cmd 192.168.1.200 'sleep 1; " \
          "cat %s | nc -q 2 192.168.1.153 6666'" % (local_file, rmt_file)
    os.system(cmd)
    return swap(cmd, False)


def start_listener(file_name, port):
    if os.name != 'nt':
        cmd = 'nc -l -k %d >> %s' % (port, file_name)
        os.system(cmd)


def command_peer(peer, command, verbosity):
    uname = names[peer]
    pw = retrieve_credentials(peer)
    ssh_command(peer, uname, pw, command, verbosity)


def command_all_peers(command, verbose):
    replies = {}
    pool = ThreadPool(processes=1)
    for peer in names.keys():
        pw = retrieve_credentials(peer)
        reply = pool.apply_async(ssh_command, (peer,names[peer],pw,command,verbose))
        if verbose:
            print reply.get()
        replies[peer] = reply
    return replies


def distribute_file_resource(file_in):
    for peer in prs:
        path = os.getcwd()+'/'+ peer
        cmd = Thread(target=send_file,args=(path, peer, file_in))
        cmd.start()
        cmd.join()


def test_transfer_rate(remote):
    if remote not in names.keys():
        print '[!!] Unknown Peer!'
        exit()

    content = ''
    for ln in range(2000):
        content += '\x42'*50+'\n'
    open('test_file.txt', 'w').write(content)

    tic = time.time()
    file_size = os.path.getsize('test_file.txt')
    os.system('python utils.py send %s test_file.txt > /dev/null 2>&1' % remote)
    dt = time.time() - tic

    db = file_size/(8000*dt)
    print '\033[1m\033[31mFile Transfer Speed: %sKB/s\033[0m' % db
    return db

#
tic = time.time()
verbosity = False
operation = False
if '-v' in sys.argv:
    verbosity = True

if 'cmd_all' in sys.argv and len(sys.argv) >= 3:
    cmd = sys.argv[2]
    replies = command_all_peers(cmd, verbose=verbosity)
    print '%d Replies Received' % len(replies)
    operation = True

if 'cmd' in sys.argv and len(sys.argv) >= 4:
    host = sys.argv[2]
    cmd = sys.argv[3]
    command_peer(host, cmd, True)
    operation = True

if 'send' in sys.argv and len(sys.argv) >= 4:
    host = sys.argv[2]
    file_in = sys.argv[3]
    send_file(os.getcwd(), host, file_in, True)
    operation = True

if 'get' in sys.argv and len(sys.argv) >= 4:
    ip = sys.argv[2]
    try:
        name = names[ip]
    except KeyError:
        print '[*] Unknown Host %s!'
    file_name = sys.argv[3]
    pw = retrieve_credentials(ip)
    get_file_untrusted(ip, name, pw, file_name, verbosity)
    operation = True

if operation:
    print '\033[1mFINISHED \033[31m[%ss Elapsed]\033[0m' % str(time.time()-tic)
