"""
MetaSpace SITL Validation Tool
Connects to ArduPilot SITL (MAVLink), monitors GPS-INS divergence,
and validates GPS spoofing detection.
"""

import sys
import os
import time

# Add src/python to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src/python'))

from pymavlink import mavutil
from metaspace_core_engine import BioParser, FormalVerifier, MetaCompiler

# 1. SETUP: MetaSpace initialization
bio_spec = """
INVARIANT: distance < 50
STATE: SAFE
"""
rules = BioParser().parse(bio_spec)
compiler = MetaCompiler(rules)
# Load generated protection logic into memory
exec(compiler.compile())

def run_sitl_validation(connection_string="udpin:localhost:14550"):
    """
    Run SITL validation with MetaSpace GPS spoofing detection.
    
    Args:
        connection_string: MAVLink connection string (default: udpin:localhost:14550)
    
    Note: Start ArduPilot SITL before running this script:
        sim_vehicle.py -v ArduCopter
    """
    print(f"Connecting to simulation: {connection_string}")
    master = mavutil.mavlink_connection(connection_string)
    
    # Connection check
    master.wait_heartbeat()
    print("SITL connection active. Starting monitoring...")

    last_ins_pos = None
    
    try:
        while True:
            # 2. DATA ACQUISITION (Telemetry Acquisition)
            msg = master.recv_match(type=['GLOBAL_POSITION_INT', 'GPS_RAW_INT'], blocking=True)
            
            if msg.get_type() == 'GLOBAL_POSITION_INT':
                # This is the "trusted" EKF position (INS)
                last_ins_pos = (msg.lat / 1e7, msg.lon / 1e7)
                
            if msg.get_type() == 'GPS_RAW_INT' and last_ins_pos:
                # This is the raw (attackable) GPS position
                raw_gps_pos = (msg.lat / 1e7, msg.lon / 1e7)
                
                # 3. METASPACE VERIFICATION (Invariant-based logic lock)
                # Calculate divergence (simplified distance)
                dist = ((last_ins_pos[0] - raw_gps_pos[0])**2 + 
                       (last_ins_pos[1] - raw_gps_pos[1])**2)**0.5 * 111320
                
                sensors = {"distance": dist}
                status = locals()['metaspace_logic_lock'](sensors, "MAV_CMD_NAV_WAYPOINT")
                
                if "REJECTED" in status:
                    print(f"[!!!] METASPACE LOGIC LOCK ENGAGED! Divergence: {dist:.2f}m")
                    # Here we could send command to SITL: RTL (Return to Launch)
                else:
                    print(f"[OK] System integrity OK. Distance: {dist:.2f}m", end='\r')

            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nValidation stopped.")

if __name__ == "__main__":
    # Note: This script requires ArduPilot SITL to be running
    # Command: sim_vehicle.py -v ArduCopter
    run_sitl_validation()

