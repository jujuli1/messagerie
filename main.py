from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
socketio = SocketIO(app, logger=True, engineio_logger=True)
connected_users = {}

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/chat', methods=["POST"])
def chat():
    username = request.form['username']
    room = request.form['room']
    return render_template("chat.html", username=username, room=room)

@socketio.on('connect')
def on_connect():
    pass

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    connected_users[request.sid] = (username, room)
    join_room(room)
    emit('connected_users', get_connected_users(room), room=room)

@socketio.on('disconnect')
def on_disconnect():
    if request.sid in connected_users:
        username, room = connected_users[request.sid]
        leave_room(room)
        del connected_users[request.sid]
        emit('connected_users', get_connected_users(room), room=room)

@socketio.on("chat message")
def handle_chat(json):
    json['username'] = connected_users[request.sid][0]
    emit("chat message", json, broadcast = True, include_self = False, to = json['room'])

def get_connected_users(room):
    return {sid: user for sid, user in connected_users.items() if user[1] == room}

if __name__ == "__main__":
    socketio.run(app, debug=True)
