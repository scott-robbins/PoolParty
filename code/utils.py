try:
    import paramiko
except:
    pass
from threading import Thread
import time
import os

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


def crawl_dir(file_path, verbose):
    directory = {'dir': [], 'file': []}
    top_lvl = os.listdir(file_path)
    for element in top_lvl:
        if os.path.isdir(file_path + '/' + element):
            directory['dir'].append(file_path + '/' + element)
            if verbose:
                print '%s is a directory' % element
        elif os.path.isfile(file_path + '/' + element):
            directory['file'].append(file_path + '/' + element)
            if verbose:
                print '%s is a file' % element
    return directory


IP = cmd('ifconfig | grep broadcast | cut -b 14-28').replace('\n','').replace(' ','')

'''                             SECURITY/COMMUNICATION FUNCTIONS                            '''
import warnings     # SUPRESSING PARAMIKO WARNINGS! '''
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
            if verbose:
                response = ssh_session.recv(1024)
                print '%s@%s:~$ %s [Executed]' % (user, ip, command)
                print '%s@%s:~$ %s' % (user, ip, response)
                return response

    except paramiko.ssh_exception.NoValidConnectionsError:
        print "Could not connect to %s" % ip
    return response


def retrieve_credentials(node):
    os.system('cp KEYS/' + node.replace('.', '') + '.txt encrypted.txt')
    os.system('cp KEYS/' + node.replace('.', '') + '.key key.txt')
    os.system('python aes.py -d >> data.txt; rm encrypted.txt key.txt')
    pw = swap('data.txt', True).pop().split('Result: ')[1].replace(' ', '')
    return pw


def ftp_put(ip, username, password, local_file, remote_file):
    transport = paramiko.Transport((ip, 22))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.put(local_file, remote_file)


def check_file_size(filename, verbose):
    file_size = int(cmd('ls -la '+filename).split(' ')[4])
    return file_size, file_size/1000.      # Return filesize and filesize in Kb


def send_file(proj_path, target, local_file):
    tic = time.time()
    """
    Send File to a remote host
    :return:
    """
    rmt_file = local_file
    if '/' in list(rmt_file):
        rmt_file = rmt_file.split('/').pop()
    print ' %s Sending %s File %s' % (IP, target, rmt_file)
    host = names[target]
    pw = retrieve_credentials(target)
    # Now Actually do it
    file_size, file_size_kb = check_file_size(local_file, False)
    Data_Transferred = '%s B' % str(file_size)
    if 1000000 > file_size > 1000:
        Data_Transferred = '%s KB' % str(file_size_kb)
        print '\033[1m[*] Local File Is \033[31m%s KB\033[0m' % str(file_size_kb)
    elif file_size_kb > 1000:
        Data_Transferred = '%s MB' % str(file_size_kb / 1000.)
        print '\033[1m Local File Is \033[31m%s MB\033[0m' % str(file_size_kb / 1000.)
    ssh_command(target, host, pw, 'cd ' + proj_path + '; echo $PWD; nc -l -p 5000 > ' + rmt_file, True)
    time.sleep(.3)
    os.system('cat ' + local_file + ' | nc -q 2 ' + target + ' 5000')
    print '\033[1m\033[32mFile Transferred!\033[0m\033[1m\t[%s in %ss Elapsed]\033[0m' % \
          (Data_Transferred, str(time.time() - tic))
    return Data_Transferred, time.time() - tic


def get_file(proj_path, localhost, target, remote_file):
    tic = time.time()
    rmt_file = remote_file
    if '/' in list(rmt_file):
        rmt_file = rmt_file.split('/').pop()
    print ' %s Getting %s File %s' % (IP, target, rmt_file)
    name = names[target]
    pwrd = retrieve_credentials(target)
    filename = proj_path+'/'+rmt_file
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


def get_local_ip(verbose):
    os.system('ifconfig | grep broadcast | cut -b 14-28 >> ip.txt')
    ip = swap('ip.txt', True).pop().replace(' ','')
    if verbose:
        print '\033[1mLocal IP:\033[3m %s\033[0m' % ip
    return ip


def start_listener(file_name, port):
    if os.name != 'nt':
        cmd = 'nc -l -k %d >> %s' % (port, file_name)
        os.system(cmd)
