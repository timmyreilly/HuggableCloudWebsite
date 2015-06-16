#main.py

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
    """Copy of background thread with better logic for cloud """
    print "in background_work"
    oldState = False
    while True:
        time.sleep(1)
        state = get_state_managed_queue()
        if state == False:
            socketio.emit('updater', {'data': 'NEUTRAL'}, namespace='/test')
        else:
            socketio.emit('updater', {'data': state}, namespace='/test')
            oldState = state
        
        if oldState == False:
            #nothing going on. If queue hasn't started this should happen
            socketio.emit('updater', {'data': '...'}, namespace='/test')
            
        

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    print 'in background_thred'
    while True:
        time.sleep(1)
        t = str(time.clock())
        print 'current t value: '
        print t
        state = get_state_managed_queue()
        print state
        if state == False:
            #no state ready to be displayed
            socketio.emit('updater', {'data': '...'}, namespace='/test')
        else:
            socketio.emit('updater', {'data': state}, namespace='/test')
        
        socketio.emit('my time', {'data': t}, namespace='/test')
      


@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_work)
        thread.start()
    return render_template('index.html')


@socketio.on('my event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my broadcast event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.on('join', namespace='/test')
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'In rooms: ' + ', '.join(request.namespace.rooms),
          'count': session['receive_count']})


@socketio.on('leave', namespace='/test')
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'In rooms: ' + ', '.join(request.namespace.rooms),
          'count': session['receive_count']})


@socketio.on('close room', namespace='/test')
def close(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         room=message['room'])
    close_room(message['room'])


@socketio.on('my room event', namespace='/test')
def send_room_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']},
         room=message['room'])


@socketio.on('disconnect request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)

