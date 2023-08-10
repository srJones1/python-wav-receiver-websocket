from flask import Flask,json,request,abort, jsonify
from flask import Response
import uuid
import wave
from flask import Blueprint, current_app, session, url_for, render_template
from flask_socketio import emit
from flask_socketio import SocketIO

app=Flask(__name__)
socketio = SocketIO(app)

app.config['FILEDIR'] = 'static/audios/'

@app.route('/', methods=['GET'])
def index():
    """Return the client application."""
    return render_template('main.html')


@socketio.on('start-recording', namespace='/audio')
def start_recording(options):
    """Start recording audio from the client."""
    id = uuid.uuid4().hex  # server-side filename
    session['wavename'] = id + '.wav'
    wf = wave.open(current_app.config['FILEDIR'] + session['wavename'], 'wb')
    wf.setnchannels(options.get('numChannels', 1))
    wf.setsampwidth(options.get('bps', 16) // 8)
    wf.setframerate(options.get('fps', 44100))
    session['wavefile'] = wf


@socketio.on('write-audio', namespace='/audio')
def write_audio(data):
    """Write a chunk of audio from the client."""
    session['wavefile'].writeframes(data)


@socketio.on('end-recording', namespace='/audio')
def end_recording():
    """Stop recording audio from the client."""
    emit('add-wavefile', url_for('static',
                                 filename='audios/' + session['wavename']))
    session['wavefile'].close()
    del session['wavefile']
    del session['wavename']
      

""" Main """
if __name__== '__main__':
  #app.run(host='0.0.0.0',debug=True)
  socketio.run(app, host='0.0.0.0', port=5000)