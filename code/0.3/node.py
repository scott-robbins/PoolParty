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
	TALKER = False
	ROUTER = False
	HOARDER = True
	WORKER = False	    # node style (WORKER, TALKER, ROUTER, HOLDER, etc...)
	internal_ip = []	# Not all machines will only have one active adapter?
	external_ip = ''	# IP seen outisde of NAT
	cpu_rating = 0.0	# computational power rating
	trx_rating = 0.0	# network connectivity rating


	def __init__(self, nickname):
		self.external_ip = utils.get_ext_ip().replace('$','').replace(' ','')
		self.get_internal_addr()
		if self.external_ip in self.internal_ip:
			self.ROUTER = True
		self.cpu_rating = self.test_cpu_power()
		# Choosing based on an arbistrary value of 100ms
		if self.cpu_rating < 0.1:
			self.WORKER = True

	def get_internal_addr(self):
		# This is only working when run locally for raspberry pi. not sure why
		addrs = utils.cmd('hostname -I',False).pop().split(' ')
		addrs.pop(-1)
		self.internal_ip =  addrs

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
		traits = {'TALKER': self.TALKER,
				  'ROUTER': self.ROUTER,
				  'HOARDER': self.HOARDER,
				  'WORKER': self.WORKER}
		ipstr = '\n'; n = 1
		for addr in self.internal_ip:
			ipstr += '    [%d] %s\n' % (n, addr)
			n += 1
		result = '[* --- < Node Details > --- *]\n'
		result += '  - Internal IP(s): %s' % ipstr
		result += '  - External IP: %s\n' % self.external_ip
		result += '  - CPU Test Timing: %ss\n' % str(self.cpu_rating)
		for ability in traits:
			if traits[ability]:
				result += '  - Node is a %s\n' % ability

		return result

					
def main():
	node = Node('Test')
	print node.show()

if __name__ == '__main__':
	main()	

