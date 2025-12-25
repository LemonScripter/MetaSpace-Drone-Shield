const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');
const archiver = require('archiver');
const { exec } = require('child_process');
const util = require('util');
const { createWriteStream } = require('fs');

const execPromise = util.promisify(exec);

// Email címek
const EMAIL_RECIPIENTS = [
    'lszoke@gmail.com',
    'planxmod@gmail.com',
    'szeklerwood@gmail.com'
];

// Dokumentumok listája (kritikus és fontos fájlok)
const DOCUMENT_PATHS = [
    // Core fájlok
    'core/metaspace_core_engine.py',
    'core/METASPACE CORE ENGINE - VERSION 1.3 (SOVEREIGN SWARM).py',
    'core/METASPACE PRO - SECRET CORE MODULE.py',
    
    // Specs
    'specs/uav_integrity_shield.bio',
    'specs/AF447_Integrity_Layer.bio',
    'specs/bank.bio',
    'specs/repuloautomata.bio',
    
    // Dokumentációk
    'docs/patent/PATENT APPLICATION - TECHNICAL SPECIFICATION.docx',
    'docs/patent/PATENT APPLICATION - TECHNICAL SPECIFICATION.rtf',
    'docs/theory/A Titkos Mag (Secret Core) Felépítése.txt',
    'docs/theory/3_piller_ido_energia_kozosseg.txt',
    'docs/theory/MetaSpace A Determinisztikus Heuris.txt',
    'docs/theory/MetaSpace A Sejttől a .bio Nyelvig.txt',
    'docs/technical/MetaSpace_ Technological Analysis and IP Protection.docx',
    'docs/strategic/EXECUTIVE SUMMARY_ MetaSpace Logic Engine.rtf',
    'docs/strategic/MetaSpace Logic Engine - Stratégiai Dokumentáció.docx',
    
    // Szimulációk
    'simulations/AF447.py',
    'simulations/MetaSpace_AF447_Divergencia.py',
    
    // Esettanulmányok
    'case_studies/Esettanulmány_ Air France 447 (AF447) .rtf',
    
    // Biztonsági dokumentumok
    'SECURITY_ANALYSIS.md',
    'PROTECTED_FILES_LIST.md'
];

// Verzió meghatározása
async function getVersion() {
    try {
        // Git verzió használata, ha van
        const { stdout } = await execPromise('git rev-parse --short HEAD').catch(() => ({ stdout: 'unknown' }));
        const gitHash = stdout.trim();
        
        // Dátum alapú verzió
        const now = new Date();
        const dateStr = now.toISOString().split('T')[0].replace(/-/g, '');
        const timeStr = now.toTimeString().split(' ')[0].replace(/:/g, '').substring(0, 4);
        
        return {
            version: `v${dateStr}-${timeStr}`,
            gitHash: gitHash !== 'unknown' ? gitHash : null,
            timestamp: now.toISOString(),
            date: dateStr,
            time: timeStr
        };
    } catch (error) {
        const now = new Date();
        const dateStr = now.toISOString().split('T')[0].replace(/-/g, '');
        const timeStr = now.toTimeString().split(' ')[0].replace(/:/g, '').substring(0, 4);
        return {
            version: `v${dateStr}-${timeStr}`,
            gitHash: null,
            timestamp: now.toISOString(),
            date: dateStr,
            time: timeStr
        };
    }
}

// SHA-256 hash generálása
async function generateSHA256(filePath) {
    try {
        const fileBuffer = await fs.readFile(filePath);
        const hashSum = crypto.createHash('sha256');
        hashSum.update(fileBuffer);
        return hashSum.digest('hex');
    } catch (error) {
        console.error(`Error generating hash for ${filePath}:`, error);
        return null;
    }
}

// ZIP fájl létrehozása
async function createZipPackage(version, outputDir) {
    return new Promise(async (resolve, reject) => {
        const zipFileName = `MetaSpace_Patent_Documents_${version.version}.zip`;
        const zipPath = path.join(outputDir, zipFileName);
        
        const output = createWriteStream(zipPath);
        const archive = archiver('zip', {
            zlib: { level: 9 } // Maximum compression
        });
        
        output.on('close', () => {
            console.log(`✅ ZIP fájl létrehozva: ${zipPath}`);
            console.log(`   Méret: ${archive.pointer()} bytes`);
            resolve(zipPath);
        });
        
        archive.on('error', (err) => {
            reject(err);
        });
        
        archive.pipe(output);
        
        // Fájlok hozzáadása
        let addedFiles = 0;
        let skippedFiles = 0;
        
        for (const filePath of DOCUMENT_PATHS) {
            const fullPath = path.join(__dirname, filePath);
            try {
                await fs.access(fullPath);
                archive.file(fullPath, { name: filePath });
                addedFiles++;
                console.log(`   ✓ Hozzáadva: ${filePath}`);
            } catch (error) {
                skippedFiles++;
                console.log(`   ⚠ Kihagyva (nem található): ${filePath}`);
            }
        }
        
        // Verzió információ hozzáadása
        const versionInfo = {
            version: version.version,
            gitHash: version.gitHash,
            timestamp: version.timestamp,
            filesIncluded: addedFiles,
            filesSkipped: skippedFiles,
            generated: new Date().toISOString()
        };
        
        archive.append(JSON.stringify(versionInfo, null, 2), { name: 'VERSION_INFO.json' });
        
        // README hozzáadása
        const readmeContent = `MetaSpace Patent Documents Package
================================

Verzió / Version: ${version.version}
Generálva / Generated: ${version.timestamp}
Git Hash: ${version.gitHash || 'N/A'}

Ez a csomag tartalmazza a MetaSpace találmányhoz kapcsolódó összes szükséges dokumentumot.

This package contains all necessary documents related to the MetaSpace invention.

Fájlok száma / File count: ${addedFiles}
Kihagyott fájlok / Skipped files: ${skippedFiles}

Fontos / Important:
- A fájlok szabadalmi oltalom alatt állnak / Files are under patent protection
- SOHA ne osszuk meg nyilvánosan / NEVER share publicly
- Csak engedélyezett személyekkel / Only with authorized persons
`;
        
        archive.append(readmeContent, { name: 'README.txt' });
        
        archive.finalize();
    });
}

// Email levél generálása
function generateEmailContent(sha256Hash, version, zipFileName) {
    const subject = `MetaSpace Patent Documents - ${version.version} - SHA-256 Hash`;
    
    const body = `Tisztelt Kolléga!

A MetaSpace találmányhoz kapcsolódó dokumentumok ZIP csomagjának SHA-256 hash értéke:

SHA-256 Hash: ${sha256Hash}

Verzió / Version: ${version.version}
Fájlnév / Filename: ${zipFileName}
Generálva / Generated: ${version.timestamp}
${version.gitHash ? `Git Hash: ${version.gitHash}` : ''}

Ez a hash érték biztosítja a dokumentumok integritását és változatlanságát.

Kérjük, tárolja ezt a hash értéket a dokumentumok hitelesítéséhez.

Üdvözlettel,
MetaSpace Development Team

---
Dear Colleague!

SHA-256 hash value of the ZIP package containing documents related to the MetaSpace invention:

SHA-256 Hash: ${sha256Hash}

Version: ${version.version}
Filename: ${zipFileName}
Generated: ${version.timestamp}
${version.gitHash ? `Git Hash: ${version.gitHash}` : ''}

This hash value ensures the integrity and immutability of the documents.

Please store this hash value for document authentication.

Best regards,
MetaSpace Development Team`;
    
    return { subject, body };
}

// Email küldés (mailto link)
function sendEmails(sha256Hash, version, zipFileName) {
    const { subject, body } = generateEmailContent(sha256Hash, version, zipFileName);
    
    console.log('\n📧 Email küldés előkészítése...');
    console.log('   Címzettek / Recipients:');
    EMAIL_RECIPIENTS.forEach(email => {
        console.log(`   - ${email}`);
    });
    
    // Mailto link generálása
    const mailtoLinks = EMAIL_RECIPIENTS.map(email => {
        return `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    });
    
    console.log('\n📋 Email tartalom / Email content:');
    console.log('─────────────────────────────────────');
    console.log(decodeURIComponent(body));
    console.log('─────────────────────────────────────\n');
    
    // Platform-specifikus email küldés
    const platform = process.platform;
    
    if (platform === 'win32') {
        // Windows - Outlook vagy alapértelmezett email kliens
        mailtoLinks.forEach((mailtoLink, index) => {
            exec(`start "" "${mailtoLink}"`, (error) => {
                if (error) {
                    console.error(`❌ Hiba az email küldésnél ${EMAIL_RECIPIENTS[index]}:`, error);
                } else {
                    console.log(`✅ Email előkészítve: ${EMAIL_RECIPIENTS[index]}`);
                }
            });
        });
    } else if (platform === 'darwin') {
        // macOS
        mailtoLinks.forEach((mailtoLink, index) => {
            exec(`open "${mailtoLink}"`, (error) => {
                if (error) {
                    console.error(`❌ Hiba az email küldésnél ${EMAIL_RECIPIENTS[index]}:`, error);
                } else {
                    console.log(`✅ Email előkészítve: ${EMAIL_RECIPIENTS[index]}`);
                }
            });
        });
    } else {
        // Linux
        mailtoLinks.forEach((mailtoLink, index) => {
            exec(`xdg-open "${mailtoLink}"`, (error) => {
                if (error) {
                    console.error(`❌ Hiba az email küldésnél ${EMAIL_RECIPIENTS[index]}:`, error);
                } else {
                    console.log(`✅ Email előkészítve: ${EMAIL_RECIPIENTS[index]}`);
                }
            });
        });
    }
    
    console.log('\n💡 Az email kliens automatikusan megnyílik. Kérjük, ellenőrizze és küldje el az emaileket!');
    console.log('💡 The email client will open automatically. Please review and send the emails!');
    
    // Visszaadjuk a mailto linkeket a frontend számára
    return mailtoLinks;
}

// Fő függvény
async function packageAndSend() {
    try {
        console.log('🚀 MetaSpace Dokumentum Csomagolás és Email Küldés');
        console.log('🚀 MetaSpace Document Packaging and Email Sending');
        console.log('='.repeat(60));
        
        // Verzió meghatározása
        console.log('\n📌 Verzió meghatározása...');
        const version = await getVersion();
        console.log(`   Verzió / Version: ${version.version}`);
        if (version.gitHash) {
            console.log(`   Git Hash: ${version.gitHash}`);
        }
        console.log(`   Időbélyeg / Timestamp: ${version.timestamp}`);
        
        // Output könyvtár létrehozása
        const outputDir = path.join(__dirname, 'exports');
        await fs.mkdir(outputDir, { recursive: true });
        console.log(`\n📁 Output könyvtár / Output directory: ${outputDir}`);
        
        // ZIP fájl létrehozása
        console.log('\n📦 ZIP fájl létrehozása...');
        const zipPath = await createZipPackage(version, outputDir);
        const zipFileName = path.basename(zipPath);
        
        // SHA-256 hash generálása
        console.log('\n🔐 SHA-256 hash generálása...');
        const sha256Hash = await generateSHA256(zipPath);
        if (!sha256Hash) {
            throw new Error('SHA-256 hash generálása sikertelen');
        }
        console.log(`   SHA-256: ${sha256Hash}`);
        
        // Hash fájl mentése
        const hashFilePath = path.join(outputDir, `${zipFileName}.sha256`);
        await fs.writeFile(hashFilePath, `${sha256Hash}  ${zipFileName}\n`, 'utf-8');
        console.log(`   Hash fájl mentve / Hash file saved: ${hashFilePath}`);
        
        // Verzió információ mentése
        const versionInfoPath = path.join(outputDir, `VERSION_${version.version}.json`);
        const versionInfo = {
            version: version.version,
            gitHash: version.gitHash,
            timestamp: version.timestamp,
            zipFile: zipFileName,
            sha256Hash: sha256Hash,
            filesIncluded: DOCUMENT_PATHS.length
        };
        await fs.writeFile(versionInfoPath, JSON.stringify(versionInfo, null, 2), 'utf-8');
        console.log(`   Verzió információ mentve / Version info saved: ${versionInfoPath}`);
        
        // Email küldés
        console.log('\n📧 Email küldés...');
        const emailLinks = sendEmails(sha256Hash, version, zipFileName);
        
        console.log('\n✅ Kész! / Done!');
        console.log(`   ZIP fájl: ${zipPath}`);
        console.log(`   SHA-256: ${sha256Hash}`);
        console.log(`   Verzió: ${version.version}`);
        
        // Visszatérési érték a frontend számára
        return {
            success: true,
            zipFile: zipFileName,
            zipPath: zipPath,
            sha256: sha256Hash,
            version: version.version,
            gitHash: version.gitHash,
            timestamp: version.timestamp,
            emailLinks: emailLinks,
            filesIncluded: DOCUMENT_PATHS.length
        };
        
    } catch (error) {
        console.error('❌ Hiba történt / Error occurred:', error);
        throw error; // Ne process.exit(), hanem dobjuk a hibát, hogy a server.js kezelhesse
    }
}

// Futtatás
if (require.main === module) {
    packageAndSend();
}

module.exports = { packageAndSend, generateSHA256, getVersion };

