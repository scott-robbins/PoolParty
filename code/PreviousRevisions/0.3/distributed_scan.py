from Crypto.Random import get_random_bytes
from threading import Thread
import control
import base64
import setup
import utils
import time 
import sys 
import os


def execute_nmap_scan(target, rmt_peer, creds, tmpf):
	cmd = 'nmap -Pn -T5 %s >> %s' % (target, tmpf)
	utils.ssh_exec(cmd, creds[rmt_peer][1], creds[rmt_peer][0], creds[rmt_peer][2], False)	

def main():
	nodes = control.get_node_names()
	c, latency = control.get_cluster_creds(nodes, False)
	localcmd = "head -n 10 ~/Snoopy/code/Blue/unique.txt | while read n; do echo $n | cut -d ':' -f 1; done"
	targets = utils.cmd(localcmd,False)
	threads = []
	paths = {}
	for n in nodes:
		t = targets.pop()
		fr = 'tmp'+base64.b64encode(get_random_bytes(4)).replace('/','x')+'.txt'
		Thread(target=execute_nmap_scan, args=(t, n, c,fr,)).start()
		threads.append([0, n, t, fr])
		if c[n][1] == 'root':
			rpath = '/root/'
		else:
			rpath = '/home/%s' % c[n][0]
		paths[n] = rpath

	print 'Finished Running scans. Waiting for 30s, then downloading Results'
	time.sleep(25)
	for tvec in threads:
		rp = paths[tvec[1]]
		utils.ssh_get_file(rp,tvec[3],c[tvec[1]][1], c[tvec[1]][0], c[tvec[1]][2])
		os.system('mv %s %s' % (tvec[3], tvec[2]))
	os.system('python control.py --cmd-all rm tmp\x2a >> /dev/null')

if __name__ == '__main__':
	main()
