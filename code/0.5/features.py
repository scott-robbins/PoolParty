import network
import utils
import os 

def is_raspberry():
	pi = False
	os_ver = os.uname()
	if 'armv7l' in os_ver or 'raspberry' in os_ver:
		pi = True
	return pi

def has_camera():
	hascam = False
	result = utils.cmd('vcgencmd get_camera',False).pop().split(' ')
	supported = int(result[0].split('=')[1])
	detected = int(result[0].split('=')[1])
	return (detected == 1)

def snap_img(im_out):
	os.system('raspistill -t 1 -o %s' % im_out)
	c = '[ ! -e %s ]; echo $?' % im_out
	if int(utils.cmd(c,False).pop()) == 1:
		return True
	else:
		return False

def stream_vid(port):
	stream_vid = 'raspivid -t 0 -w 1280 -h 720 -fps 20 -o - | nc -l -k %d' % port
	time_streaming = 0.0
	# watch_stream with 'mplayer -fps 20 -demuxer h264es ffmpeg://tcp://'	
	if is_raspberry() and has_camera():
		start = time.time()
		os.system(stream_vid)	# This will not return until stream is closed
		time_streaming = time.time() - start
	return time_streaming

def watch_stream(ip, port):
	watchcmd= 'mplayer -fps 20 -demuxer h264es ffmpeg://tcp://%s:%d' % (ip, port)
	time_watched = 0.0
	try:
		start = time.time()
		os.system(watchcmd)		# This will not return until stream is closed
		time_watched = time.time() - start
	except:
		pass
	return time_watched