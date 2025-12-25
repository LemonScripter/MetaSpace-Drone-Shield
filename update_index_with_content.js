const fs = require('fs').promises;
const path = require('path');
const { extractAllContent } = require('./extract_all_content');

// fileData string építése (jobban kezeli a nagy fájlokat)
function buildFileDataString(fileData) {
    let result = '{\n';
    
    // Core
    if (fileData.core) {
        result += '            "core": ' + JSON.stringify(fileData.core, null, 20) + ',\n';
    }
    
    // Specs
    if (fileData.specs) {
        result += '            "specs": ' + JSON.stringify(fileData.specs, null, 20) + ',\n';
    }
    
    // Docs
    if (fileData.docs) {
        result += '            "docs": {\n';
        for (const [key, value] of Object.entries(fileData.docs)) {
            result += `                "${key}": ` + JSON.stringify(value, null, 20) + ',\n';
        }
        result += '            },\n';
    }
    
    // Simulations
    if (fileData.simulations) {
        result += '            "simulations": ' + JSON.stringify(fileData.simulations, null, 20) + ',\n';
    }
    
    // Case studies
    if (fileData.case_studies) {
        result += '            "case_studies": ' + JSON.stringify(fileData.case_studies, null, 20) + ',\n';
    }
    
    // Assets
    if (fileData.assets) {
        result += '            "assets": ' + JSON.stringify(fileData.assets, null, 20) + '\n';
    }
    
    result += '        }';
    return result;
}

// index.html olvasása és frissítése
async function updateIndexWithContent() {
    console.log('📄 index.html frissítése a fájl tartalmakkal... / Updating index.html with file contents...\n');
    
    const indexPath = path.join(__dirname, 'index.html');
    let indexContent = await fs.readFile(indexPath, 'utf-8');
    
    // Fájl tartalmak kinyerése
    const fileContents = await extractAllContent();
    
    // fileData objektum keresése az index.html-ben
    const fileDataMatch = indexContent.match(/const fileData = (\{[\s\S]*?\});/);
    if (!fileDataMatch) {
        console.error('❌ Nem található fileData objektum az index.html-ben!');
        return;
    }
    
    let fileData;
    try {
        fileData = eval('(' + fileDataMatch[1] + ')');
    } catch (error) {
        console.error('❌ Hiba a fileData parse-olásánál:', error.message);
        return;
    }
    
    let updatedCount = 0;
    
    // Minden fájlhoz hozzáadjuk a content mezőt
    function addContentToFiles(categoryArray) {
        if (!Array.isArray(categoryArray)) return;
        
        categoryArray.forEach(file => {
            if (file.path) {
                const normalizedPath = file.path.replace(/\\/g, '/');
                // Próbáljuk meg közvetlenül
                if (fileContents[normalizedPath]) {
                    if (!file.content || file.content.length < fileContents[normalizedPath].content.length) {
                        file.content = fileContents[normalizedPath].content;
                        updatedCount++;
                        console.log(`  ✅ ${normalizedPath} - ${fileContents[normalizedPath].length} karakter`);
                    }
                } else {
                    // Ha nem találjuk, próbáljuk meg a Windows path formátummal is
                    const windowsPath = normalizedPath.replace(/\//g, '\\');
                    if (fileContents[windowsPath]) {
                        if (!file.content || file.content.length < fileContents[windowsPath].content.length) {
                            file.content = fileContents[windowsPath].content;
                            updatedCount++;
                            console.log(`  ✅ ${windowsPath} - ${fileContents[windowsPath].length} karakter`);
                        }
                    } else {
                        // Ha még mindig nem találjuk, keressük meg a fájlnév alapján
                        const fileName = normalizedPath.split('/').pop();
                        const foundEntry = Object.entries(fileContents).find(([key, value]) => 
                            key.includes(fileName) || value.path && value.path.includes(fileName)
                        );
                        if (foundEntry) {
                            const [key, value] = foundEntry;
                            if (!file.content || file.content.length < value.content.length) {
                                file.content = value.content;
                                updatedCount++;
                                console.log(`  ✅ ${fileName} (${key}) - ${value.length} karakter`);
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Core fájlok
    if (fileData.core) {
        console.log('📁 Core fájlok...');
        addContentToFiles(fileData.core);
    }
    
    // Specs fájlok
    if (fileData.specs) {
        console.log('📁 Specs fájlok...');
        addContentToFiles(fileData.specs);
    }
    
    // Docs fájlok
    if (fileData.docs) {
        console.log('📁 Docs fájlok...');
        Object.values(fileData.docs).forEach(subcategoryArray => {
            addContentToFiles(subcategoryArray);
        });
    }
    
    // Simulations fájlok
    if (fileData.simulations) {
        console.log('📁 Simulations fájlok...');
        addContentToFiles(fileData.simulations);
    }
    
    // Case studies fájlok
    if (fileData.case_studies) {
        console.log('📁 Case studies fájlok...');
        addContentToFiles(fileData.case_studies);
    }
    
    // Assets fájlok
    if (fileData.assets) {
        console.log('📁 Assets fájlok...');
        addContentToFiles(fileData.assets);
    }
    
    // Frissített fileData visszaírása
    // JSON.stringify helyett manuálisan építjük fel a stringet, hogy jobban kezelje a nagy fájlokat
    const fileDataString = buildFileDataString(fileData);
    indexContent = indexContent.replace(/const fileData = \{[\s\S]*?\};/, `const fileData = ${fileDataString};`);
    
    // Backup készítése
    const backupPath = path.join(__dirname, 'index.html.backup');
    await fs.copyFile(indexPath, backupPath);
    console.log(`\n💾 Backup készítve / Backup created: ${backupPath}`);
    
    // Frissített index.html mentése
    await fs.writeFile(indexPath, indexContent, 'utf-8');
    
    console.log(`\n✅ Kész! / Done!`);
    console.log(`  Frissítve / Updated: ${updatedCount} fájl`);
    console.log(`  index.html mentve / index.html saved`);
}

// Futtatás
if (require.main === module) {
    updateIndexWithContent()
        .then(() => {
            console.log('\n✅ Minden kész! / All done!');
            process.exit(0);
        })
        .catch(error => {
            console.error('\n❌ Hiba történt / Error occurred:', error);
            process.exit(1);
        });
}

module.exports = { updateIndexWithContent };

