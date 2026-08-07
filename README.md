# Esplora Banca d'Italia — demo statica

Una demo senza database e senza framework per esplorare un catalogo di risorse
della Banca d'Italia. Il progetto usa soltanto **JSON, JavaScript, HTML e CSS** e
può essere pubblicato su qualunque hosting statico.

## Avvio

Per provarla basta aprire `index.html` con un doppio clic: la copia JavaScript dei
dati viene caricata anche con il protocollo `file://`, senza server e senza rete.

### Versione singola per Windows

Nella cartella `dist` è disponibile `Esplora-Banca-d-Italia.html`: contiene nello
stesso file interfaccia, stile, programma e dati. Si può copiare su un PC Windows
e aprire con un doppio clic, senza conservare le altre cartelle del progetto.

In alternativa si può usare un piccolo server locale:

```sh
python3 -m http.server 8000
```

Aprire poi `http://localhost:8000`.

## Modello dei dati

`data/catalog.json` è la fonte dati leggibile e modificabile. `data/catalog.js`
ne contiene una copia equivalente utilizzabile direttamente dal browser locale.
Entrambi conservano separatamente:

- `resourceTypes`: vocabolario dei tipi;
- `topics`: tassonomia gerarchica degli argomenti;
- `navigationNodes`: albero editoriale con riferimenti padre-figlio;
- `resources`: schede delle risorse con riferimenti a tipo, argomenti e nodi.

JavaScript ricostruisce l'albero, applica ricerca e filtri e aggiorna i risultati
senza ricaricare la pagina. I link aprono sempre la risorsa originale sul sito
della Banca d'Italia; il catalogo non replica o altera i contenuti istituzionali.

Dopo avere modificato `data/catalog.json`, rigenerare la copia locale con:

```sh
node scripts/build-local-data.js
```

Per rigenerare anche il file HTML singolo per Windows:

```sh
node scripts/build-single-html.js
```

## Controlli

```sh
node tests/catalog.test.js
node --check app.js
```
