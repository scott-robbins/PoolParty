import multiprocessing
import network
import random
import utils
import time
import sys 
import os


def Backend():
	INBOUND = 54123
	RUNNING = False
	start_date = ''
	start_time = ''
	peers = {}
	info = {}
	actions = {}

	def __init__(self):
		# Load Local Variables 
		h,e,i,s = setup.load_local_vars()
		self.info['host'] 		= h
		self.info['external'] 	= e
		self.info['internal']	= i
		self.info['server']		= s
		self.start_date, self.start_time = utils.create_time_stamp()
		# Setup Folders/Files 
		# Start Background Tasks
		# Create Listener 
		# Start listening for API Requests


def main():
	listener = Backend()

if __name__ == '__main__':
	main()
