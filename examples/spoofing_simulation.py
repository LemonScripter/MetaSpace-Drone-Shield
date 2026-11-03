"""
MetaSpace Pro - Drone Simulation Server (Professional Edition)
---------------------------------------------------------
1. Web Server: Streams data to index.html (Port 5000)
2. Local Plot: Opens a real-time Matplotlib window
Status: 'Shield Engaged' / 'Verified Safe'
ILLUSTRATIVE SIMULATION with synthetic data. The alarm below is a plain threshold in Python; it is not the verified gate (see src/ and docs/validation/).
"""

import numpy as np
import json
import time
import http.server
import socketserver
import threading
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from http import HTTPStatus

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
        
        # History for local Matplotlib window
        self.history_t = []
        self.history_gps = []
        self.history_ins = []

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

        # Store history
        self.history_t.append(self.clock)
        self.history_gps.append(self.gps_x)
        self.history_ins.append(self.ins_x)
        
        if len(self.history_t) > 120:
            self.history_t.pop(0)
            self.history_gps.pop(0)
            self.history_ins.pop(0)

    def get_telemetry(self):
        return {
            "time": round(self.clock, 1),
            "gps": round(self.gps_x, 2),
            "ins": round(self.ins_x, 2),
            "divergence": round(self.divergence, 2),
            "alert": self.alarm_active,
            "status": "Alarm (divergence > 50 m)" if self.alarm_active else "No alarm"
        }

uav_logic = MetaSpaceSimulator()

# --- WEB SERVER ---
class TelemetryAPI(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def do_GET(self):
        if self.path == '/telemetry':
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(uav_logic.get_telemetry()).encode())
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

def start_server_thread():
    PORT = 5000
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("127.0.0.1", PORT), TelemetryAPI) as httpd:
            print(f"[METASPACE] API Server active at http://127.0.0.1:{PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"[ERROR] {e}")

# --- LOCAL MONITOR ---
def run_local_visualization():
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    line_gps, = ax.plot([], [], color='#ef4444', linestyle='--', label='GPS Measurement', alpha=0.8)
    line_ins, = ax.plot([], [], color='#10b981', label='Trusted INS Path', linewidth=2)
    
    ax.set_xlabel("Mission Time (s)")
    ax.set_ylabel("Position (m)")
    ax.legend(loc='upper left')
    ax.grid(alpha=0.1)

    def update(frame):
        uav_logic.step()
        data = uav_logic.get_telemetry()
        
        line_gps.set_data(uav_logic.history_t, uav_logic.history_gps)
        line_ins.set_data(uav_logic.history_t, uav_logic.history_ins)
        
        ax.relim()
        ax.autoscale_view()
        
        status_color = '#ef4444' if data["alert"] else '#10b981'
        ax.set_title(f"MetaSpace Monitor | Status: {data['status']} | T+{data['time']}s", 
                     color=status_color, fontweight='bold', pad=20)
        
        return line_gps, line_ins

    ani = FuncAnimation(fig, update, interval=500)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    threading.Thread(target=start_server_thread, daemon=True).start()
    print("[METASPACE] Launching Mission Control Hub...")
    run_local_visualization()