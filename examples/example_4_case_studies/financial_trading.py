"""
MetaSpace Financial Integrity Simulator
Demonstrates MetaSpace invariant-based integrity checking in financial trading systems.

Case Study: High-Frequency Trading (HFT) Glitch Prevention
This example demonstrates how MetaSpace can be applied to domains beyond aerospace,
showing the general applicability of invariant-based integrity checking.
"""

import time

class TradingEngine:
    """
    Trading engine with MetaSpace invariant-based protection.
    
    Demonstrates:
    - Position size limits (invariant: max 20% of balance)
    - Rate limiting (invariant: max 5 orders per cycle)
    - Logic lock activation on invariant violation
    """
    
    def __init__(self, balance=1000000):
        self.balance = balance
        self.exposure = 0
        self.orders_this_second = 0
        self.is_halted = False

    def check_metaspace_invariants(self, order_amount):
        """
        MetaSpace Integrity Layer (The Guard).
        Deterministically checks trading rules.
        
        Args:
            order_amount: Order amount in dollars
        
        Returns:
            tuple: (is_safe: bool, message: str)
        """
        # Invariant 1: Position size (max 20% of balance)
        if (self.exposure + order_amount) > (self.balance * 0.20):
            return False, "INVARIANT_VIOLATION: POSITION_SIZE_EXCEEDED"
            
        # Invariant 2: Order frequency (max 5 orders per cycle for demo)
        if self.orders_this_second > 5:
            return False, "INVARIANT_VIOLATION: RATE_LIMIT_EXCEEDED"
            
        return True, "SAFE"

    def execute_trade(self, amount):
        """
        Execute trade with MetaSpace invariant checking.
        
        Args:
            amount: Trade amount in dollars
        
        Returns:
            str: Execution result message
        """
        if self.is_halted:
            return "[BLOCK] MetaSpace Logic Lock active. Transaction rejected."

        # MetaSpace check BEFORE execution
        is_safe, message = self.check_metaspace_invariants(amount)
        
        if not is_safe:
            self.is_halted = True  # Activate Logic Lock
            return f"[LOCK] {message}. System halted."
        
        # If all checks pass, execute trade
        self.exposure += amount
        self.orders_this_second += 1
        return f"[SUCCESS] Order executed: ${amount}. Exposure: ${self.exposure}"

if __name__ == "__main__":
    # Demonstration: Financial trading with MetaSpace protection
    bank = TradingEngine(balance=5000000)  # $5 million capital
    
    print("=== MetaSpace Financial Integrity Test ===")
    
    # 1. Normal trading
    print(bank.execute_trade(50000))
    print(bank.execute_trade(50000))
    
    # 2. "Zombie Code" runs wild (sudden large or too many orders)
    print("\n--- FAULTY ALGORITHM ACTIVATES ---")
    for i in range(10):
        result = bank.execute_trade(200000)
        print(f"Order attempt {i+1}: {result}")
        if bank.is_halted:
            break

    print("\n[RESULT] MetaSpace stopped the bleeding.")

