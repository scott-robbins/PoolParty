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


def parse_runtime(configuration):
    raw_data = utils.swap(configuration, False)
    nodes = []
    mode = ''
    raw_steps = []
    START_INSTRUCT_BUFF = False
    for line in raw_data:
        try:
            if line.split('NODES:')>1:
                nodes = line.split('NODES: ')[1].replace(' ','').replace('\n','').split(',')
        except IndexError:
            pass
        try:
            if line.split('MODE: ')>1:
                mode = line.split('MODE: ')[1]
        except IndexError:
            pass
        try:
            if 'OPERATIONS' in line.split(':'):
                START_INSTRUCT_BUFF = True
        except IndexError:
            pass
        if START_INSTRUCT_BUFF:
            raw_steps.append(line)

    # TODO: Just for DEBUGGING
    nodes.insert(0, lan_ip)
    print '[*] %d Nodes In Runtime:' % len(nodes)
    print '[*] %s MODE Selected' % mode
    print '[o] Parsing Instructions...'
    gameplan = {}
    raw_steps.pop(0)
    for step in raw_steps:
        if len(list(step)) <= 1:
            continue
        else:
            instruct_num = int(step.split('o ')[1].split('=')[0])
            instruct_target_host = \
                int(step.split('o ')[1].split(':')[0].replace(']','').replace('[','').split('=')[1])
            instruct_unparsed = step.split('[%d]:'%instruct_target_host)[1]
            '''
            Instructions are wrapped in ()
            If an instruction starts with a $, it is meant to be executed in a shell
            If an instruction starts contains <>, it is meant to be processed via the teamwork api
            '''
            if instruct_unparsed[0]=='$':
                opcode='SHELL'
                operation = instruct_unparsed[2:].split(')')[0]
            elif instruct_unparsed[0]=='<': # more complicated, as it requires further parsing
                opcode='API'
                operation = instruct_unparsed[1:].split('>')[0]
                if 'get' in operation.split(' '):
                    opcode += '_get'
                    remote_file = operation.split('get ')[1].split(' from')[0]
                    remote_host = nodes[int(operation.split('[')[1].split(']')[0])]

                    operation = "sshpass -p '%s' sftp %s@%s:%s <<< $'get %s'" % \
                                ()
                    # TODO: Use SFTP to make this the same as a shell command
                elif 'put' in operation.split(' '):
                    opcode += '_put'
                    local_file = operation.split('get ')[1].split(' from')[0]
                    remote_host = nodes[int(operation.split('[')[1].split(']')[0])]
                    operation = "sshpass -p '%s' sftp %s@%s:%s <<< $'put %s'"  %\
                                ()
                    # TODO: Use SFTP to make this the same as a shell command
            else:
                print '[!!] Unrecognized OP-CODE: %s' % instruct_unparsed[0]
            if instruct_target_host > (len(nodes)+1) or instruct_target_host < 0:
                print '[!!] Instruction defines a host CPU that is not listed as node!'
        print '\t%d - %s on host %s' % \
              (instruct_num, opcode, nodes[instruct_target_host])
        gameplan[instruct_num] = (instruct_num, operation, nodes[instruct_target_host])
    print '[*] %d Instructions Found ' % instruct_num


if __name__ == '__main__':
    if '--unsafe' in sys.argv:
        UNSAFE = True

    # The RUNTIME_STRUCTURE will be derived from a pool_party.run file
    # where a pool_party is a structured text-file that defines an event for
    # a cluster of machines to run cooperatively
    runtime_config_file = select_run_file()

    # Parse the Runtime Configuration File
    parse_runtime(runtime_config_file)
