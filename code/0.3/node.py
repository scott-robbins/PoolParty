import control 
import routing 
import storage 
import utils
import setup
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
		# self identify
		self.identify()
		# determine roles if not already determined
		self.whoami()
		# log data about self for faster future loading
		# check functions based on roles found

	def identify(self):
		myname = utils.cmd('whoami', False)
		self.internal_ip = utils.get_internal_addr()
		print "Identifying as %s\n" % myname

		for name in control.get_node_names():
			hname, addr, pw, pk = control.load_credentials(name,False)
			if addr == self.internal_ip and myname == hname:
				print '[*] Found network name %s' % name
				self.peername = name
				break
	
	def whoami(self):
		if os.path.isfile(os.getcwd()+'/PoolData/NX/self.txt'):
			os.remove(os.getcwd()+'/PoolData/NX/self.txt')
		else:
			self.external_ip = utils.get_ext_ip()
			open(os.getcwd()+'/PoolData/NX/self.txt','wb').write(self.show())

	def show(self):
		display = 'NODE INFO: %s\n' % self.peername
		display += '\t-internal ip:\t%s\n' % self.internal_ip
		display += '\t-external ip:\t%s\n' % self.external_ip
		return display

def main():

	node = Node()
	if '--dump-info' in sys.argv:
		print node.show()

if __name__ == '__main__':
	main()
