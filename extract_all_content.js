const fs = require('fs').promises;
const path = require('path');
const pdfParseModule = require('pdf-parse');
const PDFParse = pdfParseModule.PDFParse;
const mammoth = require('mammoth');

// Wrapper függvény a PDFParse osztály használatához
async function pdfParse(buffer, options = {}) {
    try {
        const uint8Array = buffer instanceof Buffer ? new Uint8Array(buffer) : buffer;
        const parser = new PDFParse(uint8Array, options);
        await parser.load();
        const textResult = await parser.getText();
        const text = (typeof textResult === 'string') ? textResult : (textResult.text || '');
        let info = null;
        try {
            info = await parser.getInfo();
        } catch (infoError) {
            // Ignore
        }
        return {
            text: text || '',
            numpages: parser.doc ? parser.doc.numPages : 1,
            info: info
        };
    } catch (error) {
        throw error;
    }
}

// Fájl olvasása (szöveges fájlokhoz és PDF-hez)
async function readFileContent(filePath) {
    try {
        const ext = path.extname(filePath).toLowerCase().slice(1);
        const textExtensions = ['txt', 'py', 'bio', 'md', 'js', 'json', 'html', 'css', 'xml', 'yaml', 'yml'];
        
        // PDF fájlok feldolgozása
        if (ext === 'pdf') {
            try {
                const buffer = await fs.readFile(filePath);
                const data = await pdfParse(buffer);
                return data.text || '';
            } catch (pdfError) {
                console.error(`Error parsing PDF ${filePath}:`, pdfError.message);
                return null;
            }
        }
        
        if (textExtensions.includes(ext)) {
            try {
                const content = await fs.readFile(filePath, { encoding: 'utf-8' });
                return content;
            } catch (encodingError) {
                const buffer = await fs.readFile(filePath);
                try {
                    return buffer.toString('utf-8');
                } catch {
                    return buffer.toString('latin1');
                }
            }
        }
        
        // DOCX fájlok feldolgozása
        if (ext === 'docx') {
            try {
                const buffer = await fs.readFile(filePath);
                const result = await mammoth.extractRawText({ buffer: buffer });
                return result.value || '';
            } catch (docxError) {
                console.error(`Error parsing DOCX ${filePath}:`, docxError.message);
                return null;
            }
        }
        
        // RTF fájlok esetén próbáljuk meg szövegként olvasni
        if (ext === 'rtf') {
            try {
                const buffer = await fs.readFile(filePath);
                const text = buffer.toString('utf-8');
                return text.length > 0 ? text : null;
            } catch {
                return null;
            }
        }
        
        return null;
    } catch (error) {
        console.error(`Error reading file ${filePath}:`, error.message);
        return null;
    }
}

// Rekurzív fájl keresés
async function getAllFiles(dirPath, arrayOfFiles = []) {
    const files = await fs.readdir(dirPath);
    
    for (const file of files) {
        const filePath = path.join(dirPath, file);
        const stat = await fs.stat(filePath);
        
        if (stat.isDirectory()) {
            // Kihagyjuk a node_modules, temp_uploads, és .git könyvtárakat
            if (!['node_modules', 'temp_uploads', '.git'].includes(file)) {
                arrayOfFiles = await getAllFiles(filePath, arrayOfFiles);
            }
        } else {
            arrayOfFiles.push(filePath);
        }
    }
    
    return arrayOfFiles;
}

// Fő függvény
async function extractAllContent() {
    console.log('📂 Fájlok tartalmának kinyerése... / Extracting file contents...\n');
    
    const baseDir = __dirname;
    const categories = {
        'core': 'core',
        'specs': 'specs',
        'simulations': 'simulations',
        'case_studies': 'case_studies',
        'assets': 'assets',
        'docs': {
            'strategic': 'docs/strategic',
            'technical': 'docs/technical',
            'patent': 'docs/patent',
            'theory': 'docs/theory',
            'validation': 'docs/validation'
        }
    };
    
    const fileContents = {};
    let totalFiles = 0;
    let processedFiles = 0;
    let errorFiles = 0;
    
    // Összes fájl összegyűjtése
    const allFiles = await getAllFiles(baseDir);
    
    // Kategóriák szerint csoportosítás
    for (const filePath of allFiles) {
        const relativePath = path.relative(baseDir, filePath);
        const ext = path.extname(filePath).toLowerCase().slice(1);
        
        // Csak szöveges fájlokat és PDF-eket dolgozunk fel
        const processableExts = ['txt', 'py', 'bio', 'md', 'js', 'json', 'html', 'css', 'xml', 'yaml', 'yml', 'pdf', 'docx', 'rtf'];
        if (!processableExts.includes(ext)) {
            continue;
        }
        
        // Kihagyjuk a node_modules, temp_uploads, és egyéb rendszer fájlokat
        if (relativePath.includes('node_modules') || 
            relativePath.includes('temp_uploads') || 
            relativePath.startsWith('.') ||
            path.basename(filePath) === 'index.html' ||
            path.basename(filePath).startsWith('package')) {
            continue;
        }
        
        totalFiles++;
        
        try {
            console.log(`Processing: ${relativePath}`);
            const content = await readFileContent(filePath);
            
            if (content && content.trim().length > 0) {
                // Max 50000 karakter (kereséshez)
                const contentForSearch = content.length > 50000 
                    ? content.substring(0, 50000) + '... [további tartalom kihagyva]'
                    : content;
                
                fileContents[relativePath] = {
                    path: relativePath.replace(/\\/g, '/'),
                    content: contentForSearch,
                    length: content.length
                };
                processedFiles++;
                console.log(`  ✅ ${content.length} karakter kinyerve / ${content.length} characters extracted`);
            } else {
                console.log(`  ⚠️  Üres vagy nem olvasható / Empty or unreadable`);
            }
        } catch (error) {
            console.error(`  ❌ Hiba / Error: ${error.message}`);
            errorFiles++;
        }
    }
    
    console.log(`\n📊 Összefoglaló / Summary:`);
    console.log(`  Összes fájl / Total files: ${totalFiles}`);
    console.log(`  Feldolgozva / Processed: ${processedFiles}`);
    console.log(`  Hiba / Errors: ${errorFiles}`);
    
    // Eredmények mentése JSON fájlba
    const outputPath = path.join(baseDir, 'file_contents.json');
    await fs.writeFile(outputPath, JSON.stringify(fileContents, null, 2), 'utf-8');
    console.log(`\n💾 Eredmények mentve / Results saved: ${outputPath}`);
    
    return fileContents;
}

// Futtatás
if (require.main === module) {
    extractAllContent()
        .then(() => {
            console.log('\n✅ Kész! / Done!');
            process.exit(0);
        })
        .catch(error => {
            console.error('\n❌ Hiba történt / Error occurred:', error);
            process.exit(1);
        });
}

module.exports = { extractAllContent, readFileContent };

