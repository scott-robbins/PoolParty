from flask import Flask, render_template, redirect, url_for, request 
from threading import Thread
import storage
import base64
import master
import utils
import time
import sys 
import os 

NETWORK = master.Master()
app = Flask(__name__)

# = = = = = = = = = Routes For Serving Main Pages  = = = = = = = = = # 
@app.route('/')
def load():
	# NETWORK = master.Master()
	# Loading Screen gives 2s to prepare homepage data
	return render_template('loading.html')

@app.route('/home')
def homepage():
	preferences = NETWORK.preferences
	localt, locald = utils.create_timestamp()
	# N Nodes online
	n_nodes = len(NETWORK.nodes)
	# N Shared Files
	n_files = len(NETWORK.hashes.keys())
	# N Active Jobs
	if not os.path.isdir(os.getcwd()+'/PoolData/Jobs/'):
		n_jobs = 0
	else:
		n_jobs = len(os.listdir(os.getcwd()+'/PoolData/Jobs'))
	# Mean Ping Time? Download/upload bitrates?
	return render_template('home.html', uname_color=preferences.default_name_color,
										uname_font=preferences.default_name_font,
										dash_hex=preferences.default_dash_color,
										user_toolbar=preferences.default_tool_color,
										ping_data=NETWORK.timing,
										current_date=locald,
										current_time=localt,
										n_peers=n_nodes,
										n_files=n_files,
										n_jobs=n_jobs)

@app.route('/Nodes')
def node_list():
	preferences = NETWORK.preferences
	localt, locald = utils.create_timestamp()
	return render_template('nodes.html', peers=preferences.peers,
										 current_date=locald,
							   			 current_time=localt)


@app.route('/AddNode', methods=['GET','POST'])
def create_node_form():
	# localt, locald = utils.create_timestamp()
	if request.method == 'POST':
		print 'Adding Node with info:'
		try:
			pn = request.form['pname']
			hn =  request.form['hname']
			ip = request.form['ipaddr']
			pw = request.form['pword']
			av = request.form['avatar']
			content = 'IPAddress=%s\nPassword=%s\n' % (ip,pw)
			content+= 'Username=%s\nHostname=%s\n' % (pn, hn)
			open('newhost.txt','wb').write(content)
			open('PoolData/Local/settings_avatars.conf','a').write('%s %s' % (pn, av))
			os.system('python core.py --add_configured newhost.txt')
			NETWORK = master.Master()
			return redirect(url_for('/'))
		except:
			pass
	else:
		return render_template('add_node.html')

@app.route('/Downloads')
def view_sharefiles():
	preferences = NETWORK.preferences
	database = storage.MasterRecord()
	shares = database.display_file_tree(os.getcwd()+'/PoolData/Shares')
	localt, locald = utils.create_timestamp()
	return render_template('downloads.html', shared=shares,
											user_toolbar=preferences.default_tool_color,
											current_date=locald,
							   				current_time=localt)

# = = = = = = = = = Routes For Serving Static Resources = = = = = = = = = # 

@app.route('/favicon.ico')
def icon():
    return open('templates/assets/icon.png', 'rb').read()

@app.route('/icon.png')
def logo():
    return open('templates/assets/icon.png', 'rb').read()

# Server Avatars 
@app.route('/camera.png')
def serve_camera():
	return open(os.getcwd()+'/templates/assets/camera.png','rb').read()

@app.route('/ubuntu.png')
def serve_ubuntu():
	return open(os.getcwd()+'/templates/assets/ubuntu.png', 'rb').read()

@app.route('/server.png')
def serve_server():
	return open(os.getcwd()+'/templates/assets/server.png','rb').read()


@app.route('/speaker.png')
def serve_speaker():
	return open(os.getcwd()+'/templates/assets/speaker.png','rb').read()

@app.route('/gpu.png')
def serve_gpu():
	return open(os.getcwd()+'/templates/assets/gpu.png','rb').read()

@app.route('/monitor.png')
def serve_monitor():
	return open(os.getcwd()+'/templates/assets/monitor.png', 'rb').read()

@app.route('/kali.png')
def serve_kali():
	return open(os.getcwd()+'/templates/assets/kali.png','rb').read()

if __name__ == '__main__':
    # app.run('0.0.0.0', port=80)
	app.run(port=80)
