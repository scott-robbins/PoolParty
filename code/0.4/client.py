from flask import Flask, render_template, redirect, url_for, request 
from threading import Thread
import base64
import master
import utils
import time
import sys 
import os 

NETWORK = master.Master()
app = Flask(__name__)


@app.route('/')
def load():
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

@app.route('/favicon.ico')
def icon():
    return open('templates/assets/icon.png', 'rb').read()

@app.route('/icon.png')
def logo():
    return open('templates/assets/icon.png', 'rb').read()

if __name__ == '__main__':
    # app.run('0.0.0.0', port=80)
	app.run(port=80)
