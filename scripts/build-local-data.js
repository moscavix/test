"use strict";

const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname, "..");
const source = path.join(root, "data/catalog.json");
const destination = path.join(root, "data/catalog.js");
const catalog = JSON.parse(fs.readFileSync(source, "utf8"));

// JSON.stringify impedisce che dati non validi producano una copia JavaScript.
const output = `/* Generato da scripts/build-local-data.js: non modificare a mano. */\nwindow.CATALOG_DATA = ${JSON.stringify(catalog, null, 2)};\n`;
fs.writeFileSync(destination, output);
console.log(`generated ${path.relative(root, destination)}`);
