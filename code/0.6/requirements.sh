#!/bin/bash
echo '[*] Installing Dependencies...'
pip install numpy
pip install multiprocessing
yes | sudo apt-get install nmap
#EOF 