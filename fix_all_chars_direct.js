const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, 'index.html');

console.log('Közvetlen karakterek javítása...');

let content = fs.readFileSync(filePath, 'utf8');

// Összes lehetséges rossz karakter javítása
const fixes = [
    // HTML-ben lévő karakterek
    ['Keresés fájlájlokban', 'Keresés fájlokban'],
    ['Összes / All', 'Összes / All'],
    ['Specifikááciáók', 'Specifikációk'],
    ['Dokumentációáciáók', 'Dokumentációk'],
    ['Szimulációáciáók', 'Szimulációk'],
    ['Esettanulmányányok', 'Esettanulmányok'],
    ['Eszkáözáök', 'Eszközök'],
    ['Összes fájlájl', 'Összes fájl'],
    ['🔴ő', '🔴'],
    ['🔴á´', '🔴'],
    ['🟠¸á', '🟠'],
    ['🟠¸á ', '🟠'],
    ['🟠¸á¢', '🟢'],
    
    // JSON adatokban lévő karakterek - közvetlen cserék
    ['technolgiagia', 'technológia'],
    ['specifikcicis', 'specifikációs'],
    ['elemzsQjt', 'elemzőjét'],
    ['formlis', 'formális'],
    ['llapottrlsr', 'állapottér'],
    ['verifiktort', 'verifikátort'],
    ['s', 'és'],
    ['fordtrlst', 'fordítót'],
    ['osztrlslyok', 'osztályok'],
    ['kerljn', 'kerüljön'],
    ['nyilvdelminos', 'nyilvános'],
    ['repoésitory', 'repository'],
    ['és', 'és'],
    ['észemantikai', 'szemantikai'],
    ['determiniésztikués', 'determinisztikus'],
];

let changes = 0;
let iterations = 0;
let previousContent = '';

// Javítások alkalmazása - többször is
while (content !== previousContent && iterations < 50) {
    previousContent = content;
    iterations++;
    
    for (const [wrong, correct] of fixes) {
        if (content.includes(wrong)) {
            const before = content;
            const escaped = wrong.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            content = content.replace(new RegExp(escaped, 'g'), correct);
            if (before !== content) {
                changes++;
            }
        }
    }
}

// Bináris karakterek eltávolítása
content = content.replace(/[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]/g, '');

// További javítások: közvetlen karakter cserék
content = content.replace(/áá/g, 'á');
content = content.replace(/éé/g, 'é');
content = content.replace(/íí/g, 'í');
content = content.replace(/óó/g, 'ó');
content = content.replace(/öö/g, 'ö');
content = content.replace(/úú/g, 'ú');
content = content.replace(/üü/g, 'ü');

fs.writeFileSync(filePath, content, { encoding: 'utf8' });
console.log(`✅ ${changes} javítás alkalmazva (${iterations} iteráció)`);

