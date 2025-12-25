# MetaSpace Assets - Projekt Állapot / Project Status

**Utolsó frissítés / Last Updated:** 2024-12-23

## 📋 Projekt Áttekintés / Project Overview

Ez a projekt egy fájlkezelő és katalógus rendszer, amely a MetaSpace találmányhoz kapcsolódó dokumentumokat kezeli, kategorizálja és kereshetővé teszi. A rendszer automatikusan generál magyar és angol kivonatokat (summaries) és leírásokat (descriptions) az OpenAI API segítségével.

This project is a file management and catalog system that manages, categorizes, and makes searchable documents related to the MetaSpace invention. The system automatically generates Hungarian and English summaries and descriptions using the OpenAI API.

## 🏗️ Projekt Struktúra / Project Structure

```
metaspace_assets/
├── server.js                 # Node.js/Express backend szerver
├── index.html               # Frontend HTML/CSS/JavaScript
├── package.json             # NPM függőségek
├── package-export.js        # Export funkció (ZIP + email)
├── generate_summaries.js    # Batch kivonat generálás script
├── extract_all_content.js   # Fájl tartalom kinyerés script
├── file_metadata.json       # Metadata (kivonatok, leírások)
├── file_contents.json       # Fájl tartalmak (kereséshez)
├── core/                    # Core Engine fájlok
├── specs/                   # Bio specifikációk
├── docs/                    # Dokumentációk (strategic, technical, patent, theory, validation)
├── simulations/             # Szimulációs fájlok
├── case_studies/            # Esettanulmányok
├── assets/                  # Egyéb eszközök
└── exports/                 # Exportált ZIP fájlok
```

## ✅ Implementált Funkciók / Implemented Features

### 1. Fájl Feltöltés és Automatikus Elemzés / File Upload and Automatic Analysis

**Hely / Location:** `server.js` - `/api/upload` endpoint

**Funkciók / Features:**
- ✅ Fájl feltöltés `multer` middleware-rel
- ✅ UTF-8 fájlnév normalizálás (latin1 → UTF-8 konverzió)
- ✅ Fájl tartalom kinyerése:
  - PDF fájlok (`pdf-parse`)
  - DOCX fájlok (`mammoth`)
  - Szöveges fájlok (txt, py, bio, md, js, json, html, css, xml, yaml, rtf)
- ✅ OpenAI elemzés:
  - Kategória meghatározás (core, specs, docs, simulations, case_studies, assets)
  - Subcategory meghatározás (docs esetén: strategic, technical, patent, theory, validation)
  - Magyar leírás generálás (`description_hu`)
  - Angol leírás generálás (`description_en`)
  - Magyar kivonat generálás (`summary_hu`)
  - Angol kivonat generálás (`summary_en`)
- ✅ Fájl mentése a megfelelő kategóriába
- ✅ Metadata mentése `file_metadata.json`-ba
- ✅ Fájl tartalom mentése `file_contents.json`-ba (kereséshez, max 50000 karakter)

**Kód részletek / Code Details:**
```javascript
// server.js:418-640
app.post('/api/upload', upload.single('file'), async (req, res) => {
    // 1. Fájl tartalom kinyerése: readFileContent(tempPath)
    // 2. OpenAI elemzés: analyzeFileWithOpenAI()
    // 3. Fájl mentése: saveFileToCategory()
    // 4. Metadata mentése: file_metadata.json
    // 5. Fájl tartalom mentése: file_contents.json
})
```

### 2. Fájl Listázás és Keresés / File Listing and Search

**Hely / Location:** 
- Backend: `server.js` - `/api/files` endpoint
- Frontend: `index.html` - `renderFiles()` függvény

**Funkciók / Features:**
- ✅ Rekurzív fájl beolvasás (`scanAllFiles()`)
- ✅ Metadata betöltése (`file_metadata.json`)
- ✅ Fájl tartalmak betöltése (`file_contents.json`)
- ✅ Kategória szerinti szűrés (core, specs, docs, simulations, case_studies, assets)
- ✅ Keresés a következőkben:
  - Fájlnév
  - Magyar leírás (`description_hu`)
  - Angol leírás (`description_en`)
  - Magyar kivonat (`summary_hu`)
  - Angol kivonat (`summary_en`)
  - Fájl tartalom (`content`)
- ✅ Biztonsági szint szerinti szűrés (critical, high, medium, public)
- ✅ Nyelvváltás (magyar/angol)

**Kód részletek / Code Details:**
```javascript
// server.js:701-1009
async function scanAllFiles() {
    // 1. Metadata betöltése
    // 2. Fájl tartalmak betöltése
    // 3. Rekurzív fájl beolvasás kategóriánként
    // 4. Metadata és tartalom hozzáadása fájlokhoz
}

// index.html:655-783
function renderFiles(category, searchTerm, securityFilter) {
    // 1. Kategória szerinti szűrés
    // 2. Keresés és biztonsági szűrés
    // 3. Fájl kártyák renderelése
}
```

### 3. Export Funkció / Export Functionality

**Hely / Location:** 
- Backend: `server.js` - `/api/export-package` endpoint
- Script: `package-export.js`

**Funkciók / Features:**
- ✅ Core fájlok csomagolása ZIP-be verziókövetéssel
- ✅ SHA-256 hash generálás
- ✅ Verzió információ mentése (git hash, timestamp)
- ✅ Email küldés három címre:
  - lszoke@gmail.com
  - planxmod@gmail.com
  - szeklerwood@gmail.com
- ✅ Mailto linkek generálása (natív email kliens megnyitása)

**Kód részletek / Code Details:**
```javascript
// server.js:1122-1131
app.post('/api/export-package', async (req, res) => {
    const { packageAndSend } = require('./package-export');
    const result = await packageAndSend();
    res.json(result);
})

// package-export.js:286-350
async function packageAndSend() {
    // 1. Verzió meghatározása (git hash + dátum)
    // 2. ZIP fájl létrehozása
    // 3. SHA-256 hash generálása
    // 4. Email linkek generálása
    // 5. Visszatérési érték a frontend számára
}
```

### 4. Batch Kivonat Generálás / Batch Summary Generation

**Hely / Location:** `generate_summaries.js`

**Funkciók / Features:**
- ✅ Összes fájl feldolgozása
- ✅ OpenAI kivonat generálás (ha még nincs)
- ✅ Metadata frissítése `file_metadata.json`-ban

**Használat / Usage:**
```bash
node generate_summaries.js
```

### 5. Frontend Funkciók / Frontend Features

**Hely / Location:** `index.html`

**Funkciók / Features:**
- ✅ Fájl kártyák megjelenítése
- ✅ Kategória szűrők
- ✅ Keresés (név, leírás, kivonat, tartalom)
- ✅ Biztonsági szint szűrők
- ✅ Nyelvváltás (magyar/angol)
- ✅ Fájl megnyitása új ablakban
- ✅ Fájl törlése
- ✅ Export funkció

## 🔧 Technikai Részletek / Technical Details

### Backend Dependencies (package.json)
- `express` - Web szerver
- `multer` - Fájl feltöltés kezelés
- `pdf-parse` - PDF tartalom kinyerés
- `mammoth` - DOCX tartalom kinyerés
- `openai` - OpenAI API integráció
- `archiver` - ZIP fájl létrehozás
- `crypto` - SHA-256 hash generálás

### API Endpoints

1. **GET `/api/files`**
   - Visszaadja az összes fájl adatát kategóriák szerint
   - Tartalmazza a metadata-t és fájl tartalmakat

2. **POST `/api/upload`**
   - Fájl feltöltés és automatikus elemzés
   - Request: `multipart/form-data` (file field)
   - Response: `{ success: true, file: {...} }`

3. **POST `/api/export-package`**
   - Export ZIP létrehozása és email küldés
   - Response: `{ success: true, zipFile, sha256, version, emailLinks }`

4. **DELETE `/api/files`**
   - Fájl törlése
   - Request: `{ path: "relative/path/to/file" }`

5. **GET `/file/:path(*)`**
   - Fájl letöltés/megnyitás
   - UTF-8 karaktereket kezeli

### Adatfájlok / Data Files

1. **`file_metadata.json`**
   - Struktúra:
   ```json
   {
     "relative/path/to/file": {
       "path": "relative/path/to/file",
       "name": "filename.ext",
       "category": "core",
       "subcategory": null,
       "description_hu": "Magyar leírás",
       "description_en": "English description",
       "summary_hu": "Magyar kivonat",
       "summary_en": "English summary"
     }
   }
   ```

2. **`file_contents.json`**
   - Struktúra:
   ```json
   {
     "relative/path/to/file": {
       "path": "relative/path/to/file",
       "content": "Fájl tartalom (max 50000 karakter)",
       "length": 12345
     }
   }
   ```

### Path Normalizálás / Path Normalization

A rendszer kezeli a Windows (`\`) és Unix (`/`) path formátumokat:
- Minden path normalizálva van Unix formátumra (`/`) a mentéskor
- A keresés normalizálja mindkét formátumot

**Kód / Code:**
```javascript
const normalizedPath = relativePath.split(/[\\\/]/).join('/');
```

## 🐛 Ismert Problémák és Megoldások / Known Issues and Solutions

### 1. Kategória Szűrők Nem Működnek / Category Filters Not Working

**Probléma / Issue:**
- Amikor egy kategória gombra kattintunk (pl. "Case Studies"), nem jelennek meg a dobozok

**Megoldás / Solution:**
- ✅ Javítva: A `renderCategory()` függvény most mindig új section-t hoz létre
- ✅ Debug logolás hozzáadva
- ✅ Üres eredmények kezelése javítva

**Kód változások / Code Changes:**
```javascript
// index.html:627-652
function renderCategory(categoryId, categoryName, files) {
    // Mindig létrehozunk egy új section-t
    const section = document.createElement('div');
    // ...
}
```

### 2. Export Funkció Nem Működik / Export Function Not Working

**Probléma / Issue:**
- "Cannot GET /api/export" hiba

**Megoldás / Solution:**
- ✅ Frontend módosítva: POST `/api/export-package` használata
- ✅ `packageAndSend()` függvény most visszaad értéket
- ✅ Email encoding javítva

**Kód változások / Code Changes:**
```javascript
// index.html:910-945
document.getElementById('exportPackage').addEventListener('click', async (e) => {
    const response = await fetch('/api/export-package', { method: 'POST' });
    // ...
})
```

### 3. UTF-8 Karakterkódolás / UTF-8 Character Encoding

**Probléma / Issue:**
- Magyar karakterek nem jelennek meg helyesen

**Megoldás / Solution:**
- ✅ Fájl olvasás UTF-8 kódolással
- ✅ Latin1 → UTF-8 konverzió ahol szükséges
- ✅ JSON fájlok UTF-8 kódolással mentve

## 📝 Jelenlegi Állapot / Current Status

### ✅ Működő Funkciók / Working Features

1. ✅ Fájl feltöltés és automatikus elemzés
2. ✅ Metadata mentése (`file_metadata.json`)
3. ✅ Fájl tartalom mentése (`file_contents.json`)
4. ✅ Fájl listázás kategóriák szerint
5. ✅ Keresés (név, leírás, kivonat, tartalom)
6. ✅ Export funkció (ZIP + email)
7. ✅ Nyelvváltás (magyar/angol)
8. ✅ Biztonsági szint szűrők

### 🔄 Javítások Szükségesek / Fixes Needed

1. ⚠️ **Kategória szűrők tesztelése**
   - A `renderCategory()` függvény javítva, de még nincs tesztelve
   - Debug logolás hozzáadva a problémák azonosításához

2. ⚠️ **Export funkció tesztelése**
   - A frontend és backend módosítva, de még nincs tesztelve

### 📋 Következő Lépések / Next Steps

1. **Tesztelés / Testing**
   - Kategória szűrők működésének ellenőrzése
   - Export funkció tesztelése
   - Keresés működésének ellenőrzése

2. **Hibakeresés / Debugging**
   - Böngésző konzol ellenőrzése (F12)
   - Szerver logok ellenőrzése
   - `fileData` objektum ellenőrzése a frontenden

3. **Optimalizálás / Optimization**
   - Nagy fájlok kezelése
   - Teljesítmény optimalizálás
   - Hibakezelés javítása

## 🔍 Debug Információk / Debug Information

### Frontend Debug

A `renderFiles()` függvény most logolja:
- A kiválasztott kategóriát
- A keresési kifejezést
- A biztonsági szűrőt
- A `fileData` objektum kulcsait
- A `case_studies` adatokat (ha case_studies kategória)

**Böngésző konzolban / In Browser Console:**
```javascript
renderFiles called: { category: 'case_studies', searchTerm: '', securityFilter: 'all', fileDataKeys: [...] }
case_studies data: [...]
Category rendered: case_studies with 4 files
```

### Backend Debug

A szerver logolja:
- Metadata betöltését
- Fájl tartalmak betöltését
- Fájlok számát kategóriánként

**Szerver logokban / In Server Logs:**
```
Metadata betöltve: X fájl
Fájl tartalmak betöltve: Y fájl
```

## 🚀 Szerver Indítása / Server Startup

```bash
# NPM függőségek telepítése (ha szükséges)
npm install

# Szerver indítása
npm start

# Vagy nodemon-t használva (automatikus újraindítás)
npm run dev
```

**Port:** 3000 (alapértelmezett)

**URL:** http://localhost:3000

## 📧 Email Címek / Email Addresses

Az export funkció három email címre küld:
1. lszoke@gmail.com
2. planxmod@gmail.com
3. szeklerwood@gmail.com

## 🔐 Biztonsági Szintek / Security Levels

- **critical** 🔴 - KRITIKUS - PROPRIETARY
- **high** 🟠 - MAGAS - HIGH
- **medium** 🟡 - KÖZEPES - MEDIUM
- **public** 🟢 - NYILVÁNOS - PUBLIC

## 📂 Kategóriák / Categories

1. **core** - Core Engine fájlok (Python fájlok)
2. **specs** - Bio specifikációk (.bio fájlok)
3. **docs** - Dokumentációk
   - strategic - Stratégiai dokumentumok
   - technical - Technikai dokumentumok
   - patent - Szabadalmi dokumentumok
   - theory - Elméleti dokumentumok
   - validation - Validációs dokumentumok
4. **simulations** - Szimulációs fájlok
5. **case_studies** - Esettanulmányok
6. **assets** - Egyéb eszközök

## 🛠️ Scripts

### generate_summaries.js
Összes fájlhoz generál kivonatokat, ha még nincsenek.

```bash
node generate_summaries.js
```

### extract_all_content.js
Kinyeri az összes fájl tartalmát a kereséshez.

```bash
node extract_all_content.js
```

## ⚠️ Fontos Megjegyzések / Important Notes

1. **Szerver újraindítás szükséges** a backend változások után
2. **Böngésző cache törlése** (Ctrl+F5) a frontend változások után
3. **OpenAI API kulcs** szükséges a `.env` fájlban: `OPENAI_API_KEY=...`
4. **Path normalizálás** - A rendszer automatikusan kezeli a Windows és Unix path formátumokat

## 📞 További Információk / Additional Information

- **Projekt könyvtár:** `C:\Users\lszok\Documents\metaspace_assets`
- **Node.js verzió:** (ellenőrizd: `node --version`)
- **NPM verzió:** (ellenőrizd: `npm --version`)

---

**Utolsó módosítások / Last Modifications:**
- 2024-12-23: Export funkció javítva (POST endpoint, email linkek)
- 2024-12-23: Kategória szűrők javítva (renderCategory függvény)
- 2024-12-23: Fájl tartalom mentése és keresés implementálva
- 2024-12-23: Debug logolás hozzáadva


