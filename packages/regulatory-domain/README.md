# @valero-neuroerp/regulatory-domain

**Regulatory Compliance & Labels Domain** für VALEO-NeuroERP 3.0

Zentrale Verwaltung von Compliance-Regeln, Zertifikaten, Labels und rechtlichen Nachweisen in der Agrar-/Futtermittel-Wertschöpfungskette.

## 📋 Überblick

Die Regulatory-Domain ist verantwortlich für:

- **VLOG** ("Ohne Gentechnik") - Zertifizierung & Monitoring nach EGGenTDurchfG
- **QS** (Qualität & Sicherheit) - Futtermittelmonitoring gemäß QS-Leitfaden
- **PSM-Zulassungen** - Abgleich gegen BVL-Datenbank (Bundesamt für Verbraucherschutz)
- **THG-Werte** (RED II) - Treibhausgas-Berechnungen (Default/Actual) für Biokraftstoffe
- **Dokumentationspflichten** - Rückverfolgbarkeit gem. VO (EG) 178/2002 & 183/2005
- **Labels & Compliance-Cases** - Bewertung, Vergabe, Widerruf

## 🏗️ Domänenmodell

### 1. Regulatory Policies
Definition von Compliance-Regelwerken (VLOG, QS, RED II, etc.)

**Beispiel VLOG-Policy:**
- Input muss GVO-frei sein (Lieferanten-Erklärung)
- Strikte Trennung GVO/Nicht-GVO
- Reinigungsprotokolle
- GVO-Monitoring (mind. 1 Probe pro Charge)

### 2. Labels
Zertifikate/Qualitätssiegel für Batches, Contracts, Sites

**Verfügbare Labels:**
- `VLOG_OGT` - VLOG "Ohne Gentechnik"
- `QS` - QS Qualität & Sicherheit
- `REDII_COMPLIANT` - RED II THG-konform
- `GMP_PLUS`, `NON_GMO`, `ORGANIC_EU`, `ISCC`, `RTRS`, `RSPO`

### 3. Evidence (Nachweise)
Compliance-Dokumente: Zertifikate, Labor-Reports, Lieferanten-Erklärungen, Wiegescheine

### 4. PSM Product References
Pflanzenschutzmittel-Datenbank (gecacht von BVL)

### 5. GHG Pathways
THG-Emissionspfade für Biokraftstoffe (RED II Default/Actual)

### 6. Compliance Cases
Verstöße, Audit-Findings, fehlende Dokumentation

## 🚀 Quick Start

```bash
# Installation
npm install

# Environment-Variablen
cp .env.example .env

# Datenbank-Migrationen
npm run migrate:up

# Entwicklungsserver
npm run dev
```

## 📡 API-Endpunkte

### Base URL
`http://localhost:3008/regulatory/api/v1`

### Labels & Evaluation

```
POST /labels/evaluate       - Label-Eligibility prüfen (Kern-Feature!)
GET  /labels                - Labels auflisten
GET  /labels/:id            - Label abrufen
POST /labels/:id/revoke     - Label widerrufen
```

### PSM (Pflanzenschutzmittel)

```
POST /psm/check             - PSM gegen BVL prüfen
GET  /psm/search            - PSM in BVL suchen
```

### GHG (Treibhausgase)

```
POST /ghg/calc              - THG-Emissionen berechnen (RED II)
GET  /ghg/pathways          - GHG-Pfade auflisten
```

### KTBL (Landwirtschafts-Emissionen)

```
GET  /ktbl/status                    - KTBL-Service-Status
GET  /ktbl/crop-emissions/:crop      - Emissionsparameter abrufen
POST /ktbl/calculate                 - Berechnung mit Farm-Daten
```

### Health

```
GET  /health                - Server-Status
GET  /ready                 - Bereitschaft
GET  /live                  - Liveness
```

## 💡 Beispiele

### 1. VLOG-Label prüfen

```bash
POST /regulatory/api/v1/labels/evaluate
Content-Type: application/json
x-tenant-id: 123e4567-e89b-12d3-a456-426614174000

{
  "targetRef": {
    "type": "Batch",
    "id": "batch-uuid-123"
  },
  "labelCode": "VLOG_OGT",
  "context": {
    "vlog.input.gvo_free": true,
    "vlog.process.separation": true
  }
}

# Response:
{
  "eligible": false,
  "status": "Conditional",
  "missingEvidences": [
    "SupplierDeclaration: Alle Inputs müssen GVO-frei sein",
    "LabReport: GVO-Monitoring-Proben"
  ],
  "violations": [],
  "recommendation": "Label kann vergeben werden sobald fehlende Nachweise eingereicht sind.",
  "confidence": 0.6
}
```

### 2. PSM-Compliance prüfen

```bash
POST /regulatory/api/v1/psm/check
Content-Type: application/json
x-tenant-id: 123e4567-e89b-12d3-a456-426614174000

{
  "items": [
    {
      "name": "Roundup PowerFlex",
      "bvlId": "024266-00",
      "useDate": "2025-06-01T00:00:00Z",
      "cropOrUseCase": "Raps"
    }
  ],
  "batchId": "batch-uuid-123"
}

# Response:
{
  "compliant": true,
  "items": [
    {
      "name": "Roundup PowerFlex",
      "bvlId": "024266-00",
      "status": "Approved",
      "approved": true,
      "validUntil": "2025-12-31T23:59:59Z",
      "issues": []
    }
  ],
  "violations": [],
  "recommendation": "Alle PSM sind zugelassen und gültig."
}
```

### 3. THG-Berechnung (RED II)

```bash
POST /regulatory/api/v1/ghg/calc
Content-Type: application/json
x-tenant-id: 123e4567-e89b-12d3-a456-426614174000

{
  "commodity": "RAPE_OIL",
  "method": "Default",
  "originRegion": "DE-Hamburg"
}

# Response:
{
  "id": "pathway-uuid",
  "commodity": "RAPE_OIL",
  "pathwayKey": "DE-Hamburg-RAPE_OIL-Default",
  "method": "Default",
  "totalEmissions": 52,
  "savingsVsFossil": 38,
  "rediiThreshold": 60,
  "rediiCompliant": false,
  "factors": {
    "cultivation": 20.8,
    "processing": 15.6,
    "transport": 10.4,
    "landUseChange": 5.2
  }
}
```

## 🔗 Integration mit anderen Domains

### Production Domain
- Prüft Label-Eligibility vor Batch-Freigabe
- Sperrt Batches bei Compliance-Verstößen

### Contracts Domain
- Vertragsklauseln für Labels/Standards
- Claims bei Label-Revocation

### Quality Domain
- Labor-Ergebnisse als Evidence
- NCs können Compliance-Cases auslösen

### Weighing Domain
- Wiegescheine als Traceability-Evidence

## 🔔 Domain-Events

### Label Events
- `regulatory.label.eligible`
- `regulatory.label.ineligible`
- `regulatory.label.conditional`
- `regulatory.label.revoked`

### PSM Events
- `regulatory.psm.checked`
- `regulatory.psm.violation`

### GHG Events
- `regulatory.ghg.pathway.created`
- `regulatory.ghg.compliance.passed|failed`

### Policy Events
- `regulatory.policy.created`
- `regulatory.policy.updated`

### Compliance Events
- `regulatory.case.opened`
- `regulatory.case.resolved`

## 📚 Rechtliche Grundlagen

### VLOG "Ohne Gentechnik"
- Standard: [ohnegentechnik.org](https://ohnegentechnik.org)
- Rechtsbasis: EGGenTDurchfG (Gentechnik-Durchführungsgesetz)

### QS Futtermittelmonitoring
- Leitfaden 01/2025: [q-s.de](https://www.q-s.de)

### EU-Rückverfolgbarkeit
- VO (EG) 178/2002 - Lebensmittelrecht
- VO (EG) 183/2005 - Futtermittelhygiene

### BVL PSM-Datenbank
- [apps2.bvl.bund.de/psm](https://apps2.bvl.bund.de/psm/jsp)

### RED II (THG-Werte)
- [JRC Biofuels Database](https://joint-research-centre.ec.europa.eu)
- Annex V & VI Default-Werte

### KTBL BEK (THG-Landwirtschaft)
- [KTBL BEK-Parameter](https://www.ktbl.de/webanwendungen/bek-parameter)
- Status: Aktuell offline, Fallback-Daten aktiv
- Kontakt: ktbl@ktbl.de

## 🧪 Testing

```bash
# Unit-Tests
npm run test

# E2E-Tests
npm run test:e2e

# Coverage
npm run test:coverage
```

## 🐳 Docker

```bash
# Build
docker build -t valero-regulatory-domain:latest .

# Run
docker run -d \
  --name regulatory-domain \
  -p 3008:3008 \
  -e DATABASE_URL=postgres://... \
  -e NATS_URL=nats://... \
  valero-regulatory-domain:latest
```

## 🔐 Security & Permissions

### Required Headers
```http
Authorization: Bearer <JWT>
x-tenant-id: <UUID>
```

### Permissions
- `regulatory:policy:manage`
- `regulatory:label:evaluate`
- `regulatory:label:issue`
- `regulatory:label:revoke`
- `regulatory:evidence:upload`
- `regulatory:compliance:audit`

## 📊 Observability

- **OpenTelemetry** - Distributed Tracing
- **Pino** - Strukturierte Logs
- **Prometheus** - Metriken (via OTel)
- **Health Checks** - `/health`, `/ready`, `/live`

## 📝 Lizenz

Proprietary - VALEO GmbH

---

**Status:** ✅ Production-Ready  
**Version:** 0.1.0  
**Port:** 3008
