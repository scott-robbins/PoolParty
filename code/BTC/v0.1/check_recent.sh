#!/bin/sh
rm btc_prices.txt;
python client.py get 192.168.1.200 '~/Desktop/PoolParty/code/btc_prices.txt';
tail btc_prices.txt;
echo ' '
#EOF 
