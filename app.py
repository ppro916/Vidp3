from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/<room_id>')
def admin(room_id):
    return render_template('admin.html', room_id=room_id)

@app.route('/user/<room_id>')
def user(room_id):
    return render_template('user.html', room_id=room_id)

@socketio.on('join')
def on_join(data):
    room = data['room_id']
    join_room(room)
    print(f"User joined room: {room}")

@socketio.on('leave')
def on_leave(data):
    room = data['room_id']
    leave_room(room)
    print(f"User left room: {room}")

@socketio.on('webrtc_offer')
def handle_offer(data):
    room = data['room_id']
    emit('webrtc_offer', data, room=room, include_self=False)

@socketio.on('webrtc_answer')
def handle_answer(data):
    room = data['room_id']
    emit('webrtc_answer', data, room=room, include_self=False)

@socketio.on('webrtc_ice_candidate')
def handle_ice_candidate(data):
    room = data['room_id']
    emit('webrtc_ice_candidate', data, room=room, include_self=False)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
