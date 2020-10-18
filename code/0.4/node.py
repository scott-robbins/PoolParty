import utils
import core
import time 
import sys 
import os 

class Node:
	hostname = ''
	peername = ''
	internal_ip = ''
	external_ip = ''
	role = None

	def __init__(self):
		# determine roles if not already determined
		self.whoami()
		# log data about self for faster future loading
		# check functions based on roles found

	def identify(self):
		self.hostname = utils.cmd('whoami', False).pop()
		self.internal_ip = utils.get_internal_addr().pop(0)
		self.external_ip = utils.get_ext_ip()
		for name in core.get_node_names():
			hname, addr, pw, pk = core.load_credentials(name,False)
			if (addr == self.internal_ip):
				print '[*] Found network name %s' % name
				self.peername = name
				break

	
	def whoami(self):
		if not os.path.isdir(os.getcwd()+'/PoolData/'):
			os.mkdir(os.getcwd()+'/PoolData')
		if not os.path.isdir(os.getcwd()+'/PoolData/NX'):
			os.mkdir(os.getcwd()+'/PoolData/NX')
		if os.path.isfile(os.getcwd()+'/PoolData/NX/self.txt'):
			os.remove(os.getcwd()+'/PoolData/NX/self.txt')
		if not os.path.isdir(os.getcwd()+'/PoolData/Shares'):
			os.mkdir(os.getcwd()+'/PoolData/Shares')
		else:
			# self identify
			self.identify()
			open(os.getcwd()+'/PoolData/NX/self.txt','wb').write(self.show())

	def refresh(self):
		if os.path.isfile(os.getcwd()+'/PoolData/NX/self.txt'):
			os.remove(os.getcwd()+'/PoolData/NX/self.txt')

	def show(self):
		info = {}
		display = '\nNODE INFO: %s\n' % self.peername
		display += '\t-name:\t%s\n' % self.hostname
		display += '\t-internal ip:\t%s\n' % self.internal_ip
		display += '\t-external ip:\t%s\n' % self.external_ip
		return display

def main():

	node = Node()
	if '--dump-info' in sys.argv:
		print node.internal_ip
		print node.external_ip
		print node.hostname
		for name in control.get_node_names():
			h, ad, pw, pk = core.load_credentials(name,False)
			print name 
			print h 
			print ad
			if (ad == node.internal_ip):
				print '[*] Found network name %s' % name
		print node.show()

	if '--refresh' in sys.argv:
		node.refresh()

if __name__ == '__main__':
	main()
