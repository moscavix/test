"use strict";

const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname, "..");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");
const escapeScript = (source) => source.replaceAll("</script", "<\\/script");

let html = read("index.html");
const css = read("styles.css");
const catalog = read("data/catalog.js");
const application = read("app.js");

html = html
  .replace('  <link rel="stylesheet" href="styles.css">', `  <style>\n${css}\n  </style>`)
  .replace('  <!-- La copia JavaScript del catalogo consente l\'apertura diretta via file://. -->\n', "")
  .replace('  <script src="data/catalog.js" defer></script>\n', "")
  .replace('  <script src="app.js" defer></script>\n', "")
  .replace("</body>", `  <script>\n${escapeScript(catalog)}\n${escapeScript(application)}\n  </script>\n</body>`);

if (html.includes('src="data/catalog.js"') || html.includes('src="app.js"') || html.includes('href="styles.css"')) {
  throw new Error("il file singolo contiene ancora dipendenze locali");
}

const outputDirectory = path.join(root, "dist");
const output = path.join(outputDirectory, "Esplora-Banca-d-Italia.html");
fs.mkdirSync(outputDirectory, { recursive: true });
fs.writeFileSync(output, html);
console.log(`generated ${path.relative(root, output)}`);
