import backend
import network
import socket
import base64
import client
import utils 
import time
import sys 
import os

# Each machine running in the pool is active when it is
# running this program (node). It enables not only the
# client/servers to run, but organizes the signaling to other
# nodes and scheduling as directed by master. 

class Node:
	DEBUG = True
	inbound_gw = 54123	# api command server port
	outbound_tx = 5678	# outbound request port (initial)
	current_sig = 4242	# inbound signaling listener port (initial)
	op_status = 'None'
	info = {}

	def __init__(self):
		# setup local file structure for node
		self.setup_folders()
		# keep track of running jobs
		self.job_data = self.synchronize_workload(verbose=self.DEBUG)
		# check local shared files 
		lfs = self.index_local_shares()
		# notify that node is running 
		self.populate_info(lfs)
		self.log_work('node.py', False, self.info)
		# Start main loop to continuously monitor states
		

	def load_node_info(self):
		if os.path.isfile(os.getcwd()+'/PoolData/Status/node.py'):
			return utils.parse_status_file(os.getcwd()+'/PoolData/Status/node.py')

	
	def setup_folders(self):
		if not os.path.isdir(os.getcwd()+'/PoolData'):
			os.mkdir('PoolData')
		if not os.path.isdir(os.getcwd()+'/PoolData/Shares'): 
			os.mkdir('PoolData/Shares')		# local files to be duplicated by peers
		if not os.path.isdir(os.getcwd()+'/PoolData/Work'):
			os.mkdir('PoolData/Work')		# where to put results of work requests
		if not os.path.isdir(os.getcwd()+'/PoolData/Status'):
			os.mkdir('PoolData/Status')		# place to track progress of work/operations
		if not os.path.isdir(os.getcwd()+'/PoolData/Signals'):
			os.mkdir('PoolData/Signals')	# track state to prevent miscommunications

	def synchronize_workload(self, verbose):
		jobs = {}
		# read through PoolData/Status to see if anything is ready to transmit
		for job in os.listdir(os.getcwd()+'/PoolData/Status'):
			job_state = utils.parse_status_file(os.getcwd()+'/PoolData/Status/'+job)
			jobs[job] = job_state
			# Check if job is COMPLETE
			if 'COMPLETE' in job_state.keys() and verbose:
				completed = job_state['COMPLETE'].upper()
				if completed == 'TRUE':
					print('[*] %s has completed' % job)
			if verbose:	# else (if verbose) report Job properties
				print('[*] %s SUMMARY' % job)
				for k in job_state.keys():
					print('%s: %s' % (k, job_state[k]))
		return jobs

	def index_local_shares(self):
		files = {}
		for f in os.listdir(os.getcwd()+'/PoolData/Shares'):
			fhash = utils.cmd('sha256sum PoolData/Shares/%s' % f,False).pop().split(' ')[0]
			files[fhash] = f
		return files


	def populate_info(self, local_files):
		ldate, ltime = utils.create_timestamp()
		self.info['START'] = ldate
		self.info['NSHARES'] = len(local_files.keys())
		previous_info = self.load_node_info()
		# TODO: Update as needed
		if 'START' in previous_info.keys():
			if ldate != previous_info['START']:
				self.info['LAST_RUN'] = previous_info['START']
		self.info['RUNNING'] = True


	def log_work(self, process_name, completed, workdict):
		fpath = os.getcwd()+'/PoolData/Status/%s' % process_name
		content = 'NAME=%s\n' % process_name
		content += 'COMPLETE=%s\n' % str(completed)
		arr = []
		for field in workdict.keys():
			if field != '':
				f = str(field).upper()
				# check types? or is that too slow
				v = str(workdict[field])
				arr.append('%s=%s' % (f, v))
		content += '\n'.join(arr)
		# write content 
		open(fpath, 'w').write(content)


	def shutdown(self):
		ldate, ltime = utils.create_timestamp()
		if 'RUNNING' in self.info.keys():
			self.info['RUNNING'] = False
		self.log_work('node.py', True, self.info)

	def create_job(self, process_name):
		# Create Job Method 
		ldate, ltime = utils.create_timestamp()
		job = {}
		job['NAME'] = process_name
		job['COMPLETE'] = False
		job['START'] = ldate
		job['RUNNING'] = False
		self.log_work(process_name, False, job)
	
	def update_job(self,name, field, value):
		# Update Job Status
		if os.path.isfile(os.getcwd()+'/PoolData/Status/%s' % name):
			j = utils.parse_status_file(os.getcwd()+'/PoolData/Status/%s' % name)
			if field in j.keys():
				j[field] = value
				self.log_work(name, j['COMPLETE'], j)
		else:
			print('[!!] Cannot find %s' % name)

	# TODO: Start Work Method 
	# TODO: Log/Report Work Data
	

def main():
	cell = Node()
	cell.shutdown()

if __name__ == '__main__':
	main()
