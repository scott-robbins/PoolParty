import control 
import utils 
import setup
import time 
import sys
import os 


# Need to define peers in different classes of worker. Different machines have different levels of connectivity, 
# will be sitting in different network topologies, and have different levels of computational power. Utilizng nodes
# effecively will require knowing this about each peer and organizing their coordination around these profiles. 

class Node:
	style = ''			# node style (WORKER, TALKER, ROUTER, etc...)
	internal_ip = {}	# Not all machines will only have one active adapter?
	external_ip = ''	# IP seen outisde of NAT
	cpu_rating = 0.0	# computational power rating
	trx_rating = 0.0	# network connectivity rating

	def __init__(self, nickname):
		self.external_ip = utils.get_ext_ip()
		hostname, ip, pword, pkey = setup.load_credentials(nickname, True)
		self.get_internal_addr()

	def get_internal_addr(self):
		for line in utils.cmd('ifconfig | grep UP', False):
			iface = line.split(':')[0].replace('\n','').replace(' ','')
			flags = utils.arr2chstr(line.split(':')[1].split('<')[1:]).split('>')[0].split(',')
			if 'RUNNING'  in flags:
				route = utils.cmd('ifconfig %s | grep inet | grep netmask' % iface, False)
				if 'LOOPBACK' not in flags:
					self.internal_ip[iface] = route.pop().split(' netmask')[0].replace(' ','').split('inet')[1]
					
def main():
	Node('Test')

if __name__ == '__main__':
	main()	

