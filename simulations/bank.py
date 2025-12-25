import time

# MetaSpace Pénzügyi Integritás Szimulátor
# Egy elszabadult algoritmus (HFT Glitch) megállítása

class TradingEngine:
    def __init__(self, balance=1000000):
        self.balance = balance
        self.exposure = 0
        self.orders_this_second = 0
        self.is_halted = False

    def check_metaspace_invariants(self, order_amount):
        """
        Ez a MetaSpace Integritási Réteg (The Guard).
        Determinisztikusan ellenőrzi a szabályokat.
        """
        # Invariáns 1: Pozíció méret (max 20%)
        if (self.exposure + order_amount) > (self.balance * 0.20):
            return False, "INVARIANT_VIOLATION: POSITION_SIZE_EXCEEDED"
            
        # Invariáns 2: Rendelési gyakoriság (max 5 rendelés/ciklus a demóhoz)
        if self.orders_this_second > 5:
            return False, "INVARIANT_VIOLATION: RATE_LIMIT_EXCEEDED"
            
        return True, "SAFE"

    def execute_trade(self, amount):
        if self.is_halted:
            return "[BLOCK] MetaSpace Logic Lock aktív. Tranzakció megtagadva."

        # MetaSpace ellenőrzés a végrehajtás ELŐTT
        is_safe, message = self.check_metaspace_invariants(amount)
        
        if not is_safe:
            self.is_halted = True # Logic Lock aktiválása
            return f"[LOCK] {message}. Rendszer leállítva."

        # Ha minden rendben, végrehajtjuk
        self.exposure += amount
        self.orders_this_second += 1
        return f"[SUCCESS] Rendelés végrehajtva: ${amount}. Kitettség: ${self.exposure}"

# --- SZIMULÁCIÓ ---
if __name__ == "__main__":
    bank = TradingEngine(balance=5000000) # 5 millió dolláros tőke
    
    print("=== MetaSpace Pénzügyi Integritás Teszt ===")
    
    # 1. Normál kereskedés
    print(bank.execute_trade(50000))
    print(bank.execute_trade(50000))
    
    # 2. A "Zombi Kód" elszabadul (Hirtelen hatalmas vagy túl sok rendelés)
    print("\n--- HIBÁS ALGORITMUS AKTIVÁLÓDIK ---")
    for i in range(10):
        result = bank.execute_trade(200000)
        print(f"Rendelési kísérlet {i+1}: {result}")
        if bank.is_halted:
            break

    print("\n[VÉGEREDMÉNY] A MetaSpace megállította a vérzést.")