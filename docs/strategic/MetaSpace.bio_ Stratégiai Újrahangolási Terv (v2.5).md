# **MetaSpace.bio: Stratégiai Újrahangolási Terv (v2.5)**

Ez a dokumentum rögzíti a Perplexity-kritika és a "Demand-Driven" audit utáni szükséges korrekciókat a projekt teljes struktúrájában.

## **1\. Kommunikációs Paradigmaváltás**

* **RÉGI:** "Építettünk egy SIL-3-as rendszert, ami 0ms alatt verifikál mindent." (Marketing-fókusz)  
* **ÚJ:** "Létrehoztunk egy TRL-4 szintű prototípust, amely SMT-alapú formális logikával védi a drónokat, kiszolgálva a precíziós mezőgazdaság (SIL-2) és a katonai UAV-k egyedi igényeit." (Mérnöki-fókusz)

## **2\. A README.md Kritikus Pontjai**

* **TRL-4 Lab Prototype:** Ez az első mondat. Nincs több félreértés a készültségi szinttel kapcsolatban.  
* **Market-Specific Requirements:** 3 blokk (Agri, Delivery, Defense) konkrét követelményekkel (Latency, CPU, Standards).  
* **Scientific Grounding:** Hivatkozás a Z3 solver integritására és a kinematikai invariánsokra.  
* **Honest Limitations:** A LIMITATIONS.md linkje kiemelt helyen.

## **3\. Struktúrális Korrekciók**

* **Mappák:** Elkülönített src/cpp (firmware) és src/python (sim) könyvtárak.  
* **Validáció:** Új validation/ mappa az empirikus adatoknak (logok, CSV-k).  
* **Legal & Papers:** A szabadalmi és tudományos háttér külön docs/legal/ és papers/ mappába kerül.

## **4\. Ütemterv (Timeline) Pontosítása**

* **Jan 2025:** Alap repo és dokumentáció véglegesítése.  
* **Feb 2025:** Gazebo szimulációs adatok publikálása.  
* **Mar 2025:** Pixhawk 4 Mini fizikai prototípus és HackRF tesztek.

**Konklúzió:** A MetaSpace.bio ezentúl nem egy "ígéret", hanem egy "folyamatban lévő tudományos kísérlet", amelynek minden lépése dokumentált és cáfolható.