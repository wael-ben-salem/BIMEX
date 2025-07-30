#!/usr/bin/env node

// Script Node.js pour convertir un fichier IFC en XKT
// Usage: node convert_ifc.js <source_ifc> <output_xkt>

import { convert2xkt } from '../src/convert2xkt.js';
import path from 'path';
import fs from 'fs';

const args = process.argv.slice(2);

if (args.length < 2) {
    console.error('Usage: node convert_ifc.js <source_ifc> <output_xkt>');
    process.exit(1);
}

const sourceIfc = args[0];
const outputXkt = args[1];

console.log('=== Conversion IFC vers XKT ===');
console.log('Fichier source:', sourceIfc);
console.log('Fichier de sortie:', outputXkt);

// Vérifier que le fichier source existe
if (!fs.existsSync(sourceIfc)) {
    console.error('Erreur: Fichier source introuvable:', sourceIfc);
    process.exit(1);
}

// Créer le dossier de sortie si nécessaire
const outputDir = path.dirname(outputXkt);
if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
}

// Convertir les chemins en absolus
const absoluteSourceIfc = path.resolve(sourceIfc);
const absoluteOutputXkt = path.resolve(outputXkt);

console.log('Chemin source absolu:', absoluteSourceIfc);
console.log('Chemin sortie absolu:', absoluteOutputXkt);

// Lancer la conversion
convert2xkt({
    source: absoluteSourceIfc,
    output: absoluteOutputXkt,
    log: (msg) => console.log('[CONVERT]', msg)
}).then(() => {
    console.log('=== Conversion terminée avec succès ===');
    console.log('Fichier XKT créé:', absoluteOutputXkt);
    process.exit(0);
}).catch(err => {
    console.error('=== Erreur de conversion ===');
    console.error('Message:', err.message || err);
    console.error('Stack trace:', err.stack || 'Pas de stack trace');
    process.exit(1);
});
