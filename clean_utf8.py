import os

def fix_encoding_errors(text):
    # Gyakori UTF-8 -> Latin1 torzulások javítása
    replacements = {
        'fájlƒájl': 'fájl',
        'fájlƒájlokban': 'fájlokban',
        'leÁƒírÁƒásokban': 'leírásokban',
        'DokumentációƒáciÁƒók': 'Dokumentációk',
        'sikeresen feltörlésƒöltve': 'sikeresen feltöltve',
        'feltörlésƒöltés': 'feltöltés',
        'szűrhető‘': 'szűrhető',
        'kereshető‘': 'kereshető',
        'Áƒő€“sszes': 'Összes',
        'Áƒügyvivédelmi…ő€˜vel': 'ügyvivővel',
        'lehető…ő€˜védelmiƒé': 'lehetővé',
        'törlésƒörtörlésƒént': 'történt',
        '✅“ő€¦': '✅',
        '❌ Å’': '❌',
        '🔒¸ő€œÁ¤': '📤',
        '🔒¸ő€œÁ¦': '📦',
        'Áƒútmutatörlésƒó': 'Útmutató',
        'jegyzÁ…ő€˜kÁƒönyv': 'jegyzőkönyv',
        'fejlesztörlésƒési': 'fejlesztési',
        'szÁƒüksÁƒéges': 'szükséges'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def process_file(filename):
    if not os.path.exists(filename):
        print(f"File {filename} not found!")
        return

    # Beolvasás kényszerített UTF-8 kódolással
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    fixed_content = fix_encoding_errors(content)

    # Visszaírás tiszta UTF-8-ba
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    print(f"Javítva: {filename}")

# Futtatás a két fájlon
process_file('index.html')
process_file('server.js')