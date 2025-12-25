"""
METASPACE CORE ENGINE - VERSION 1.3 (SOVEREIGN SWARM)
Szabadalmi oltalom alatt: OSIM 20251221-2230
Feltaláló: Laszlo-Ferenc Szoke

Ez a végső modul integrálja a Temporal Determinism (Időbeli determinizmus), 
a Swarm Consensus (Raj-konszenzus) és az Energy Metabolism (Energia-kezelés) rétegeket.
"""

import time
import re

class TemporalGuard:
    """
    Időbeli Integritás: Ellenőrzi, hogy az adatok frissek-e.
    A valós idejű rendszerekben a késő válasz = hiba.
    """
    @staticmethod
    def check_staleness(timestamp, threshold_ms=100):
        current_ms = int(time.time() * 1000)
        delay = current_ms - timestamp
        return delay <= threshold_ms

class SwarmConsensus:
    """
    Raj-Integritás: Ha több MetaSpace sejt van jelen, 
    konszenzust kell kötniük a valóságról.
    """
    @staticmethod
    def verify_swarm(local_data, peer_data_list):
        # Egyszerűsített Bizánci Hibatűrés (BFT) logika
        agreements = 0
        threshold = len(peer_data_list) * 0.6 # 60%-os többség kell
        
        for peer_data in peer_data_list:
            # Ha a társak adatai 5%-on belül vannak
            if abs(local_data - peer_data) / local_data < 0.05:
                agreements += 1
        
        return agreements >= threshold

class SovereignCompiler:
    """
    A legmagasabb szintű fordító, amely egyesíti 
    a fizikai, fuzzy, időbeli és közösségi szabályokat.
    """
    def __init__(self, rules):
        self.rules = rules

    def compile_sovereign_logic(self):
        """
        Generálja a 'Sovereign Shield' kódot.
        """
        code = "def metaspace_sovereign_shield(sensors, swarm_peers, cmd_time):\n"
        code += "    # 1. TEMPORAL CHECK (Időbeli horgony)\n"
        code += "    if not TemporalGuard.check_staleness(cmd_time):\n"
        code += "        return 'REJECTED: TEMPORAL_STALENESS_DETECTED'\n\n"
        
        code += "    # 2. SWARM CONSENSUS (Közösségi hitelesítés)\n"
        code += "    local_dist = sensors['distance']\n"
        code += "    if not SwarmConsensus.verify_swarm(local_dist, swarm_peers):\n"
        code += "        return 'REJECTED: SWARM_DISSENT_DETERMINED'\n\n"
        
        code += "    # 3. METABOLIC CHECK (Energia-invariáns)\n"
        code += "    if sensors['battery'] < 15.0:\n"
        code += "        return 'FORCE_ACTION: LANDING_PROCEDURE_INITIATED'\n\n"
        
        code += "    # 4. TRADITIONAL INVARIANTS (Alap invariánsok)\n"
        code += "    if sensors['distance'] > 50.0:\n"
        code += "        return 'REJECTED: DISTANCE_INVARIANT_VIOLATION'\n"
        
        code += "\n    return 'EXECUTED: COMMAND_AUTHENTICATED'\n"
        return code

# --- SZIMULÁCIÓ: A SZUVERÉN RAJ MŰKÖDÉSE ---
if __name__ == "__main__":
    rules = {"cell_name": "SovereignDrone", "invariants": ["distance < 50"]}
    compiler = SovereignCompiler(rules)
    
    # Generált kód betöltése
    sovereign_logic = compiler.compile_sovereign_logic()
    print("=== METASPACE SOVEREIGN SHIELD GENERATED ===")
    
    # Teszt környezet
    my_sensors = {"distance": 10.0, "battery": 80.0}
    peer_sensors = [10.1, 9.9, 10.5, 40.0] # Az utolsó drón hibás adatot ad
    current_timestamp = int(time.time() * 1000)
    
    exec(sovereign_logic)
    
    # 1. Teszt: Minden rendben
    res1 = locals()['metaspace_sovereign_shield'](my_sensors, peer_sensors, current_timestamp)
    print(f"\n[NORMAL OPERATION]: {res1}")
    
    # 2. Teszt: Régi adat (Stale data attack)
    res2 = locals()['metaspace_sovereign_shield'](my_sensors, peer_sensors, current_timestamp - 500)
    print(f"[STALE DATA ATTACK]: {res2}")
    
    # 3. Teszt: Raj-széthúzás (Ha a többség nem ért egyet)
    fake_peers = [100.0, 110.0, 95.0, 10.0]
    res3 = locals()['metaspace_sovereign_shield'](my_sensors, fake_peers, current_timestamp)
    print(f"[SWARM DISSENT]: {res3}")