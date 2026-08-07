/* Generato da scripts/build-local-data.js: non modificare a mano. */
window.CATALOG_DATA = {
  "meta": {
    "title": "Esplora Banca d'Italia",
    "description": "Catalogo dimostrativo di risorse pubbliche",
    "updatedAt": "2026-08-07",
    "source": "https://www.bancaditalia.it/"
  },
  "resourceTypes": [
    {
      "id": "page",
      "label": "Pagina informativa"
    },
    {
      "id": "publication",
      "label": "Pubblicazione"
    },
    {
      "id": "report",
      "label": "Rapporto",
      "parentId": "publication"
    },
    {
      "id": "dataset",
      "label": "Dati e statistiche"
    },
    {
      "id": "service",
      "label": "Servizio"
    }
  ],
  "topics": [
    {
      "id": "economy",
      "label": "Economia e moneta"
    },
    {
      "id": "monetary-policy",
      "label": "Politica monetaria",
      "parentId": "economy"
    },
    {
      "id": "italian-economy",
      "label": "Economia italiana",
      "parentId": "economy"
    },
    {
      "id": "financial-system",
      "label": "Sistema finanziario"
    },
    {
      "id": "supervision",
      "label": "Vigilanza",
      "parentId": "financial-system"
    },
    {
      "id": "payments",
      "label": "Pagamenti e moneta"
    },
    {
      "id": "statistics",
      "label": "Statistiche"
    },
    {
      "id": "citizens",
      "label": "Cittadini e famiglie"
    },
    {
      "id": "research",
      "label": "Ricerca economica"
    }
  ],
  "navigationNodes": [
    {
      "id": "home",
      "label": "Tutte le risorse",
      "order": 0
    },
    {
      "id": "economy",
      "label": "Economia e moneta",
      "parentId": "home",
      "order": 10
    },
    {
      "id": "monetary",
      "label": "Politica monetaria",
      "parentId": "economy",
      "order": 10
    },
    {
      "id": "financial",
      "label": "Sistema finanziario",
      "parentId": "home",
      "order": 20
    },
    {
      "id": "supervision",
      "label": "Vigilanza",
      "parentId": "financial",
      "order": 10
    },
    {
      "id": "payments",
      "label": "Pagamenti e moneta",
      "parentId": "home",
      "order": 30
    },
    {
      "id": "data",
      "label": "Dati e statistiche",
      "parentId": "home",
      "order": 40
    },
    {
      "id": "citizens",
      "label": "Per cittadini e famiglie",
      "parentId": "home",
      "order": 50
    }
  ],
  "resources": [
    {
      "id": "annual-report",
      "title": "Relazione annuale",
      "typeId": "report",
      "description": "La relazione sull'attività della Banca e sull'economia italiana.",
      "url": "https://www.bancaditalia.it/pubblicazioni/relazione-annuale/",
      "topicIds": [
        "italian-economy"
      ],
      "navigationNodeIds": [
        "economy"
      ],
      "language": "it",
      "featured": true
    },
    {
      "id": "economic-bulletin",
      "title": "Bollettino economico",
      "typeId": "publication",
      "description": "Analisi congiunturale dell'economia italiana e internazionale.",
      "url": "https://www.bancaditalia.it/pubblicazioni/bollettino-economico/",
      "topicIds": [
        "italian-economy",
        "monetary-policy"
      ],
      "navigationNodeIds": [
        "economy",
        "monetary"
      ],
      "language": "it",
      "featured": true
    },
    {
      "id": "regional-economies",
      "title": "Economie regionali",
      "typeId": "report",
      "description": "Analisi delle economie e dei territori italiani.",
      "url": "https://www.bancaditalia.it/pubblicazioni/economie-regionali/",
      "topicIds": [
        "italian-economy"
      ],
      "navigationNodeIds": [
        "economy"
      ],
      "language": "it"
    },
    {
      "id": "working-papers",
      "title": "Temi di discussione",
      "typeId": "publication",
      "description": "Lavori di ricerca economica prodotti dalla Banca d'Italia.",
      "url": "https://www.bancaditalia.it/pubblicazioni/temi-discussione/",
      "topicIds": [
        "research"
      ],
      "navigationNodeIds": [
        "economy"
      ],
      "language": "it"
    },
    {
      "id": "qef",
      "title": "Questioni di economia e finanza",
      "typeId": "publication",
      "description": "Studi e documentazione su temi economici e finanziari.",
      "url": "https://www.bancaditalia.it/pubblicazioni/qef/",
      "topicIds": [
        "research",
        "financial-system"
      ],
      "navigationNodeIds": [
        "economy",
        "financial"
      ],
      "language": "it"
    },
    {
      "id": "statistics",
      "title": "Statistiche",
      "typeId": "dataset",
      "description": "Il punto di accesso alle statistiche prodotte dalla Banca d'Italia.",
      "url": "https://www.bancaditalia.it/statistiche/",
      "topicIds": [
        "statistics"
      ],
      "navigationNodeIds": [
        "data"
      ],
      "language": "it",
      "featured": true
    },
    {
      "id": "monetary-policy",
      "title": "Politica monetaria",
      "typeId": "page",
      "description": "Il ruolo della Banca d'Italia nell'Eurosistema e nella politica monetaria.",
      "url": "https://www.bancaditalia.it/compiti/polmon-garanzie/",
      "topicIds": [
        "monetary-policy"
      ],
      "navigationNodeIds": [
        "monetary"
      ],
      "language": "it"
    },
    {
      "id": "supervision",
      "title": "Vigilanza bancaria e finanziaria",
      "typeId": "page",
      "description": "Obiettivi, strumenti e attività della vigilanza sul sistema finanziario.",
      "url": "https://www.bancaditalia.it/compiti/vigilanza/",
      "topicIds": [
        "supervision"
      ],
      "navigationNodeIds": [
        "supervision"
      ],
      "language": "it",
      "featured": true
    },
    {
      "id": "payment-systems",
      "title": "Sistemi di pagamento e mercati",
      "typeId": "page",
      "description": "Infrastrutture, sistemi di pagamento e attività sui mercati.",
      "url": "https://www.bancaditalia.it/compiti/sispaga-mercati/",
      "topicIds": [
        "payments"
      ],
      "navigationNodeIds": [
        "payments"
      ],
      "language": "it"
    },
    {
      "id": "citizen-services",
      "title": "Servizi per il cittadino",
      "typeId": "service",
      "description": "Informazioni, strumenti e servizi rivolti direttamente al pubblico.",
      "url": "https://www.bancaditalia.it/servizi-cittadino/",
      "topicIds": [
        "citizens"
      ],
      "navigationNodeIds": [
        "citizens"
      ],
      "language": "it",
      "featured": true
    }
  ]
};
