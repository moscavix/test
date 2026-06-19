# Word Accessibility Fixer

Questa app da riga di comando analizza un documento Word `.docx`, segnala i problemi di accessibilità più comuni e crea una nuova copia del documento con correzioni automatiche pensate per avvicinarsi ai controlli del Controllo accessibilità di Microsoft Word.

> Nota: i file legacy `.doc` sono binari e devono essere convertiti prima in `.docx` con Word o LibreOffice. L'app non modifica mai il documento originale.

## Funzionalità

- Imposta una lingua predefinita del documento (`it-IT`) quando manca.
- Aggiunge un titolo documento nelle proprietà se assente.
- Aggiunge testo alternativo provvisorio alle immagini prive di descrizione.
- Marca la prima riga delle tabelle come intestazione quando non esiste già.
- Corregge salti nella gerarchia dei titoli, ad esempio da `Heading 1` a `Heading 3`.
- Rimuove paragrafi vuoti usati come spaziatura.
- Sostituisce testi link ambigui come “clicca qui” con un'etichetta più descrittiva.
- Produce un report JSON con problemi rilevati e correzioni applicate.

## Installazione locale

```bash
python -m pip install -e .
```

## Uso

```bash
word-a11y-fix documento.docx documento-accessibile.docx --report report-accessibilita.json
```

L'output è un nuovo file `.docx`. Il report elenca codice problema, severità, posizione e correzione applicata.

## Limiti importanti

Alcune verifiche di Word richiedono giudizio umano o informazioni che non sono ricavabili in modo affidabile dal solo file, per esempio la qualità semantica del testo alternativo, l'ordine di lettura in layout complessi o la chiarezza reale dei nomi dei link. In questi casi l'app applica correzioni sicure e segnala nel report gli elementi che andrebbero rivisti.
