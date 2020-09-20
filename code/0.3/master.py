from flask import Flask, render_template, redirect, url_for, request
import control 
import routing 
import storage 
import utils
import setup
import time 
import sys 
import os 

app = Flask(__name__)

class Settings:
	opt_file = 'master.config'
	default_name_color = 'blue';
	default_name_font = 'Bungee Hairline'
	default_dash_color = 'deaddd'
	default_tool_color = 'bbaaddd'
	peers = {}

	def __init__(self):
		self.initialize()

	def initialize(self):
		# Load info about self
		if not os.path.isdir(os.getcwd()+'/PoolData/Local/'):
			os.mkdir('PoolData/Local/')
			print '[*] No Configurations found. Running Default Layout'
				# Load Info About Nodes/Network
		if os.path.isfile(os.getcwd()+'/PoolData/NX/peerlist.txt'):
			print '[*] Found peerlist'
			peers = utils.swap(os.getcwd()+'/PoolData/NX/peerlist.txt',False)
			for peer in peers:
				pName = peer.split('\n')[0]
				self.peers[pName] = {}
		if os.path.isfile(os.getcwd()+'/PoolData/Local/settings_avatars.conf'):
			print '[*] Loading GUI Configurations'
			config = utils.swap(os.getcwd()+'/PoolData/Local/settings_avatars.conf',False)
			for line in config:
				peer = line.split(' ')[0]
				avatar = line.split(' ')[1].replace('\n','')
				print os.getcwd()+avatar
				if os.path.isfile(os.getcwd()+'/templates/assets/'+avatar):
					self.peers[peer]['avatar'] = avatar
					print '%s has avatar %s' % (peer, avatar)
		else:
			# DEFAULT AVATAR
			self.peers[peer]['avatar'] = 'server.png'

@app.route('/')
def load():
	return render_template('loading.html')

@app.route('/home')
def home():
	# Check in with the network to show nodes available and network info
	preferences = Settings()
	localt, locald = utils.create_timestamp()
	utils.refresh_peers()
	fastest, best_time, timing = setup.test_pool(verbose=False)
	# Basic info to show
	# * N Nodes Online
	n_nodes = len(timing.keys())
	# * N Files Shared
	n_files = len(os.listdir('PoolData/Shares'))
	# * N Active Jobs
	if not os.path.isdir(os.getcwd()+'/PoolData/Jobs/'):
		n_jobs = 0
	else:
		n_jobs = len(os.listdir(os.getcwd()+'/PoolData/Jobs'))
	peer_data = {}
	for peer in preferences.peers.keys():
		hostname = ''
		internal = ''
		external = ''
		content, info = control.show_info(peer, False)
		if 'hostname' in info.keys():
			hostname = info['hostname']
		if 'internal' in info.keys():
			internal = info['internal']
		if 'external' in info.keys():
			external = info['external']
		peer_data[peer] = info
	return render_template('home.html', uname_color=preferences.default_name_color,
										uname_font=preferences.default_name_font,
										dash_hex=preferences.default_dash_color,
										user_toolbar=preferences.default_tool_color,
										ping_data=timing,
										current_date=locald,
										current_time=localt,
										n_peers=n_nodes,
										n_files=n_files,
										n_jobs=n_jobs)
@app.route('/Nodes')
def node_list():
	preferences = Settings()
	return render_template('nodes.html', peers=preferences.peers)

@app.route('/Nodes/<peer>')
def display_node_info(peer):
	preferences = Settings()
	poolpath = '/PoolParty/code/0.3'
	if peer in preferences.peers.keys():
		print '[*] Loading %s Peer Data' % (peer)
		hname, ip, pword, pk = setup.load_credentials(peer, False)
		if hname == 'root':
			rpath = '/root' + poolpath
		else:
			rpath = '/home/%s%s' % (hname,poolpath)
		content, info = control.show_info(peer, False)
		print '[*] Reply from %s: %s' % (ip,info)
		hostname = ''
		internal = ''
		external = ''
		if 'hostname' in info.keys():
			hostname = info['hostname']
		if 'internal' in info.keys():
			internal = info['internal']
		if 'external' in info.keys():
			external = info['external']
		return render_template('peer.html', 
							   name=peer,
							   hostname=hostname,
							   internal=internal,
							   external=external,
							   avatar=preferences.peers[peer]['avatar'])

@app.route('/Settings')
def customize_settings():
	# This is where users can customize the day CSS a bit 
	# Check in with the network to show nodes available and network info
	preferences = Settings()
	return render_template('settings.html', peers=preferences.peers)

@app.route('/Upload')
def upload_file():
	return render_template('upload.html')

@app.route('/Download')
def download_file():
	return render_template('download.html')

@app.route('/Jobs')
def show_active_jobs():
	return render_template('active_jobs.html')

@app.route('/Logs')
def show_logs():
	return render_template('logs.html')

@app.route('/favicon.ico')
def icon():
    return open('templates/assets/icon.png', 'rb').read()

@app.route('/icon.png')
def logo():
    return open('templates/assets/icon.png', 'rb').read()

@app.route('/AddNode', methods=['GET','POST'])
def add_node():
	# TODO: The submission for this isnt working? Creates weird link
	return render_template('add_node.html')

# Server Avatars 
@app.route('/Nodes/camera.png')
def serve_camera():
	return open(os.getcwd()+'/templates/assets/camera.png','rb').read()


@app.route('/Nodes/server.png')
def serve_server():
	return open(os.getcwd()+'/templates/assets/server.png','rb').read()


@app.route('/Nodes/speaker.png')
def serve_server():
	return open(os.getcwd()+'/templates/assets/speaker.png','rb').read()

@app.route('/Nodes/gpu.png')
def serve_gpu():
	return open(os.getcwd()+'/templates/assets/gpu.png','rb').read()

if __name__ == '__main__':
    app.run(port=80)
