import socket
import re
import random
from flask import Flask, render_template
from flask_socketio import SocketIO
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

CHANNEL = 'laumehdi' 
SERVER = 'irc.chat.twitch.tv'
PORT = 6667
NICK = f"justinfan{random.randint(10000, 99999)}"

def twitch_bot():
    irc = socket.socket()
    irc.connect((SERVER, PORT))
    irc.send(f"NICK {NICK}\r\n".encode('utf-8'))
    irc.send(f"JOIN #{CHANNEL}\r\n".encode('utf-8'))
    
    while True:
        try:
            resp = irc.recv(2048).decode('utf-8')
            if resp.startswith('PING'):
                irc.send("PONG\r\n".encode('utf-8'))
                continue
            
            match = re.search(r':(.*?)!.*?PRIVMSG #.*? :(.*)', resp)
            if match:
                user = match.group(1).lower()
                msg = match.group(2).strip()

                if msg.startswith("!dibujar "):
                    draw_code = msg.replace("!dibujar ", "").strip()
                    socketio.emit('new_drawing', {'user': user, 'code': draw_code})

                if user == CHANNEL:
                    if msg.startswith("!borrar "):
                        target = msg.replace("!borrar ", "").strip().lower().replace('@', '')
                        socketio.emit('mod_action', {'type': 'delete_user', 'target': target})
                    elif msg == "!limpiar":
                        socketio.emit('mod_action', {'type': 'clear_all'})
        except:
            pass

@app.route('/')
def index():
    return render_template('stream.html')

if __name__ == '__main__':
    threading.Thread(target=twitch_bot, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
