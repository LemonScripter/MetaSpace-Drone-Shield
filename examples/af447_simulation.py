import numpy as np
import matplotlib.pyplot as plt

# --- METASPACE AF447 SZENZOR-DIVERGENCIA SZIMULÁTOR ---

class AviationShieldSim:
    def __init__(self, duration=100):
        self.time = np.linspace(0, duration, duration * 10)
        self.steps = len(self.time)
        
        # Alap sebesség: 480 csomó
        self.base_speed = 480.0
        
        # Három szenzor adatfolyama
        self.s1 = np.full(self.steps, self.base_speed) + np.random.normal(0, 0.5, self.steps)
        self.s2 = np.full(self.steps, self.base_speed) + np.random.normal(0, 0.5, self.steps)
        self.s3 = np.full(self.steps, self.base_speed) + np.random.normal(0, 0.5, self.steps)
        
        # Jegesedés szimulációja (T=30-nál az s1 és s2 elkezd esni)
        for i in range(300, self.steps):
            self.s1[i] -= (i - 300) * 4.0
            self.s2[i] -= (i - 300) * 2.5
            if self.s1[i] < 60: self.s1[i] = 60

    def run_audit(self):
        self.detections = []
        self.fallback_active = False
        threshold = 20.0
        
        for i in range(self.steps):
            # Invariáns ellenőrzés: max különbség a szenzorok között
            speeds = [self.s1[i], self.s2[i], self.s3[i]]
            max_diff = max(speeds) - min(speeds)
            
            if max_diff > threshold:
                self.fallback_active = True
                self.detections.append(i)
                
    def plot(self):
        plt.style.use('dark_background')
        plt.figure(figsize=(12, 6))
        
        plt.plot(self.time, self.s1, 'r', label='Pitot 1 (Icing)', alpha=0.6)
        plt.plot(self.time, self.s2, 'orange', label='Pitot 2 (Icing)', alpha=0.6)
        plt.plot(self.time, self.s3, 'cyan', label='Pitot 3 (Healthy)', linewidth=2)
        
        if self.detections:
            trigger_t = self.time[self.detections[0]]
            plt.axvline(x=trigger_t, color='white', linestyle='--', label='METASPACE: FALLBACK ENGAGED')
            plt.fill_between(self.time, 0, 600, where=[i in self.detections for i in range(self.steps)], 
                             color='red', alpha=0.1)

        plt.title("AF447 Szenzorhiba vs. MetaSpace Determinisztikus Logika")
        plt.ylabel("Mért sebesség (csomó)")
        plt.xlabel("Idő (s)")
        plt.legend()
        plt.grid(alpha=0.1)
        plt.show()

if __name__ == "__main__":
    sim = AviationShieldSim()
    sim.run_audit()
    sim.plot()