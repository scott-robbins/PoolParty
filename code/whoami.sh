#!/bin/sh

IP=$(curl https://ipinfo.io/$(curl https://api.ipify.org))
echo $IP

#EOF