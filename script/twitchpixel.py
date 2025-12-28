import socket, re, random, threading
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

CHANNEL = 'laumehdi' 

def twitch_bot():
    irc = socket.socket()
    irc.connect(('irc.chat.twitch.tv', 6667))
    irc.send(f"NICK justinfan{random.randint(100,999)}\r\n".encode())
    irc.send(f"JOIN #{CHANNEL}\r\n".encode())
    
    while True:
        try:
            resp = irc.recv(2048).decode('utf-8')
            if resp.startswith('PING'): irc.send("PONG\r\n".encode())
            match = re.search(r':(.*?)!.*?PRIVMSG #.*? :(.*)', resp)
            if match:
                user, msg = match.group(1).lower(), match.group(2).strip()
                if msg.startswith("!dibujar "):
                    code = msg.split(" ", 1)[1].strip()
                    socketio.emit('new_drawing', {'user': user, 'code': code})
                if user == CHANNEL:
                    if msg.startswith("!borrar "):
                        target = msg.replace("!borrar ", "").strip().lower().replace('@', '')
                        socketio.emit('mod_action', {'type': 'delete_user', 'target': target})
                    elif msg == "!limpiar":
                        socketio.emit('mod_action', {'type': 'clear_all'})
        except: pass

@app.route('/')
def index(): return render_template('stream.html')

if __name__ == '__main__':
    threading.Thread(target=twitch_bot, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
