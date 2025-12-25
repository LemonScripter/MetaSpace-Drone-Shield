"""
METASPACE SITL VALIDATION TOOL
Csatlakozik az ArduPilot SITL-hez (Mavlink), monitorozza a divergenciát 
és szimulálja a GPS Spoofing támadást.
"""

import time
from pymavlink import mavutil
from metaspace_core_engine import BioParser, FormalVerifier, MetaCompiler

# 1. SETUP: MetaSpace inicializálása
bio_spec = """
INVARIANT: distance < 50
STATE: SAFE
"""
rules = BioParser().parse(bio_spec)
compiler = MetaCompiler(rules)
# A generált védelmi logikát betöltjük a memóriába
exec(compiler.compile())

def run_sitl_validation(connection_string="udpin:localhost:14550"):
    print(f"Csatlakozás a szimulációhoz: {connection_string}")
    master = mavutil.mavlink_connection(connection_string)
    
    # Kapcsolat ellenőrzése
    master.wait_heartbeat()
    print("SITL Kapcsolat aktív. Monitoring indítása...")

    last_ins_pos = None
    
    try:
        while True:
            # 2. ADATGYŰJTÉS (Telemetry Acquisition)
            msg = master.recv_match(type=['GLOBAL_POSITION_INT', 'GPS_RAW_INT'], blocking=True)
            
            if msg.get_type() == 'GLOBAL_POSITION_INT':
                # Ez a "bizalmi" EKF pozíció (INS)
                last_ins_pos = (msg.lat / 1e7, msg.lon / 1e7)
                
            if msg.get_type() == 'GPS_RAW_INT' and last_ins_pos:
                # Ez a nyers (támadható) GPS pozíció
                raw_gps_pos = (msg.lat / 1e7, msg.lon / 1e7)
                
                # 3. METASPACE ELLENŐRZÉS (The Logic Lock)
                # Kiszámítjuk a divergenciát (egyszerűsített távolság)
                dist = ((last_ins_pos[0] - raw_gps_pos[0])**2 + (last_ins_pos[1] - raw_gps_pos[1])**2)**0.5 * 111320
                
                sensors = {"distance": dist}
                status = locals()['metaspace_logic_lock'](sensors, "MAV_CMD_NAV_WAYPOINT")
                
                if "REJECTED" in status:
                    print(f"[!!!] METASPACE LOGIC LOCK AKTÍV! Divergencia: {dist:.2f}m")
                    # Itt küldhetnénk parancsot a SITL-nek: RTL (Return to Launch)
                else:
                    print(f"[OK] Rendszer integritás rendben. Távolság: {dist:.2f}m", end='\r')

            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nValidáció leállítva.")

if __name__ == "__main__":
    # Megjegyzés: Ez a script akkor fut, ha elindítottad az ArduPilot SITL-t!
    # parancs: sim_vehicle.py -v ArduCopter
    run_sitl_validation()