from flask import Flask, request
from flask_cors import CORS
import threading
import time
import json

import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # отключаем обычные HTTP-логи

orientation_data = {
    'y': 0,
    'p': 0,
    'r': 0
}

ps_true = ""

app = Flask(__name__)
CORS(app)

@app.route('/data', methods=['GET'])
def data():
    ps = request.args.get('text', 'none')
    print("GET_Password:", ps)
    if ps == ps_true:
        return 'Password is correct'
    else:
        return 'Wrong password'

@app.route('/update', methods=['POST'])
def update():
    data = request.json
    
    password = data.get('ps', 0)
    
    if password == ps_true:
        
        orientation_data['y'] = data.get('y', 0)
        orientation_data['p'] = data.get('p', 0)
        orientation_data['r'] = data.get('r', 0)
        
        with open("orientation.json", "w") as f:
            json.dump(orientation_data, f)

        return 'OK'
    else:
        return "Wrong"

def start():
    app.run(host="0.0.0.0", port=5000)

def main_loop():
    while True:
        
        yaw = orientation_data['y']
        pitch = orientation_data['p']
        roll = orientation_data['r']
        
        print(f"[LOOP] Yaw: {yaw:.2f}, Pitch: {pitch:.2f}, Roll: {roll:.2f}")
        
        time.sleep(0.1)

if __name__ == "__main__":
    threading.Thread(target=start, daemon=True).start()
    main_loop()
