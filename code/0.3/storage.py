import numpy as np
import hashlib
import time 
import sys 
import os 


class HashTable:
	slot_id = -1 # start with an invalid size
	hashes = [] # actually hashes this node has
	n_nodes = 0 # need to keep track in case table is shuffled on node exits
	peers = {} # Save peer info, and which bucket they fill

def __init__(self, table_loc, table_size):
	self.slot_id = table_loc	# the chunk of hashspace this node owns
	self.n_nodes = table_size	# the numbers of divisions in table

def is_mine(filename):
	save = false
	if os.path.isfile(filename):
		hashsum = file256sum(filename)
		chunks = divide_hashsum(hashsum)
		if choose_largest_chunk(chunks) == self.slot_id:
			save = True
	else:
		print '[!!] Cannot find %s' % filename
	return save


def data256sum(data):
	return hashlib.sha256(data).digest()

def file256sum(filename):
	sha256_hash = hashlib.sha256()
	with open(filename,"rb") as f:
		# Read and update hash string value in blocks of 4K
		for byte_block in iter(lambda: f.read(4096),b""):
			sha256_hash.update(byte_block)
	return sha256_hash.hexdigest()

def divide_hashsum(hashsum, N_NODES):
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

def choose_largest_chunk(buckets):
	slots = []
	for section in buckets:
		slots.append(int(section, 16))  # convert to 16-bit integer
	# return the largest bucket
	return np.where(np.array(slots) == np.array(slots).max()) 

