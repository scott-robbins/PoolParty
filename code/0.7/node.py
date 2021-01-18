import multiprocessing
import threading
import backend
import utils 
import time
import json
import sys 
import os 


CHANNELS = ['BTC', 'Security', 'Music', 'Self']

class Node():
	node_name = ''		# name on the p2p network
	internal_ip = ''
	external_ip = ''	
	subbed = []			# channels node subscribes to
	uptime = 0.0
	config = {}
	raw_state = {}

	def __init__(self, name):
		# change initial fields
		self.start_tic = time.time()
		self.node_name = name
		self.running = True
		self.DEBUG = False
		# If config file doesnt exist, make one based on what is present
		if not os.path.isdir('PoolData'):
			os.mkdir('PoolData')
		if not os.path.isdir('PoolData/Config'):
			os.mkdir('PoolData/Config')
		if not os.path.isfile('PoolData/Config/config.json'):
			self.update_config() # TODO: this should be encrypted, even if saved locally
		else:
			with open('PoolData/Config/config.json','r') as jf:
				self.config = json.load(jf)
			jf.close()
			# warn if something looks wrong with config loaded
			if self.config['nxname'] != name:
				print('[!!] Configuration loaded has a \033[1mdifferent\033[0m name')
			print('[*] Configuration Loaded from Disk')
			# Save new structure
			self.update_config()
		# Check local structure
		self.update_channels()
		# TODO: Nodes need to be able to be given master(s)
		# Should start a thread to listen for messages from master or BROKERS
		# self.backend = backend.Messager(self.node_name)
		self.backend = threading.Thread(target=backend.Messager, args=(self.node_name,))
		self.backend.setDaemon(True)
		self.backend.start()
	
		# TODO: Nodes need to be able to be deemed BROKERS of messages from master(s)
		# Run the Node
		self.run()

	def run(self):
		# Set flag that node is running
		self.toggle_channel_status('Self','running', True)
		# Update the initial uptime counter
		self.uptime = time.time() - self.start_tic
		# Start the run loop
		try:
			pool = multiprocessing.Pool(10)
			# Iteratively check each channel for any changes
			cycle = 0
			
			while self.running:
				for op in self.raw_state.keys():
					self.check_channel_fields(op, self.DEBUG)
					time.sleep(10) # FOR DEBUGGING
					# check for changes in master node/brokers
					self.check_messaging_nodes()
					# check n_cycles
					# if self.raw_state[op]['cycle']%200:
					# 	print('[*] %s has run %d cycles' % (op, self.raw_state[op]['cycle']))
					# update the tic of channels clock
					self.toggle_channel_status(op,'cycle',cycle)
					# Check whether node backend was killed

				cycle += 1

		except KeyboardInterrupt:
			print('[*] Shutting down node')
			self.running = False
			# self.backend.kill()
			self.toggle_channel_status('Self','running',False)
			pass

	def check_messaging_nodes(self):
		fn = 'PoolData/Config/Channels/Self/messaging.json'
		if os.path.isfile(fn):
			with open('PoolData/Config/Channels/Self/messaging.json', 'r') as f:
				messaging = json.load(f)
				if 'master' in messaging.keys():
					print('[*] Master node is: %s' % messaging['master'])
				if 'brokers' in messaging.keys():
					print('[*] Brokers are:\n%s' % utils.arr2str('-'.join(messaging['brokers'])))
				# check if backend was killed 
				if 'listening' in messaging.keys():
					self.running = messaging['listening']
					if not self.running:
						print('[!!] Triggering Shutdown from Backend')

	def update_channels(self):
		# make sure these folders are present
		if not os.path.isdir('PoolData/Config/Channels'):
			print('')
			os.mkdir('PoolData/Config/Channels')
		for chname in CHANNELS:
			if not os.path.isdir('PoolData/Config/Channels/%s' % chname):
				os.mkdir('PoolData/Config/Channels/%s' % chname)
				init = {'channel_name': chname, 'running': False,
						'subscriber': False, 'consumer': False,
						'cycle': 0}
				# Every channel needs some information about it to be maintained
				with open('PoolData/Config/Channels/%s/settings.json' % chname,'w') as c:
					json.dump(init, c)
				self.raw_state[chname] = init
				c.close()
			else:
				with open('PoolData/Config/Channels/%s/settings.json' % chname,'r') as c:
					self.raw_state[chname] = json.load(c)
				c.close()
			# check whether anything is running
			self.check_channel_fields(chname,self.DEBUG)



	def check_channel_fields(self, channel, verbose):
		data = []
		if channel not in self.raw_state.keys():
			print('[!!] Unable to find channel %s' % channel)
			return []
		else:
			if 'running' in self.raw_state[channel].keys() and self.raw_state[channel]['running']:
				if verbose:
					print('[*] %s Process is \033[32m\033[1mRunning\033[0m' % channel)
			# TODO: Handle what happens if node is a SUBSCRIBER of channel
			# TODO: Handle what happens if node is a CONSUMER of channel


	def update_config(self):
		"""
		can also be used to update an existing config
		"""
		print('[*] Saving configuration')
		self.config['nxname'] = self.node_name
		if 'int_ip' not in self.config.keys():
			self.config['int_ip'] = utils.get_internal_addr()
		if 'ext_ip' not in self.config.keys():
			self.config['ext_ip'] = utils.get_ext_ip()
		# write the config
		with open('PoolData/Config/config.json', 'w') as jfile:
			json.dump(self.config, jfile)
		jfile.close()


	def toggle_channel_status(self,channel, field, value):
		if channel not in self.raw_state.keys():
			print('[!!] Unable to find channel %s' % channel)
			return []
		else:
			if field in self.raw_state[channel].keys():
				self.raw_state[channel][field] = value
				with open('PoolData/Config/Channels/%s/settings.json' % channel,'w') as c:
					json.dump(self.raw_state[channel], c)
				print('[*] %s.%s has been updated' % (channel, field))


def main():
	test_node = Node('test_node')

if __name__ == '__main__':
	main()
