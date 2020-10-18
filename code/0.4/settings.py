import utils
import core
import os

class Settings():
	opt_file = 'master.config'
	default_name_color = 'blue'
	default_name_font = 'Bungee Hairline'
	default_dash_color = 'deaddd'
	default_tool_color = 'bbaadd'
	peers = {}

	def __init__(self):
		self.initialize()

	def initialize(self):
		for n in core.get_node_names():
			self.peers[n] = {}

		if os.path.isfile(os.getcwd()+'/PoolData/Local/settings_avatars.conf'):
			config = utils.swap(os.getcwd()+'/PoolData/Local/settings_avatars.conf', False)
			for line in config:
				peer = line.split(' ')[0]
				avatar = line.split(' ')[1].replace('\n','')
				if os.path.isfile(os.getcwd()+'/templates/assets/'+avatar):
					self.peers[peer]['avatar'] = avatar
					# print '%s has avatar %s' % (peer, avatar)
		else:  # DEFAULT AVATAR
			self.peers[peer]['avatar'] = 'Server.png'
