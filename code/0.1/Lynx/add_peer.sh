#!/bin/bash

# First check args in
if [ $# != 2 ]; then
    echo 'Incorrect Usage!'
    echo '$ ./add_peer.sh <user_name> <ip_address>'
    exit
fi

# Get Password
stty -echo
read -p 'Enter Password for '$1'@'$2':' password
stty echo

# Encrypt the user data into key files
python aes.py -e $password
echo ''
keyfile=$(echo $2 | sed 's/[^0-9]*//g')'.txt'
keyfilekey=$(echo $2 | sed 's/[^0-9]*//g')'.key'

# Finalize the file with peer name
mv encrypted.txt $keyfile
mv key.txt $keyfilekey

# EOF
