"""
MetaSpace AF447 Divergence Simulator
Simulates pitot tube icing and MetaSpace invariant-based detection response.

Case Study: Air France 447 (AF447) - Sensor failure detection
Demonstrates how MetaSpace detects sensor inconsistencies using invariant checking.
"""

import numpy as np
import matplotlib.pyplot as plt

class AF447Simulation:
    """
    Simulates AF447 pitot tube icing scenario with MetaSpace detection.
    
    The simulation demonstrates:
    - Normal flight with three pitot sensors
    - Icing event causing sensor divergence
    - MetaSpace invariant-based detection trigger
    """
    
    def __init__(self, duration=100, dt=0.1):
        self.time = np.arange(0, duration, dt)
        self.steps = len(self.time)
        
        # Normal speed: 480 knots
        self.true_speed = np.full(self.steps, 480.0)
        
        # Initialize three sensors with noise
        self.s1 = self.true_speed + np.random.normal(0, 1, self.steps)
        self.s2 = self.true_speed + np.random.normal(0, 1, self.steps)
        self.s3 = self.true_speed + np.random.normal(0, 1, self.steps)
        
        # Simulate icing at t=30 (Sensors 1 and 2 start dropping)
        for i in range(int(30/dt), self.steps):
            self.s1[i] -= (i - 30/dt) * 5.0  # Fast drop
            self.s2[i] -= (i - 30/dt) * 3.5  # Different rate drop
            if self.s1[i] < 0: 
                self.s1[i] = 0
            if self.s2[i] < 0: 
                self.s2[i] = 0

    def run_metaspace_logic(self):
        """
        Run MetaSpace invariant checking on sensor data.
        
        Invariant: Maximum difference between any two sensors < 20 knots
        """
        self.detections = []
        threshold = 20.0  # 20 knots max divergence
        
        for i in range(self.steps):
            # Invariant check: maximum pairwise difference
            diff = max(abs(self.s1[i]-self.s2[i]), 
                      abs(self.s2[i]-self.s3[i]), 
                      abs(self.s1[i]-self.s3[i]))
            
            if diff > threshold:
                self.detections.append(i)
                # In real system, Logic Lock would activate here

    def plot(self):
        """Visualize simulation results with detection events."""
        plt.style.use('dark_background')
        plt.figure(figsize=(12, 6))
        
        plt.plot(self.time, self.s1, 'r', label='Pitot 1 (Icing)', alpha=0.7)
        plt.plot(self.time, self.s2, 'orange', label='Pitot 2 (Icing)', alpha=0.7)
        plt.plot(self.time, self.s3, 'cyan', label='Pitot 3 (Healthy)', linewidth=2)
        
        if self.detections:
            # First detection moment
            trigger_t = self.time[self.detections[0]]
            plt.axvline(x=trigger_t, color='red', linestyle='--', 
                       label='METASPACE: SHIELD ENGAGED')
            plt.fill_between(self.time, 0, 600, 
                           where=[i in self.detections for i in range(self.steps)], 
                           color='red', alpha=0.1)

        plt.title("AF447 Sensor Failure vs. MetaSpace Deterministic Logic")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Measured Speed (knots)")
        plt.legend()
        plt.grid(alpha=0.2)
        plt.show()

if __name__ == "__main__":
    sim = AF447Simulation()
    sim.run_metaspace_logic()
    sim.plot()

