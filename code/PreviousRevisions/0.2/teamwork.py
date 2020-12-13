import party
import utils
import time
import sys
import os

UNSAFE = False      # Pre-parse scripts for dependencies, and download libraries as needed
                    # on all nodes that are missing these needed modules

lan_ip = utils.get_local_ip()


def select_run_file():
    print '======== POOL_PARTY:RUNTIME_CONFIGURATION ========'
    os.system('ls *.run  >> configs.txt')
    configs = utils.swap('configs.txt', True)
    if len(configs) == 0:
        print '[!!] No Runtime Configuration File(s) Present! '
        exit()
    choices = {}; opt = 1
    for file_name in configs:
        print '| [%d] |\t %s\t\t\t\t  |' % (opt, file_name)
        choices[opt] = file_name
        opt += 1
    print '====|<-------------------------------------->|===='
    try:
        selection = int(raw_input('Enter a Selection: '))
        print '[*] Loading %s' % choices[selection]
    except:
        print '[!!] Illegal Selection'
        exit()
    if selection not in choices.keys():
        print '[!!] Illegal Selection'
        exit()
    return choices[selection]


def extract_features(raw_data):
    ns = []
    m = ''
    steps = []
    start_instruction_buff = False
    for line in raw_data:
        try:
            if line.split('NODES:') > 1:
                ns = line.split('NODES: ')[1].replace(' ', '').replace('\n', '').split(',')
        except IndexError:
            pass
        try:
            if line.split('MODE: ') > 1:
                m = line.split('MODE: ')[1]
        except IndexError:
            pass
        try:
            if 'OPERATIONS' in line.split(':'):
                start_instruction_buff = True
        except IndexError:
            pass
        try:
            if 'ITERATIONS' in line.split(':'):
                iterations = int(line.split('ITERATIONS: ')[1])
        except IndexError:
            pass
        if start_instruction_buff:
            steps.append(line)
    ns.insert(0, lan_ip)
    steps.pop(0)
    return ns, m, steps, iterations


def build_sequential(nodes, iterations, raw_steps):
    print '[*] %d Iterations ' % iterations
    open('run.sh', 'wb').write('#!/bin/bash\n')
    if iterations > 1:
        open('run.sh', 'a').write('for i in {1..%d};\ndo\n' % iterations)
    instruct_num = 0
    for step in raw_steps:
        if len(list(step)) <= 1:
            continue
        else:
            instruct_num = int(step.split('o ')[1].split('=')[0])
            instruct_target_host = \
                int(step.split('o ')[1].split(':')[0].replace(']', '').replace('[', '').split('=')[1])
            instruct_unparsed = step.split('[%d]:' % instruct_target_host)[1]
            '''
            Instructions are wrapped in ()
            If an instruction starts with a $, it is meant to be executed in a shell
            If an instruction starts contains <>, it is meant to be processed via the teamwork api
            '''
            if instruct_unparsed[0] == '$':
                opcode = 'SHELL'
                operation = instruct_unparsed[2:].split(')')[0]

            elif instruct_unparsed[0] == '<':  # more complicated, as it requires further parsing
                opcode = 'API'
                operation = instruct_unparsed[1:].split('>')[0]
                if 'get' in operation.split(' '):
                    opcode += '_get'
                    remote_file = operation.split('get ')[1].split(' from')[0]
                    remote_host = nodes[int(operation.split('[')[1].split(']')[0])]
                    node_creds = party.which_nodes(remote_host)
                    node_info = node_creds.split('.')[0] + '.pool'
                    credentials = party.quick_load(node_creds, node_info)
                    ip = credentials['ip']
                    uname = credentials['name']
                    pwd = credentials['password']
                    loc = utils.arr2dir(remote_file.split('/')[:-1])
                    opg = "echo 'get %s' | sshpass -p '%s' sftp %s@%s:%s\n" % \
                          (remote_file.split('/')[-1], pwd, uname, ip, loc)
                    if iterations <= 1:
                        open('run.sh', 'a').write(opg)
                    else:
                        open('run.sh', 'a').write('    '+opg)
                if 'put' in operation.split(' '):
                    opcode += '_put'
                    local_file = operation.split('get ')[1].split(' from')[0]
                    remote_host = nodes[int(operation.split('[')[1].split(']')[0])]
                    node_creds = party.which_nodes(remote_host)
                    node_info = node_creds.split('.')[0] + '.pool'
                    credentials = party.quick_load(node_creds, node_info)
                    ip = credentials['ip']
                    uname = credentials['name']
                    pwd = credentials['password']
                    opp = "echo 'put %s' | sshpass -p '%s' sftp %s@%s:%s\n" % \
                          (local_file, pwd, uname, ip, '~/%s' % local_file.split('/')[-1])
                    if iterations <= 1:
                        open('run.sh', 'a').write(opp)
                    else:
                        open('run.sh', 'a').write('    '+opp)
            # Check for configuration file syntax errors
            else:
                print '[!!] Unrecognized OP-CODE: %s' % instruct_unparsed[0]
                exit()
            if instruct_target_host > (len(nodes) + 1) or instruct_target_host < 0:
                print '[!!] Instruction defines a host CPU that is not listed as node!'
                exit()

        if opcode == 'SHELL' and instruct_target_host != 0:
            if iterations <= 1:
                open('run.sh', 'a').write('python party.py cmd %s %s\n' %
                                          (nodes[instruct_target_host], operation))
            else:
                open('run.sh', 'a').write('    python party.py cmd %s %s\n' %
                                          (nodes[instruct_target_host], operation))
        elif opcode == 'SHELL' and instruct_target_host == 0:
            verbose = True
            if iterations <= 1:
                open('run.sh', 'a').write(operation + '\n')
            else:
                open('run.sh', 'a').write('    ' + operation + '\n')
    print '[*] %d Instructions Found ' % instruct_num
    if iterations > 1:
        open('run.sh', 'a').write('done\n')
    open('run.sh', 'a').write('rm -- %s/"$0"\n#EOF\n' % os.getcwd())
    # Run the built script
    if not verbose:
        os.system('bash run.sh >> /dev/null 2>&1')
    else:
        os.system('bash run.sh')
    print '[*] Execution Finished [%ss Elapsed]' % str(time.time() - tic)


def parse_runtime(configuration):
    raw_dat = utils.swap(configuration, False)
    node_list, mode_str, instructions, N = extract_features(raw_dat)

    if mode_str == 'SEQUENTIAL':
        build_sequential(node_list, N, instructions)


if __name__ == '__main__':
    tic = time.time()
    verbose = False
    if '--unsafe' in sys.argv:
        UNSAFE = True
    if ('-v' or '--verbose') in sys.argv:
        verbose = True

    # The RUNTIME_STRUCTURE will be derived from a pool_party.run file
    # where a pool_party is a structured text-file that defines an event for
    # a cluster of machines to run cooperatively
    runtime_config_file = select_run_file()

    # Parse the Runtime Configuration File
    parse_runtime(runtime_config_file)
    print '[*] Beginning Execution [%ss Elapsed]' % str(time.time()-tic)

