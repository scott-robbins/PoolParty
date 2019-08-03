import utils
import time
import sys
import os


tic = time.time()
IP = utils.cmd('ifconfig | grep broadcast | cut -b 14-28').replace('\n','').replace(' ','')

peers = utils.prs
names = utils.names
known_languages = ['python', 'java', 'sh', 'c', 'asm']


''' RAXION Distributed Computing Architecture: 

_________ - (3) Machine Types - __________
[1] Master [Single instance]
    - Command and Control Device 
[2] Planner/Delegator(s)
    - Best Network Speeds 
[3] Worker(s)
    - Best Computing speeds 
==========================================
'''


def update_all(verbose):
    for host in peers:
        name = names[host]
        pwrd = utils.retrieve_credentials(host)
        cmd = 'cd ~/Desktop/RAXion; sudo git pull origin'
        utils.ssh_command(host,name,pwrd,cmd,verbose)


def construct_operation(config):
    machine_ids = {1: [], 2: [], 3: []}
    programs = {}
    master = config['Master']  # [1]
    machine_ids[1] = [master]
    for m in config['Schedulers']:
        machine_ids[2].append(m)
    for n in config['Workers']:
        machine_ids[3].append(n)
    for i in range(len(config['Programs'])):
        programs[i+1] = config['Programs'][i]
    operations = []

    for op in config['Jobs']:
        cmd = machine_ids[int(op[0].replace('[','').replace(']',''))]
        program = [programs[int(op[1].split('<')[1].split('>')[0])]]
        execute = op[1].split('>')[1].split(' ')
        # Get Language type for command
        for lang in known_languages:
            if lang in op[1].split('<')[0].split(' ')[0]:
                program.append(lang)
        arguments = []
        if len(execute) == 2:
            arguments.append(execute[1])
        elif len(execute) > 2:
            for e in execute[1:]:
                arguments.append(e)# TODO: Complex args w/ machine refs {[n]}
        operations.append({'hosts': cmd, 'prog': program, 'args': arguments})
    return operations, machine_ids


def parse_config(filename):
    raw_config = {'Master': '', 'Schedulers': [], 'Workers': [],
                  'Programs': [], 'Jobs': []}
    seek_jobs = False
    cache_flag = False
    for line in utils.swap(filename, False):
        try:
            raw_config['Master'] = line.split('[1]: ')[1]  # Master Machine
        except IndexError:
            pass
        try:
            raw_config['Schedulers'] = line.split('[2]: ')[1].split(',')[:]  # Scheduler Machine(s)
        except IndexError:
            pass
        try:
            raw_config['Workers'] = line.split('[3]: ')[1].split(',')[:]  # Worker Machine(s)
        except IndexError:
            pass
        try:
            prog1 = line.split('\t<1>')[1].replace(' ', '')  # Program 1?
            raw_config['Programs'].append(prog1)
        except IndexError:
            pass
        try:
            prog2 = line.split('\t<2>')[1].replace(' ', '')  # Program 1?
            raw_config['Programs'].append(prog2)
        except IndexError:
            pass
        try:
            prog3 = line.split('\t<3>')[1].replace(' ', '')  # Program 1?
            raw_config['Programs'].append(prog3)
        except IndexError:
            pass
        try:
            if seek_jobs and not cache_flag:
                tasks = line.split('=>').pop()
                jobid = line.split('=>')[0].split('\t')[1]
                raw_config['Jobs'].append([jobid, tasks])
        except IndexError:
            pass

        if len(line.split('Job')) == 2:
            seek_jobs = True
        if len(line.split('Caching')) >= 2:
            cache_flag = True
    print '====================================================='
    print 'Workers: %s' % raw_config['Workers']
    print 'Scheduler(s): %s' % raw_config['Schedulers']
    print 'Master Machine: %s' % raw_config['Master']
    print 'Programs In ION:'
    for prog in raw_config['Programs']:
        print '* %s ' % prog
    return raw_config


def distributed_computation():
    Master = IP
    Delegators = ['192.168.1.229']
    Workers = ['192.168.1.217', '192.168.1.200']
    for host in peers:
        uname = names[host]
        pw = utils.retrieve_credentials(host)
        comp_bench = 'cd ~/Desktop/RAXion/code; python compbench.py'
        utils.ssh_command(host, uname, pw, comp_bench, False)
        utils.ssh_command(host, uname, pw, 'ping -c 1 1.1.1.1', False)  # TODO: Display results (optional)
        # TODO Use Results to Determine Machines [2] and rest [3]
    for filename in os.listdir(os.getcwd()):
        if 'ion' in filename.split('.'):
            print '*\033[3m Configuration Model Found \033[0m\033[1m< %s >\033[0m' % filename
            # LOAD CONFIGURATION DATA
            raw_config = parse_config(filename)
            # Create [D]istributed [O]peration (DO)
            operations, machines = construct_operation(raw_config)
            print 'Parsed Result:'
            # Do IT:
            for code in operations:
                cmd = code['prog'][1]+' '+code['prog'][0]
                arg = ''
                if len(code['args'])>2:
                    for arg in code['args']:
                        if len(arg.split('{['))>1:
                            N = int(arg.split('{[')[1].split(']}')[0])
                            for host in machines[N]:
                                arg = ' ' + host
                        arg.replace('  ', ' ')
                        cmd += ' ' + arg
                elif len(code['args'])==1:
                    cmd += ' ' + code['args'][0]
                print 'Running \033[1m\033[32m%s\033[0m on peer machine(s) \033[1m%s\033[0m' %\
                      (cmd, str(code['hosts']))


if __name__ == '__main__':

    if 'init' in sys.argv:
        print '\033[1m\t\t< Initializing >\033[1m'
        distributed_computation()

    if 'update_all' in sys.argv:
        update_all(True)

    if 'send' in sys.argv and len(sys.argv) == 4:
        peer = sys.argv[2]
        file_in = sys.argv[3]
        bytes_sent, time_elapsed = utils.send_file('~/Desktop/RAXion/code', peer, file_in)

    if 'cmd' in sys.argv:
        peer = sys.argv[2]
        cmd = sys.argv[3]
        name = names[peer]  # TODO: Can raise error if unknown peer
        pwrd = utils.retrieve_credentials(peer)
        utils.ssh_command(peer, name, pwrd, cmd, True)

    if 'get' in sys.argv:
        peer = sys.argv[2]
        if len(sys.argv[3].split('/')) > 1:
            remote_file = sys.argv[3].split('/').pop()
            base = sys.argv[3].split(sys.argv[3].split('/').pop())[0]
        base = '~/Desktop/RAXion/code'
        remote_file = sys.argv[3]
        bytes_recvd, time_spent = utils.get_file(base, IP, peer, remote_file)

