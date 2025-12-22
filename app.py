"""
MetaSpace Pro - Drone Simulation Server (Railway Deployment)
---------------------------------------------------------
Web Server: Streams data to index.html
Status: 'Shield Engaged' / 'Verified Safe'
"""

import numpy as np
import json
import time
import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.')
CORS(app)

# --- SIMULATION ENGINE ---
class MetaSpaceSimulator:
    def __init__(self):
        self.clock = 0
        self.tick_rate = 0.5
        self.true_x = 0
        self.ins_x = 0
        self.gps_x = 0
        self.divergence = 0
        self.alarm_active = False
        self.invariant_threshold = 50.0

    def step(self):
        self.clock += self.tick_rate
        self.true_x = self.clock * 15.0
        self.ins_x = self.true_x + np.random.normal(0, 0.15)
        
        # Attack Scenarios
        if self.clock < 20:
            self.gps_x = self.true_x + np.random.normal(0, 1.8)
        elif 20 <= self.clock < 40:
            self.gps_x = self.true_x - (self.clock - 20) * 48.0
        else:
            self.gps_x = self.true_x + 850.0 
            
        self.divergence = abs(self.gps_x - self.ins_x)
        
        # Latch logic: once engaged, stay engaged for safety
        if self.divergence > self.invariant_threshold:
            self.alarm_active = True

    def get_telemetry(self):
        return {
            "time": round(self.clock, 1),
            "gps": round(self.gps_x, 2),
            "ins": round(self.ins_x, 2),
            "divergence": round(self.divergence, 2),
            "alert": self.alarm_active,
            "status": "Shield Engaged" if self.alarm_active else "Verified Safe"
        }

# Global simulator instance
uav_logic = MetaSpaceSimulator()

# Update simulator in background
import threading
def update_simulator():
    while True:
        uav_logic.step()
        time.sleep(0.5)

simulator_thread = threading.Thread(target=update_simulator, daemon=True)
simulator_thread.start()

# --- ROUTES ---
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/telemetry')
def telemetry():
    return jsonify(uav_logic.get_telemetry())

@app.route('/logo.png')
def logo():
    return send_from_directory('.', 'logo.png')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=False)

