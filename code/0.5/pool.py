from dotenv import load_dotenv
from threading import Thread
import multiprocessing
import storage
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
		threads = multiprocessing.Pool(12)
		n_cycles = 0; start = time.time()
		# TODO: This works ok, but it doesnt know when to stop (continually distributes)
		shared_data = storage.MasterRecord(self.workers.keys())
		shared_data.distribute()

		# Start iteratively running through nodes in pool
		while self.running:
			pool_cycle_start = time.time()
			# check in on connected nodes
			try:
				for node_name in self.workers.keys():
					peer =  self.workers[node_name]
					if peer['connected']:	# check in on worker
						# see if they have jobs finished (populates self.task_list)
						jobs = self.check_for_node_work(threads, node_name)
						# work on jobs 
						if jobs != 0 and len(jobs):
							print('[*] %d New Job(s) added by %s' % (len(jobs), node_name))
							results = self.execute_node_work(threads, node_name, jobs)

						# check shared folders for changes
						if n_cycles > 1:
							# This works okay, but adding new files while running will break it
							# if the file you add has a new name (key will be missing from pool)
							# so add in a pop/insert mechanism for the file keys!
							print('\033[1m\033[32mChecking Node Shares\033[0m')
							shared_data.distribute()
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

			# How long does this inner loop take? it's basically refresh rate for pool
			cycle_time = time.time() - pool_cycle_start  # right now, this is about 7 Seconds
			n_cycles += 1
			if n_cycles % 3 == 0:
				avg = float(time.time() - start)/n_cycles
				print('[%ss Cycle, %d Cycles Run - %fs/cyc. on avg]' % (str(cycle_time), n_cycles, avg)) 
				# shared_data.distribute()

	def execute_node_work(self,threadpool, node_name, job_names):
		# Process node work
		exes = ['sh', 'bash', 'py', 'class']
		opco = {'sh': 'sh',
				'bash': 'bash',
				'py':	'python',
				'class': 'java'}
		results = {}
		for job_title in job_names:
			fun = job_title.split('.')[0]
			ext = job_title.split('.')[1]
			p = self.workers[node_name]
			h = self.workers[node_name]['hname']
			i = self.workers[node_name]['ip']
			p = self.workers[node_name]['pword']
			print('[*] Executing %s on peer %s' % (job_title, node_name))
			
			if ext in exes and ext !='c':
				cmd = '%s /home/%s/Work/%s' % (opco[ext], h, job_title)
				w = threadpool.apply_async(func=utils.ssh_exec, args=(cmd,i,h,p,True))
				results[job_title] = w.get(timeout=5)
				# Now remove the job
				rmcmd = 'rm /home/%s/Work/%s' % (h,job_title)
				w = threadpool.apply_async(func=utils.ssh_exec, args=(rmcmd,i,h,p,False))
				w.get(timeout=5)

		return results

	def check_for_node_work(self, threadpool, name):
		p = self.workers[name]
		h = self.workers[name]['hname']
		i = self.workers[name]['ip']
		p = self.workers[name]['pword']
		loc = '/home/%s/Work/' % h
		# Check whether NODE has any new files in WORK folder
		e = threadpool.apply_async(func=utils.remote_file_exists, args=(h,i,p,loc))
		try:
			exists = e.get(timeout=5)
			if exists == 1:
				# make the folder
				show = 'ls /home/%s/Work' % h
				e2 = threadpool.apply_async(func=utils.ssh_exec, args=(show, i,h,p,False)) 
				result = e2.get(timeout=10)
			elif exists == 0:
				show = 'mkdir /home/%s/Work' % h
				e2 = threadpool.apply_async(func=utils.ssh_exec, args=(show, i,h,p, False))
				try:
					e2.get(timeout=5)
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
					self.workers[node]['connected'] = e.get(timeout=5)
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
					self.workers[node]['connected'] = e.get(timeout=5)
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

