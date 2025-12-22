# Railway Telepítési Útmutató

Ez a projekt most már készen áll a Railway-re való telepítésre.

## Telepítési lépések

### 1. Railway fiók létrehozása
- Menj a [Railway.app](https://railway.app) oldalra
- Regisztrálj vagy jelentkezz be

### 2. Új projekt létrehozása
- Kattints a "New Project" gombra
- Válaszd a "Deploy from GitHub repo" opciót
- Válaszd ki ezt a repository-t

### 3. Automatikus telepítés
A Railway automatikusan felismeri a következő fájlokat:
- `Procfile` - Meghatározza, hogyan kell futtatni az alkalmazást
- `requirements.txt` - Python függőségek
- `runtime.txt` - Python verzió

### 4. Környezeti változók (opcionális)
A Railway automatikusan beállítja a `PORT` változót. Nincs szükség további konfigurációra.

### 5. Domain beállítása
- A Railway automatikusan generál egy domain-t
- Opcionálisan beállíthatsz egyedi domain-t is

## Fájlok változásai

### Új fájlok:
- `app.py` - Flask alkalmazás a Railway-hez
- `Procfile` - Railway process definíció
- `runtime.txt` - Python verzió specifikáció

### Módosított fájlok:
- `requirements.txt` - Hozzáadva: flask, flask-cors
- `index.html` - API URL módosítva relatív útvonalra

## Helyi tesztelés

A Railway-re való telepítés előtt tesztelheted helyileg:

```bash
pip install -r requirements.txt
python app.py
```

Ezután nyisd meg a böngészőben: `http://localhost:5000`

## Megjegyzések

- A `matplotlib` csak a helyi fejlesztéshez szükséges, a Railway-en nem használjuk
- A szimulátor háttérben fut, és folyamatosan frissíti az adatokat
- Az alkalmazás automatikusan a Railway által biztosított PORT-ot használja

