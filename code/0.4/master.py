from threading import Thread
import multiprocessing
import settings
import storage
import network
import socket
import utils 
import core
import os

class Master:
	peers = {}
	nodes = []

	def __init__(self):
		self.nodes = core.get_node_names()
		self.peers = self.initialize()
		self.preferences = settings.Settings()
		self.database = storage.MasterRecord()
		self.fastest, self.best_time, self.timing = network.test_pool(verbose=False)
		self.build_pool()

	def initialize(self):
		# Create local data folder 
		if not os.path.isdir(os.getcwd()+'/PoolData/Local'):
			os.mkdir('PoolData/Local')
		# Create Network Data Folder
		if not os.path.isdir(os.getcwd()+'/PoolData/NX'):
			os.mkdir('PoolData/NX')
		# create peerlist 
		if not os.path.isfile(os.getcwd()+'/PoolData/NX/peerlist.txt'):
			open(os.getcwd()+'/PoolData/NX/peerlist.txt','wb').write(utils.arr2str(self.peers))
		# Check/Index Local Shares
		self.files, self.hashes = utils.crawl_dir(os.getcwd()+'/PoolData/Shares', True, False)
		# Load Peer Data 
		utils.refresh_peers()
		peer_data = {}
		for peer in self.nodes:
			hostname = ''
			internal = ''
			external = ''
			content, info = network.show_info(peer, False)
			if 'hostname' in info.keys():
				hostname = info['hostname']
			if 'internal' in info.keys():
				internal = info['internal']
			if 'external' in info.keys():
				external = info['external']
			peer_data[peer] = info
		# This Peer Data will be used externall in UI
		return peer_data

	

def main():
	Master()

if __name__ == '__main__':
	main()
