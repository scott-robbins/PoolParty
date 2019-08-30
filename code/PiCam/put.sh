#!/bin/bash

ip=$1
path=$2
user=$3
username=$4
password=$5
file=$6

ftp -inv $ip << EOF
$user $username $password

cd $path
put $file

bye
EOF
