import numpy as np
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
	style = ''			# node style (WORKER, TALKER, ROUTER, HOLDER, etc...)
	internal_ip = {}	# Not all machines will only have one active adapter?
	external_ip = ''	# IP seen outisde of NAT
	cpu_rating = 0.0	# computational power rating
	trx_rating = 0.0	# network connectivity rating

	def __init__(self, nickname):
		self.external_ip = utils.get_ext_ip()
		self.get_internal_addr()
		print self.test_cpu_power()

	def get_internal_addr(self):
		for line in utils.cmd('ifconfig | grep UP', False):
			iface = line.split(':')[0].replace('\n','').replace(' ','')
			flags = utils.arr2chstr(line.split(':')[1].split('<')[1:]).split('>')[0].split(',')
			if 'RUNNING'  in flags:
				route = utils.cmd('ifconfig %s | grep inet | grep netmask' % iface, False)
				if 'LOOPBACK' not in flags:
					self.internal_ip[iface] = route.pop().split(' netmask')[0].replace(' ','').split('inet')[1]


	def test_cpu_power(self):
		t0 = time.time()
		l0 = []
		l1 = 0
		for i in range(10000):
			l0.append(np.random.randint(0,1,1)[0])
		l0 = np.array(l0).reshape(100, 100)
		for i in range(1000):
			l1 += np.array(l0[i,:]).sum()
		dt = time.time() - t0
		return dt

					
def main():
	Node('Test')

if __name__ == '__main__':
	main()	

