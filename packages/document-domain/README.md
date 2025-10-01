# @valero-neuroerp/document-domain

**Document Platform** für VALEO-NeuroERP 3.0

Templating, Rendering (HTML→PDF), Signierung, Archivierung, Distribution.

## 📋 Features

- ✅ **Templating** (Handlebars, mehrsprachig)
- ✅ **Rendering** (HTML→PDF via Playwright)
- ✅ **Nummernkreise** (Race-safe, INV-2025-00001)
- ✅ **Signierung** (SHA-256, Timestamp, optional PAdES)
- ✅ **S3-Storage** (MinIO/AWS S3)
- ✅ **Signed URLs** (zeitlich begrenzt)

## 🚫 Abgrenzung

| Was document-domain NICHT tut |
|-------------------------------|
| ❌ Keine Geschäftslogik (Preise, Buchungen, Bestände) |
| ❌ Keine Steuerberechnung (nur Stammdaten) |
| ❌ Keine eInvoice-Validierung (nur File-Generation) |

**Nur:** Dokumente aus Payloads erzeugen!

## 🚀 Quick Start

```bash
npm install
npm run migrate:up
npm run dev  # Port 3070
```

## 📡 API (MVP)

```
POST /document/api/v1/documents            - Dokument erstellen
GET  /document/api/v1/documents/:id        - Metadaten
GET  /document/api/v1/documents/:id/file   - Signed URL
```

## 💡 Beispiel

```json
POST /document/api/v1/documents
{
  "docType": "invoice",
  "templateKey": "invoice_v1_de",
  "payload": {
    "invoiceNumber": "INV-2025-00123",
    "customer": { "name": "Müller GmbH" },
    "items": [{ "sku": "WHEAT-11.5", "qty": 25, "price": 210 }],
    "total": 5250
  },
  "locale": "de-DE",
  "seriesId": "series-invoice-2025",
  "options": { "sign": "timestamp", "qr": true }
}
```

## 🔗 Integration

- **Sales Domain** → Invoice, Credit-Note
- **Weighing Domain** → Weighing-Ticket
- **Contracts Domain** → Contract-PDF
- **Quality Domain** → Certificates (CoA/CoC)

## 📊 Port: 3070

**Status:** ✅ MVP Ready
