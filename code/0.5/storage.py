from threading import Thread
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

	def __init__(self, nodes):
		# create some buckets for thoe peers available
		self.distro = self.setup(nodes)
		# Look at Shared Folder(s)
		# self.distribute()

	def setup(self, names):
		for name in names:
			self.peers.append(name.split('/')[-1].split('.')[0])
		# check local shares and divide
		if not os.path.isdir(os.getcwd()+'/PoolData/Shares'):
			os.mkdir(os.getcwd()+'/PoolData/Shares')
			share_distro = {}
		else:
			share_distro = self.create_distribution()
		return share_distro

		# print(share_distro)
	def distribute(self):
		# now make sure all remote hosts have share folders for receiving
		for peer in self.peers:
			h, i, p, k = utils.load_credentials(peer, False)
			if utils.remote_file_exists(h, i, p, '/home/%s/PoolParty/code/0.5/PoolData/Shares' % h) == 1:
				# get their shares
				share_names = utils.ssh_exec('ls /home/%s/PoolParty/code/0.5/PoolData/Shares' % h, i, h, p, False)
				# remote machine needs to hash its shares
				# distribute this peers files too
				# for fs in share_distro[peer]:
				for fs in os.listdir('PoolData/Shares'):
					recipient = self.distro[fs]
					rh, ri, rp, rk = utils.load_credentials(recipient, False)
					f = 'PoolData/Shares/'+fs
					rf = '/home/%s/PoolParty/code/0.5/PoolData/Shares/' % rh
					if recipient == peer and utils.remote_file_exists(h, i, p, rf+fs) == 0:
						# print('Giving %s file: %s' % (recipient, fs))
						utils.put_file(f,rf,rh,ri,rp,True)
					# else:
					# 	print('%s has file %s' % (recipient, fs))
			else:
				if utils.remote_file_exists(h, i, p, '/home/%s/PoolParty/code/0.5/PoolData' % h) == 0:
					utils.ssh_exec('mkdir /home/%s/PoolParty/code/0.5/PoolData' % h, i, h, p, False)	
				utils.ssh_exec('mkdir /home/%s/PoolParty/code/0.5/PoolData/Shares' % h, i, h, p, False)
			


	def create_distribution(self):
		distribution = {}
		for p in self.peers:
			distribution[p] = []
		for n in os.listdir('PoolData/Shares'):
			hashval = self.file256sum(os.getcwd()+'/PoolData/Shares/'+n)
			bucket = abs(self.find_largest_chunk(self.divide_hashsum(hashval, len(self.peers)))[0] -1)
			print('[*] Will distribute %s to %s' % (n, str(self.peers[bucket].split('/')[-1].split('.')[0])))
			distribution[n] = self.peers[bucket].split('/')[-1].split('.')[0]
		return distribution

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
		segments = np.linspace(0,64,N_NODES+2).astype(np.int)
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
		return np.where(np.array(slots) == np.array(slots).min())[0]

	def display_file_tree(self, path):
		tree = [path]
		result = {}
		while len(tree) > 0:
			folder = tree.pop()
			result[folder] = []
			for item in os.listdir(folder):
				if os.path.isfile(folder + '/' + item):
					result[folder].append(item)
				else:
					tree.append(folder + '/' + item)
		return result


def main():
	table_data = MasterRecord()

if __name__ == '__main__':
	main()
