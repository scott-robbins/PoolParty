try:
    import paramiko
except:
    pass
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
    size = ''
    file_size = int(cmd('ls -la '+filename).split(' ')[4])
    return file_size, file_size/1000.      # Return filesize and filesize in Kb


