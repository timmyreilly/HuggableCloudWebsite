from gevent import monkey
monkey.patch_all()

import time
from threading import Thread
from flask import Flask, render_template, session, request
from flask.ext.socketio import SocketIO, emit, join_room, leave_room, \
    close_room, disconnect

from helperFunctions import *

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread = None

def background_work():
    """ Let's do it again with the trial example"""
    print 'in background_trial'
	oldState = False
    while True:
        time.sleep(1)
		state = get_state_managed_queue()
		
		if state == False:
			socketio.emit('newstate', {'data': 'NEUTRAL'}, namespace='/test')
			continue
		else:
			socketio.emit('newState', {'data': state}, namespace='/test')
			oldState = state
			continue

@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_work)
        thread.start()
    return render_template('indexagain.html')
	

@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')
	
if __name__ == '__main__':
    socketio.run(app)