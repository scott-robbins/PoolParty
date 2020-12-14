#!/bin/bash
h=$(hostname)
wd=$(/home/$h/Documents/PoolParty/)
cd $wd
git pull origin
#EOF