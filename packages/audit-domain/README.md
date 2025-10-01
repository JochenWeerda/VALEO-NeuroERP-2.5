# @valero-neuroerp/audit-domain

**Revisionssichere Protokollierung** für VALEO-NeuroERP 3.0

## 📋 Features

- ✅ **Hash-Chain** (SHA-256, unveränderbar)
- ✅ **Append-Only** (keine Updates/Deletes)
- ✅ **Event-Driven** (konsumiert alle Domain-Events)
- ✅ **Integritätsprüfung** (verifyIntegrity)
- ✅ **GoBD/HGB/ISO-konform**
- ✅ **Export** (CSV, PDF, JSON)

## 🚫 Abgrenzung

❌ Keine Geschäftslogik  
❌ Nur Logging & Audit!

## 🚀 Quick Start

```bash
npm install
npm run migrate:gen
npm run dev  # Port 3090
```

## 📡 API

```
POST /audit/api/v1/events              - Event loggen
GET  /audit/api/v1/events              - Events abfragen
GET  /audit/api/v1/events/:id          - Event abrufen
GET  /audit/api/v1/integrity/check     - Hash-Chain prüfen
```

## 💡 Beispiel

```json
POST /audit/api/v1/events
{
  "actor": { "userId": "user-123", "role": "Admin" },
  "action": "APPROVE",
  "target": { "type": "Contract", "id": "contract-456" },
  "payload": { "approvalAmount": 50000 },
  "ip": "192.168.1.100"
}
```

## 🔗 Integration

**Konsumiert Events von:**
- sales-domain
- contracts-domain
- document-domain
- notifications-domain
- weighing-domain
- quality-domain
- pricing-domain
- ... allen Domains!

## 📊 Port: 3090

**Status:** ✅ Production-Ready
