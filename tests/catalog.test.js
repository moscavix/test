"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const catalog = JSON.parse(fs.readFileSync(path.join(__dirname, "../data/catalog.json"), "utf8"));
const localData = fs.readFileSync(path.join(__dirname, "../data/catalog.js"), "utf8");
const expectedLocalData = `/* Generato da scripts/build-local-data.js: non modificare a mano. */\nwindow.CATALOG_DATA = ${JSON.stringify(catalog, null, 2)};\n`;
assert.equal(localData, expectedLocalData, "catalog.js non sincronizzato: eseguire node scripts/build-local-data.js");

const singleHtml = fs.readFileSync(path.join(__dirname, "../dist/Esplora-Banca-d-Italia.html"), "utf8");
assert.ok(singleHtml.includes("window.CATALOG_DATA"), "catalogo non incorporato nel file HTML singolo");
assert.ok(singleHtml.includes(":root"), "stili non incorporati nel file HTML singolo");
assert.ok(!singleHtml.includes('src="data/catalog.js"'), "dipendenza catalog.js rimasta nel file singolo");
assert.ok(!singleHtml.includes('src="app.js"'), "dipendenza app.js rimasta nel file singolo");
assert.ok(!singleHtml.includes('href="styles.css"'), "dipendenza CSS rimasta nel file singolo");

const unique = (items, label) => assert.equal(new Set(items.map((x) => x.id)).size, items.length, `${label}: ID duplicati`);
unique(catalog.resourceTypes, "tipi"); unique(catalog.topics, "argomenti"); unique(catalog.navigationNodes, "nodi"); unique(catalog.resources, "risorse");

const types = new Set(catalog.resourceTypes.map((x) => x.id));
const topics = new Set(catalog.topics.map((x) => x.id));
const nodes = new Map(catalog.navigationNodes.map((x) => [x.id, x]));
assert.equal(catalog.resources.length, 10);

for (const resource of catalog.resources) {
  assert.ok(types.has(resource.typeId), `${resource.id}: tipo inesistente`);
  assert.ok(resource.topicIds.length && resource.topicIds.every((id) => topics.has(id)), `${resource.id}: argomento inesistente`);
  assert.ok(resource.navigationNodeIds.length && resource.navigationNodeIds.every((id) => nodes.has(id)), `${resource.id}: nodo inesistente`);
  assert.equal(new URL(resource.url).hostname, "www.bancaditalia.it", `${resource.id}: host inatteso`);
}

for (const node of nodes.values()) {
  const visited = new Set([node.id]); let current = node;
  while (current.parentId) {
    assert.ok(nodes.has(current.parentId), `${node.id}: genitore inesistente`);
    assert.ok(!visited.has(current.parentId), `${node.id}: ciclo nell'albero`);
    visited.add(current.parentId); current = nodes.get(current.parentId);
  }
}
console.log("catalog references, URLs and navigation tree: OK");
