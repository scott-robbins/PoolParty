#!/bin/bash
if [ $# != 1 ]; then
    echo 'Incorrect Usage!'
    echo '$ ./update_peer_code.sh <ip_address>'
    exit
fi
python utils.py cmd $1 'rm conductive.py' > /dev/null 2>&1
python utils.py send $1 conductive.py -v > /dev/null 2>&1
echo '\033[1m'$1' Has Been Updated\033[m'
#EOF
