# MetaSpace.bio Projekt Átstrukturálási Terv
## Marketing-vezérelt → Mérnöki- és Tudomány-vezérelt TRL-4 Prototípus

**Dátum:** 2025-12-25  
**Státusz:** Tervezési fázis  
**Cél:** TRL-4 prototípus, transzparens dokumentáció, tudományos rigor

---

## 1. JELENLEGI ÁLLAPOT ELEMZÉSE

### 1.1. Projektstruktúra (Jelenlegi)

```
metaspace_assets/
├── core/                    # Core engine fájlok (Python)
├── specs/                   # .bio specifikációk
├── docs/                    # Dokumentációk (stratégiai, technikai, patent, theory, validation)
├── simulations/             # Szimulációk (Python)
├── case_studies/            # Esettanulmányok
├── assets/                  # Egyéb eszközök
├── exports/                 # Exportált fájlok
├── index.html               # Fájlkezelő webes felület
├── server.js                # Node.js backend
├── README.md                # Jelenleg: fájlkezelő leírás
└── package.json             # NPM konfiguráció
```

### 1.2. Problémák azonosítása

**Marketing-vezérelt elemek (eltávolítandó):**
- ❌ "0ms latency" állítások (valóság: ~12ms software, 0.0005ms target hardware)
- ❌ "Certified" címkék (nincs még valós certifikáció)
- ❌ Túlzó teljesítmény ígéretek
- ❌ Hiányzó tudományos korlátok dokumentálása

**Hiányzó struktúra:**
- ❌ `src/cpp/pixhawk_integrator/` mappa
- ❌ `src/python/analysis/` mappa
- ❌ `src/python/simulation/` mappa
- ❌ `src/smtlib2/` mappa
- ❌ `validation/` mappa (jelenleg `simulations/` van)
- ❌ `papers/` mappa
- ❌ `docs/LIMITATIONS.md`
- ❌ `docs/ARCHITECTURE.md`
- ❌ `CONTRIBUTING.md`
- ❌ `LICENSE` (Apache 2.0)

**Áthelyezendő fájlok:**
- `src/verification/metaspace_smt_engine.py` → `src/python/analysis/invariant_checker.py` (ha létezik)
- Validációs dokumentumok → `docs/` (már ott vannak, de át kell rendezni)

**Módosítandó fájlok:**
- `README.md` → Teljes átírás (TRL-4, 3 piaci igény, transzparens)
- `index.html` → Sötét, minimalista "Technical Portal" stílus
- `results/audit_report_summary.json` → Metrikák javítása (ha létezik)

---

## 2. CÉLÁLLAPOT (Tervdokumentum alapján)

### 2.1. Új mappaszerkezet

```
MetaSpace-Drone-Shield/
│
├── README.md                      (TRL-4, 3 use case, transzparens)
├── CONTRIBUTING.md                (hozzájárulási útmutató)
├── LICENSE                        (Apache 2.0)
├── .gitignore                     (Python + C++ + ArduPilot)
│
├── docs/
│   ├── ARCHITECTURE.md            (3 szint: Szintaktikai, Szemantikai, Pragmatikai)
│   ├── LIMITATIONS.md             (Zero-delay meaconing, Invariant completeness)
│   ├── INSTALLATION.md            (telepítési útmutató)
│   ├── TECHNICAL_THEORY.md        (SMT alapok)
│   └── PAPERS.md                  (referenciák, publikációk)
│
├── src/
│   ├── cpp/
│   │   ├── pixhawk_integrator/    (ArduPilot integráció)
│   │   │   ├── GPS_Spoofing_Detector.cpp
│   │   │   ├── GPS_Spoofing_Detector.h
│   │   │   ├── kinematic_constraints.cpp
│   │   │   └── smtlib_gen.cpp
│   │   │
│   │   ├── z3_solver/
│   │   │   ├── z3_wrapper.cpp
│   │   │   ├── constraint_builder.cpp
│   │   │   └── result_interpreter.cpp
│   │   │
│   │   └── tests/
│   │       ├── test_constraints.cpp
│   │       ├── test_z3_integration.cpp
│   │       └── test_pixhawk_sim.cpp
│   │
│   ├── python/
│   │   ├── simulation/
│   │   │   ├── gazebo_simulator.py
│   │   │   ├── spoofing_generator.py
│   │   │   └── flight_data_generator.py
│   │   │
│   │   ├── analysis/
│   │   │   ├── trajectory_validator.py
│   │   │   ├── invariant_checker.py      (← metaspace_smt_engine.py-ból)
│   │   │   └── performance_analyzer.py
│   │   │
│   │   └── tests/
│   │       ├── test_simulation.py
│   │       └── test_analysis.py
│   │
│   └── smtlib2/                   (SMTLib2 constraint fájlok)
│       ├── quadcopter_kinematics.smt2
│       ├── fixed_wing_kinematics.smt2
│       └── sensor_constraints.smt2
│
├── validation/
│   ├── gazebo_tests/
│   │   ├── test_scenario_1_overt_spoofing.py
│   │   ├── test_scenario_2_covert_spoofing.py
│   │   ├── test_scenario_3_normal_flight.py
│   │   └── test_results/            (CSV outputs)
│   │
│   ├── hardware_tests/
│   │   ├── pixhawk_benchmark.py
│   │   ├── hackrf_integration.py
│   │   └── field_test_protocols.md
│   │
│   └── performance_metrics.py
│
├── papers/
│   ├── MetaSpace_Whitepaper.md
│   ├── arxiv_preprint.tex
│   ├── conference_submission.tex
│   └── references.bib
│
├── examples/
│   ├── example_1_gazebo_sim.py
│   ├── example_2_pixhawk_proto.cpp
│   ├── example_3_hackrf_test.py
│   └── example_4_case_studies/
│       ├── precision_agriculture.md
│       ├── drone_delivery.md
│       └── military_uav.md
│
├── ardupilot_integration/
│   ├── ardupilot_fork/
│   └── BUILD_INSTRUCTIONS.md
│
├── requirements.txt
├── setup.py
├── Makefile
├── CMakeLists.txt
└── .github/
    └── workflows/
        ├── ci_test.yml
        ├── documentation.yml
        └── code_coverage.yml
```

### 2.2. Hangvétel és stílus irányelvek

**Kód kommentek:**
- ✅ Magyar nyelvű (a kódban)
- ✅ Mérnöki, pontos, technikai

**Dokumentáció:**
- ✅ Angol nyelvű (README, docs/) - nemzetközi közösség számára
- ✅ Szigorú, mérnöki hangvétel
- ✅ Mentes minden "hype"-tól
- ✅ Transzparens korlátok és feltételezések

**Whitepaper/Manifest:**
- ✅ Lehet utalás magyar származásra (LemonScript Laboratory)
- ✅ De főleg angol

---

## 3. LÉPÉSRŐL-LÉPÉSRE ÁTALAKÍTÁSI TERV

### FÁZIS 1: MAPPASZERKEZET LÉTREHOZÁSA

**Lépések:**
1. ✅ Létrehozni: `src/cpp/pixhawk_integrator/`
2. ✅ Létrehozni: `src/cpp/z3_solver/`
3. ✅ Létrehozni: `src/cpp/tests/`
4. ✅ Létrehozni: `src/python/analysis/`
5. ✅ Létrehozni: `src/python/simulation/`
6. ✅ Létrehozni: `src/python/tests/`
7. ✅ Létrehozni: `src/smtlib2/`
8. ✅ Létrehozni: `validation/gazebo_tests/`
9. ✅ Létrehozni: `validation/hardware_tests/`
10. ✅ Létrehozni: `papers/`
11. ✅ Létrehozni: `examples/`
12. ✅ Létrehozni: `ardupilot_integration/`
13. ✅ Létrehozni: `.github/workflows/`

**Időbecslés:** 15-30 perc

---

### FÁZIS 2: FÁJLOK ÁTHELYEZÉSE

**Áthelyezendő fájlok:**

1. **SMT Engine:**
   - `src/verification/metaspace_smt_engine.py` → `src/python/analysis/invariant_checker.py`
   - *Megjegyzés: Ha nem létezik, később létre kell hozni*

2. **Szimulációk:**
   - `simulations/AF447.py` → `src/python/simulation/` (ha releváns)
   - `simulations/bank.py` → `src/python/simulation/` (ha releváns)
   - `simulations/MetaSpace_AF447_Divergencia.py` → `src/python/simulation/`
   - `simulations/sitl_validation_tool.py` → `validation/hardware_tests/`

3. **Core fájlok:**
   - `core/METASPACE CORE ENGINE - VERSION 1.3 (SOVEREIGN SWARM).py` → `src/python/` (átnevezve)
   - `core/metaspace_core_engine.py` → `src/python/` (átnevezve)
   - *Megjegyzés: Ezeket át kell nézni, hogy relevánsak-e az új struktúrához*

4. **Dokumentációk:**
   - `docs/validation/` → Már jó helyen van, de át kell rendezni
   - `docs/strategic/` → Marad, de át kell nézni
   - `docs/technical/` → Marad, de át kell nézni

**Időbecslés:** 30-60 perc

---

### FÁZIS 3: ÚJ FÁJLOK GENERÁLÁSA

**1. LICENSE (Apache 2.0)**
- Teljes Apache 2.0 licenc szöveg
- Copyright: LemonScript Laboratory / Citrom Media SRL

**2. docs/LIMITATIONS.md**
- Zero-delay meaconing korlát (matematikai bizonyítás)
- Invariant completeness korlát
- Covert spoofing korlátok
- Szenzorhiba és kalibrálás korlátok
- Computational overhead korlátok

**3. docs/ARCHITECTURE.md**
- Szintaktikai szint (SMT logika)
- Szemantikai szint (valósvilág mapping)
- Pragmatikai szint (konkrét alkalmazás)
- Implementáció: Pixhawk integráció

**4. CONTRIBUTING.md**
- Hozzájárulási útmutató
- Issue reporting
- Pull request folyamat
- Code style guide
- Development workflow

**5. src/smtlib2/quadcopter_kinematics.smt2**
- Példa SMT-LIB v2.6 fájl
- Drón gyorsulási és sebesség korlátok
- Kinematikai invariánsok

**6. README.md (Teljes átírás)**
- TRL-4 státusz
- 3 piaci igény (Agri, Delivery, Military)
- Teljesítmény adatok (szcenárió-alapú)
- Korlátok (transzparens)
- Quick start
- Roadmap

**7. index.html (Frissítés)**
- Sötét, minimalista "Technical Portal" stílus
- Fókusz: "UNSAT" eredmény
- Szcenárió-alapú teljesítmény adatok
- Eltávolítani: marketing elemek

**8. results/audit_report_summary.json (Javítás)**
- Software latency: ~12ms
- Target hardware: 0.0005ms
- Egyéb metrikák javítása

**Időbecslés:** 2-3 óra

---

### FÁZIS 4: MEGLÉVŐ FÁJLOK ÁTÍRÁSA

**1. README.md**
- **Jelenlegi:** Fájlkezelő leírás
- **Új:** TRL-4 prototípus leírás, 3 use case, teljesítmény adatok, korlátok

**2. index.html**
- **Jelenlegi:** Világos, színes, marketing stílus
- **Új:** Sötét, minimalista, technikai portal
- **Fókusz:** UNSAT eredmények, szcenárió-alapú adatok

**3. Core Python fájlok**
- Kommentek magyarra fordítása (ha szükséges)
- Mérnöki hangvétel biztosítása
- Marketing állítások eltávolítása

**4. Dokumentációk**
- `docs/validation/SMT_CERTIFICATE.md` → "Certified" eltávolítása, helyette "Validated" vagy "Proven"
- Egyéb dokumentumokban marketing állítások eltávolítása

**Időbecslés:** 2-3 óra

---

## 4. RÉSZLETES FÁJLLISTA

### 4.1. Létrehozandó mappák

```
src/cpp/pixhawk_integrator/
src/cpp/z3_solver/
src/cpp/tests/
src/python/analysis/
src/python/simulation/
src/python/tests/
src/smtlib2/
validation/gazebo_tests/
validation/hardware_tests/
papers/
examples/
examples/example_4_case_studies/
ardupilot_integration/
ardupilot_integration/ardupilot_fork/
.github/workflows/
```

### 4.2. Létrehozandó fájlok

```
LICENSE
CONTRIBUTING.md
docs/LIMITATIONS.md
docs/ARCHITECTURE.md
docs/INSTALLATION.md
docs/TECHNICAL_THEORY.md
docs/PAPERS.md
src/smtlib2/quadcopter_kinematics.smt2
src/smtlib2/fixed_wing_kinematics.smt2
src/smtlib2/sensor_constraints.smt2
requirements.txt
setup.py
Makefile
CMakeLists.txt
.github/workflows/ci_test.yml
.github/workflows/documentation.yml
.github/workflows/code_coverage.yml
```

### 4.3. Átírandó fájlok

```
README.md (teljes átírás)
index.html (stílus és tartalom frissítés)
docs/validation/SMT_CERTIFICATE.md (marketing elemek eltávolítása)
```

### 4.4. Áthelyezendő fájlok

```
src/verification/metaspace_smt_engine.py → src/python/analysis/invariant_checker.py
simulations/sitl_validation_tool.py → validation/hardware_tests/
```

---

## 5. STÍLUS ÉS HANGVÉTEL IRÁNYELVEK

### 5.1. Kód kommentek

**Nyelv:** Magyar  
**Stílus:** Mérnöki, pontos, technikai

**Példa:**
```python
# GPS mérés ellenőrzése kinematikai invariánsok alapján
# Ha az SMT solver UNSAT-tel tér vissza, spoofing detektálva
def check_gps_measurement(gps_loc, velocity, acceleration):
    """
    GPS spoofing detektálás SMT solver-rel.
    
    Args:
        gps_loc: GPS pozíció mérés
        velocity: IMU-ból származó sebesség
        acceleration: IMU-ból származó gyorsulás
    
    Returns:
        bool: True ha spoofing detektálva
    """
```

### 5.2. Dokumentáció (README, docs/)

**Nyelv:** Angol  
**Stílus:** Szigorú, mérnöki, transzparens

**Példa:**
```markdown
## Limitations

⚠️ **Zero-delay meaconing:** Not detectable at receiver level (mathematical limit)

⚠️ **Invariant completeness:** Depends on accurate kinematic model

See `docs/LIMITATIONS.md` for full discussion.
```

### 5.3. Marketing elemek eltávolítása

**Eltávolítandó:**
- ❌ "0ms latency" → ✅ "~12ms software latency, 0.0005ms target hardware"
- ❌ "Certified" → ✅ "Validated" vagy "Proven"
- ❌ "100% accuracy" → ✅ "98.5% detection rate (overt spoofing)"
- ❌ "Revolutionary" → ✅ "Novel approach"
- ❌ "Perfect" → ✅ "Effective for specific use cases"

---

## 6. IDŐBECSLÉS ÉS PRIORITÁSOK

### Prioritás 1 (Azonnal): Mappaszerkezet + Alapfájlok
- **Idő:** 1-2 óra
- **Tartalmazza:**
  - Mappák létrehozása
  - LICENSE, CONTRIBUTING.md
  - docs/LIMITATIONS.md, docs/ARCHITECTURE.md
  - README.md átírás

### Prioritás 2 (Fontos): Fájlok áthelyezése + Új fájlok
- **Idő:** 2-3 óra
- **Tartalmazza:**
  - SMT engine áthelyezése
  - Szimulációk átszervezése
  - src/smtlib2/ fájlok generálása
  - index.html frissítés

### Prioritás 3 (Később): Finomhangolás
- **Idő:** 1-2 óra
- **Tartalmazza:**
  - Dokumentációk átnézése és marketing elemek eltávolítása
  - Core fájlok kommentjeinek frissítése
  - CI/CD workflow fájlok

**Összes időbecslés:** 4-7 óra

---

## 7. KOCKÁZATOK ÉS MEGOLDÁSOK

### Kockázat 1: Hiányzó fájlok
**Probléma:** `src/verification/metaspace_smt_engine.py` nem létezik  
**Megoldás:** Létrehozni `src/python/analysis/invariant_checker.py`-t a tervdokumentum alapján

### Kockázat 2: Függőségek
**Probléma:** Core fájlok függnek egymásra  
**Megoldás:** Áthelyezés előtt függőségek ellenőrzése

### Kockázat 3: Törött linkek
**Probléma:** Dokumentációkban linkek a régi struktúrára  
**Megoldás:** Átstrukturálás után linkek frissítése

---

## 8. ELLENŐRZÉSI LISTA

### Előkészítés
- [ ] Tervdokumentum elolvasva és megértve
- [ ] Jelenlegi struktúra feltérképezve
- [ ] Backup készítése (git commit)

### Fázis 1: Mappaszerkezet
- [ ] `src/cpp/pixhawk_integrator/` létrehozva
- [ ] `src/python/analysis/` létrehozva
- [ ] `src/python/simulation/` létrehozva
- [ ] `src/smtlib2/` létrehozva
- [ ] `validation/` létrehozva
- [ ] `papers/` létrehozva

### Fázis 2: Fájlok áthelyezése
- [ ] SMT engine áthelyezve
- [ ] Szimulációk átszervezve
- [ ] Core fájlok átnézve

### Fázis 3: Új fájlok
- [ ] LICENSE létrehozva
- [ ] CONTRIBUTING.md létrehozva
- [ ] docs/LIMITATIONS.md létrehozva
- [ ] docs/ARCHITECTURE.md létrehozva
- [ ] src/smtlib2/quadcopter_kinematics.smt2 létrehozva
- [ ] README.md átírva

### Fázis 4: Módosítások
- [ ] README.md átírva (TRL-4, 3 use case)
- [ ] index.html frissítve (sötét, minimalista)
- [ ] Marketing elemek eltávolítva
- [ ] Metrikák javítva

### Végleges ellenőrzés
- [ ] Minden fájl a helyén van
- [ ] Linkek működnek
- [ ] Dokumentáció konzisztens
- [ ] Hangvétel mérnöki, transzparens
- [ ] Git commit kész

---

## 9. KÖVETKEZŐ LÉPÉSEK

1. **Terv jóváhagyása** (ez a dokumentum)
2. **Backup készítése** (git commit)
3. **Fázis 1: Mappaszerkezet létrehozása**
4. **Fázis 2: Fájlok áthelyezése**
5. **Fázis 3: Új fájlok generálása**
6. **Fázis 4: Meglévő fájlok átírása**
7. **Végleges ellenőrzés és tesztelés**
8. **Git commit és dokumentáció frissítése**

---

**Terv készítő:** AI Assistant  
**Dátum:** 2025-12-25  
**Státusz:** Várakozás jóváhagyásra

