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

	def __init__(self, nodes):
		self.workers = nodes

	def run(self):

		while len(self.task_list):
			for node_name in self.workers.keys():
				# check in on worker
				checkCmd = 'ls /home/%s/PoolParty/code/0.5/PoolData/Work/'
				# see if they have jobs finished
			# Check if more tasks have been added to the queue
		
