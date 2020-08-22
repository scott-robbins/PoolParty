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
		self.cpu_rating = self.test_cpu_power()

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
		for i in range(99):
			l1 += np.array(l0[i,:]).sum()
		dt = time.time() - t0
		return dt


	def show(self):
		ipstr = '\n'; n = 1
		for addr in self.internal_ip.values():
			ipstr += '    [%d] %s\n' % (n, addr)
			n += 1
		result = '[* --- < Node Details > --- *]\n'
		result += '  - Internal IP(s): %s' % ipstr
		result += '  - External IP: %s\n' % self.external_ip
		result += '  - CPU Test Timing: %ss\n' % str(self.cpu_rating)
		return result

					
def main():
	node = Node('Test')
	print node.show()

if __name__ == '__main__':
	main()	

