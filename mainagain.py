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
    oldState = False
    while True:
        time.sleep(0.85)
        state = get_state_managed_queue()
        
        if state == False:
            socketio.emit('newState', {'data': 'NEUTRAL'}, namespace='/test')
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
    return render_template('indexAgain.html')
	

@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})



	
if __name__ == '__main__':
    socketio.run(app)