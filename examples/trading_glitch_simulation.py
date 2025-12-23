import time
import json

# --- METASPACE PÉNZÜGYI SZIMULÁTOR ---
# Egy elszabadult algoritmus (HFT Glitch) megállítását szemlélteti

class FinancialLogicEngine:
    def __init__(self, balance=5000000):
        self.balance = balance
        self.exposure = 0
        self.orders_this_cycle = 0
        self.is_locked = False
        self.limit = balance * 0.20

    def check_metaspace_invariants(self, next_order_amount):
        """ Determinisztikus ellenőrzés a végrehajtás előtt. """
        
        # 1. Invariáns: Pozíció méret
        if (self.exposure + next_order_amount) > self.limit:
            return False, "LIMIT_EXCEEDED"
            
        # 2. Invariáns: Rendelési sebesség (szimulált ciklus)
        if self.orders_this_cycle > 5:
            return False, "RATE_LIMIT_EXCEEDED"
            
        return True, "CLEAR"

    def process_order(self, amount):
        if self.is_locked:
            return {"status": "LOCKED", "msg": "MetaSpace Logic Lock aktív. Tranzakció megtagadva."}

        # Ellenőrzés
        safe, reason = self.check_metaspace_invariants(amount)
        
        if not safe:
            self.is_locked = True # Reteszelés
            return {"status": "HALTED", "msg": f"INVARIANTS_BREACHED: {reason}. Rendszer lezárva."}

        # Végrehajtás
        self.exposure += amount
        self.orders_this_cycle += 1
        return {"status": "SUCCESS", "exposure": self.exposure, "msg": "Rendelés elfogadva."}

if __name__ == "__main__":
    engine = FinancialLogicEngine()
    print("=== MetaSpace Pénzügyi Pajzs Teszt indítása ===")
    
    # Normál működés
    for i in range(3):
        res = engine.process_order(100000)
        print(f"Ciklus {i}: {res['msg']} (Kitettség: ${res.get('exposure', 0)})")

    print("\n--- HIBÁS ALGORITMUS (GLITCH) AKTIVÁLÓDIK ---")
    # A zombi kód megpróbál gyorsan sok nagy tranzakciót indítani
    for i in range(10):
        res = engine.process_order(300000)
        print(f"Támadás {i}: {res['msg']}")
        if res['status'] == "HALTED":
            print("\n[SIKER] A MetaSpace megállította a tőke kifolyását.")
            break