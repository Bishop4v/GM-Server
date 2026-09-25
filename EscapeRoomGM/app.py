from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'escape-room-secret'

socketio = SocketIO(app, async_mode='threading')


# ROOM CONFIGURATION


ROOMS = {
    "Room 1": {
        "name": "Maintenance Room",
        "controller": "Ronnie ESP32",
        "plc": "Maintenance PLC"
    },

    "Room 2": {
        "name": "Tron Room",
        "controller": "Tron PLC",
        "plc": "Tron PLC"
    },

    "Room 3": {
        "name": "Temple Room",
        "controller": "Winston ESP32",
        "plc": "Temple PLC"
    },

    "Room 4": {
        "name": "Haunted House Room",
        "controller": "Demogorgon ESP32",
        "plc": "Haunted House PLC"
    }
}


# ROOM STATUS

room_status = {
    "Room 1": {
        "controller": False,
        "plc": False,
        "phase": "Waiting",
        "details": ""
    },

    "Room 2": {
        "controller": False,
        "plc": False,
        "phase": "Waiting",
        "details": ""
    },

    "Room 3": {
        "controller": False,
        "plc": False,
        "phase": "Waiting",
        "details": ""
    },

    "Room 4": {
        "controller": False,
        "plc": False,
        "phase": "Waiting",
        "details": ""
    }
}


# WEB PAGE

@app.route('/')
def index():
    return render_template(
        'index.html',
        rooms=ROOMS
    )


# CONNECTION STATUS

@socketio.on('update_connection')
def handle_connection_update(data):

    room = data.get('room')
    device = data.get('device')
    connected = data.get('status', False)

    if room not in room_status:
        print(f"Unknown room: {room}")
        return

    if device not in ['controller', 'plc']:
        print(f"Unknown device type: {device}")
        return

    room_status[room][device] = connected

    print(
        f"{room} - {device}: "
        f"{'ONLINE' if connected else 'OFFLINE'}"
    )

    socketio.emit(
        'status_update',
        room_status
    )


# GM COMMANDS

@socketio.on('trigger_action')
def handle_action(data):

    room = data.get('room')
    action = data.get('action')

    if room not in ROOMS:
        print(f"Unknown room: {room}")
        return

    if not action:
        print("No action supplied")
        return

    print("=" * 60)
    print("GM COMMAND")
    print(f"Room:   {ROOMS[room]['name']}")
    print(f"Action: {action}")
    print("=" * 60)

    
    socketio.emit(
        'execute_hardware_action',
        {
            'room': room,
            'action': action
        }
    )


# UPDATE ROOM PHASE

@socketio.on('update_phase')
def handle_phase_update(data):

    room = data.get('room')
    phase = data.get('phase')
    details = data.get('details', '')

    if room not in room_status:
        print(f"Unknown room: {room}")
        return

    room_status[room]['phase'] = phase
    room_status[room]['details'] = details

    print(
        f"{ROOMS[room]['name']} phase: "
        f"{phase}"
    )

    socketio.emit(
        'status_update',
        room_status
    )


# RESET ROOM

@socketio.on('reset_room')
def handle_reset_room(data):

    room = data.get('room')

    if room not in room_status:
        print(f"Unknown room: {room}")
        return

    room_status[room]['phase'] = "Waiting"
    room_status[room]['details'] = "Room reset to default state"

    print(
        f"RESET: {ROOMS[room]['name']}"
    )

    socketio.emit(
        'execute_hardware_action',
        {
            'room': room,
            'action': 'reset_room'
        }
    )

    socketio.emit(
        'status_update',
        room_status
    )


# START SERVER

if __name__ == '__main__':

    print()
    print("=" * 60)
    print("ESCAPE ROOM GM CONTROL CENTER")
    print("=" * 60)
    print("Server: http://127.0.0.1:5000")
    print("=" * 60)
    print()

    socketio.run(
        app,
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=False,
        allow_unsafe_werkzeug=True
    )
