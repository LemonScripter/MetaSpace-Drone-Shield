import numpy as np
import matplotlib.pyplot as plt

# MetaSpace AF447 Divergencia Szimulátor
# Szimuláljuk a sebességmérők jegesedését és a MetaSpace reakcióját

class AF447Simulation:
    def __init__(self, duration=100, dt=0.1):
        self.time = np.arange(0, duration, dt)
        self.steps = len(self.time)
        
        # Normál sebesség: 480 csomó
        self.true_speed = np.full(self.steps, 480.0)
        
        # Három szenzor inicializálása
        self.s1 = self.true_speed + np.random.normal(0, 1, self.steps)
        self.s2 = self.true_speed + np.random.normal(0, 1, self.steps)
        self.s3 = self.true_speed + np.random.normal(0, 1, self.steps)
        
        # Jegesedés szimulációja t=30-nál (Szenzor 1 és 2 hirtelen esni kezd)
        for i in range(int(30/dt), self.steps):
            self.s1[i] -= (i - 30/dt) * 5.0  # Gyors esés
            self.s2[i] -= (i - 30/dt) * 3.5  # Eltérő ütemű esés
            if self.s1[i] < 0: self.s1[i] = 0
            if self.s2[i] < 0: self.s2[i] = 0

    def run_metaspace_logic(self):
        self.detections = []
        threshold = 20.0 # 20 csomó max eltérés
        
        for i in range(self.steps):
            # Invariáns ellenőrzés
            diff = max(abs(self.s1[i]-self.s2[i]), abs(self.s2[i]-self.s3[i]), abs(self.s1[i]-self.s3[i]))
            
            if diff > threshold:
                self.detections.append(i)
                # Itt aktiválódna a LOGIC LOCK az igazi rendszerben

    def plot(self):
        plt.style.use('dark_background')
        plt.figure(figsize=(12, 6))
        
        plt.plot(self.time, self.s1, 'r', label='Pitot 1 (Icing)', alpha=0.7)
        plt.plot(self.time, self.s2, 'orange', label='Pitot 2 (Icing)', alpha=0.7)
        plt.plot(self.time, self.s3, 'cyan', label='Pitot 3 (Healthy)', linewidth=2)
        
        if self.detections:
            # Az első detektálás pillanata
            trigger_t = self.time[self.detections[0]]
            plt.axvline(x=trigger_t, color='red', linestyle='--', label='METASPACE: SHIELD ENGAGED')
            plt.fill_between(self.time, 0, 600, where=[i in self.detections for i in range(self.steps)], 
                             color='red', alpha=0.1)

        plt.title("AF447 Szenzorhiba vs. MetaSpace Determinisztikus Logika")
        plt.xlabel("Idő (másodperc)")
        plt.ylabel("Mért sebesség (Csomó)")
        plt.legend()
        plt.grid(alpha=0.2)
        plt.show()

if __name__ == "__main__":
    sim = AF447Simulation()
    sim.run_metaspace_logic()
    sim.plot()