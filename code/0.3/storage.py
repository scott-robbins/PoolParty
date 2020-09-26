import numpy as np
import hashlib
import utils
import time 
import sys 
import os 


class MasterRecord:
	slot_id = -1 # start with an invalid size
	hashes = {} # actually hashes this node has
	n_nodes = 0 # need to keep track in case table is shuffled on node exits
	peers = [] # Save peer info, and which bucket they fill
	hashtable = {}
	def __init__(self):
		# [1] First determine number of nodes in table 
		self.hashtable = self.determine_table_slots()
		# [2] check in with registered files
		shared_data = self.review_master_filelist()
		# Check if an existing table extists
		# If it does check whether new data has been added
		# Else create the table for distributing
		self.create_hashtable(shared_data) 
		# [3] check in with nodes to see if they've updated files, and redistribute
		# 	  accordingly
		

	def create_hashtable(self, rawdata):
		filenames = rawdata['file']
		for fname in self.hashes.keys():
			uid = self.hashes[fname]
			largest = self.find_largest_chunk(self.divide_hashsum(uid, self.n_nodes))[0]
			self.hashtable[self.peers[largest]] = uid
		# DEBUGGIN:
		print self.hashtable

	def determine_table_slots(self):
		hashtable = {}
		if os.path.isdir(os.getcwd()+'/PoolData') and os.path.isfile(os.getcwd()+'/PoolData/NX/peerlist.txt'):
			nodes = open(os.getcwd()+'/PoolData/NX/peerlist.txt', 'rb').read().split('\n')
			nodes.pop(-1)
			self.n_nodes = len(nodes)
			self.peers = nodes
		else:
			print '[!!] Unable to retrieve peerlist'
			exit()
		for node in nodes:
			hashtable[node] = []
		return hashtable

	def review_master_filelist(self):
		if os.path.isdir(os.getcwd()+'/PoolData/Shares'):
			contents, self.hashes = utils.crawl_dir(os.getcwd()+'/PoolData/Shares', True, False)
		else:
			print '[!!] No Shared Data'
			exit()
		return contents		

	def data256sum(self, data):
		return hashlib.sha256(data).digest()

	def file256sum(self, filename):
		sha256_hash = hashlib.sha256()
		with open(filename,"rb") as f:
			# Read and update hash string value in blocks of 4K
			for byte_block in iter(lambda: f.read(4096),b""):
				sha256_hash.update(byte_block)
		return sha256_hash.hexdigest()

	def divide_hashsum(self, hashsum, N_NODES):
		segments = np.linspace(0,63,N_NODES+1).astype(np.int)
		buckets = []
		idx = 0
		# iterate through each bucket and divide the given hash into it
		for block in segments:
			if idx > 0:
				chunk = ''.join(hashsum[segments[idx-1]:segments[idx]])
				buckets.append(chunk)
			idx += 1
		return buckets

	def find_largest_chunk(self, buckets):
		slots = []
		for section in buckets:
			slots.append(int(section, 16))  # convert to 16-bit integer
		# return the largest bucket
		return np.where(np.array(slots) == np.array(slots).max())[0]

	def find_smallest_chunk(self, buckets):
		slots = []
		for section in buckets:
			slots.append(int(section, 16))
		# return the smallest bucket
		return np.where(np.array(slots) == np.array(slots).min())

# def is_mine(filename):
	# 	save = false
	# 	if os.path.isfile(filename):
	# 		hashsum = file256sum(filename)
	# 		chunks = divide_hashsum(hashsum)
	# 		if choose_largest_chunk(chunks) == self.slot_id:
	# 			save = True
	# 	else:
	# 		print '[!!] Cannot find %s' % filename
	# 	return save

def main():
	table_data = MasterRecord()


if __name__ == '__main__':
	main()
