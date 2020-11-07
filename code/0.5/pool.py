from dotenv import load_dotenv
from threading import Thread
import multiprocessing
import network
import random
import utils 
import time
import sys
import os

load_dotenv()

class Pool():
	task_list = []
	workers = {}
	verbose = False
	running = False

	def __init__(self, nodes, verbosity):
		self.workers = nodes
		self.verbose = verbosity

	def run(self):
		self.running = True
		threads = multiprocessing.Pool(10)
		# Start iteratively running through nodes in pool
		while self.running:
			# check in on connected nodes
			try:
				for node_name in self.workers.keys():
					peer =  self.workers[node_name]
					if peer['connected']:	# check in on worker
						# see if they have jobs finished (populates self.task_list)
						n_jobs = self.check_for_node_work(threads, node_name)
			except RuntimeError:
				# hmm how to handle this correctly???
				pass
			
			# check whether previously disconnected nodes are now connected
			self.check_disconnected_nodes(threads, self.verbose)

			# Check if more tasks have been added to the queue
			if len(self.task_list):
				# load the next job
				job = self.task_list.pop()
				job_creator = job[0]
				job_actions = job[1]

	def check_for_node_work(self, threadpool, name):
		p = self.workers[name]
		h = self.workers[name]['hname']
		i = self.workers[name]['ip']
		p = self.workers[name]['pword']
		loc = '/home/%s/Work/' % h
		e = threadpool.apply_async(func=utils.remote_file_exists, args=(h,i,p,loc))
		try:
			exists = e.get(timeout=10)
			if exists == 1:
				# make the folder
				show = 'ls /home/%s/Work' % h
				e2 = threadpool.apply_async(func=utils.ssh_exec, args=(show, i,h,p,False)) 
				result = len(e2.get(timeout=10))
			elif exists == 0:
				show = 'mkdir /home/%s/Work' % h
				e2 = threadpool.apply_async(func=utils.ssh_exec, args=(show, i,h,p, False))
				try:
					e2.get(timeout=10)
				except multiprocessing.context.TimeoutError:
					self.disconnect_node_from_pool(name)	
					result = 0
					pass
		except multiprocessing.context.TimeoutError:
			self.disconnect_node_from_pool(name)	
			result = 0
			pass
		
		return result


	def check_disconnected_nodes(self, threadpool, verbose):
		for node in network.get_node_names():
			if node not in self.workers.keys():
				# see if node is now connected
				h, i, p, m = utils.load_credentials(node, False)
				e = threadpool.apply_async(func=network.check_connected, args=(h,i,p,))
				try:
					self.workers[node]['connected'] = e.get(timeout=10)
				except multiprocessing.context.TimeoutError:
					self.disconnect_node_from_pool(node)
					pass
				except IndexError:
					self.disconnect_node_from_pool(node)
					pass
				if self.workers[node]['connected']:
					self.connect_node_to_pool(node)	
			elif not self.workers[node]['connected']:
				# see if node is now connected
				h = self.workers[node]['hname']
				i = self.workers[node]['ip']
				p = self.workers[node]['pword']
				e = threadpool.apply_async(func=network.check_connected, args=(h,i,p,))
				try:
					self.workers[node]['connected'] = e.get(timeout=10)
				except multiprocessing.context.TimeoutError:
					self.disconnect_node_from_pool(node)
					pass
				except IndexError:
					self.disconnect_node_from_pool(node)
					pass
				if self.workers[node]['connected']:
					self.connect_node_to_pool(node)	


	def disconnect_node_from_pool(self, name):
		self.workers[name]['connected'] = False
		if self.verbose:
			print('[!] %s has left Pool' % name.split('/')[-1].split('.')[0])

	def connect_node_to_pool(self, name):
		self.workers[name]['connected'] = True
		if self.verbose:
			print('[!] %s has joined Pool' % name.split('/')[-1].split('.')[0])		
