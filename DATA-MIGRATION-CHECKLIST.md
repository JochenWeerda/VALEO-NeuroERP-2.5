# 📋 Datenmigrationen-Checkliste – L3 → VALERO NeuroERP

**Zweck:** Sichere, vollständige und nachvollziehbare Migration von L3 (doku.service-erp.de) nach NeuroERP.

**Scope:** Stammdaten, Bewegungsdaten, Dokumente, Historie

---

## 🎯 Migrations-Strategie

### Gesamtansatz: Stepwise Migration + Dual-Run

```
Phase 1: Stammdaten (Kunden, Artikel, Lieferanten)
   ↓
Phase 2: Historische Daten (Verträge, Rechnungen, Lieferscheine)
   ↓
Phase 3: Laufende Geschäftsvorfälle (parallel L3 + NeuroERP)
   ↓
Phase 4: Vollumschaltung (L3 read-only)
   ↓
Phase 5: L3-Archivierung (Zugriff nur noch für Audit)
```

**Dauer:** 4-8 Wochen (abhängig von Datenmenge)

---

## 📦 Daten-Kategorien

### 1. Stammdaten (Master Data)

| Entität | L3-Quelle | NeuroERP-Ziel | Priorität |
|---------|-----------|---------------|-----------|
| **Kunden** | `customers` | crm-domain | 🔴 HOCH |
| **Lieferanten** | `suppliers` | procurement-domain | 🔴 HOCH |
| **Artikel** | `products` | inventory-domain | 🔴 HOCH |
| **Lager/Silos** | `warehouses` | inventory-domain | 🔴 HOCH |
| **Mitarbeiter** | `employees` | hr-domain | 🟡 MITTEL |
| **Fahrzeuge** | `vehicles` | fleet-domain | 🟡 MITTEL |

### 2. Transaktionsdaten

| Entität | L3-Quelle | NeuroERP-Ziel | Priorität |
|---------|-----------|---------------|-----------|
| **Verträge** | `contracts` | contracts-domain | 🔴 HOCH |
| **Rechnungen** | `invoices` | sales-domain | 🔴 HOCH |
| **Lieferscheine** | `delivery_notes` | weighing-domain | 🔴 HOCH |
| **Wiegungen** | `weighings` | weighing-domain | 🔴 HOCH |
| **Zahlungen** | `payments` | finance-domain | 🟡 MITTEL |
| **Prüfergebnisse** | `quality_checks` | quality-domain | 🟢 NIEDRIG |

### 3. Dokumente & Anhänge

| Typ | L3-Quelle | NeuroERP-Ziel | Speicher |
|-----|-----------|---------------|----------|
| **Rechnungs-PDFs** | `/docs/invoices/` | document-domain | S3 |
| **Vertrags-PDFs** | `/docs/contracts/` | document-domain | S3 |
| **Zertifikate** | `/docs/certs/` | regulatory-domain | S3 |
| **Prüfprotokolle** | `/docs/quality/` | quality-domain | S3 |

---

## 🗺️ Feldmapping (Beispiel: Kunden)

### L3 → NeuroERP (CRM-Domain)

| L3-Feld | NeuroERP-Feld | Transformation | Validierung |
|---------|---------------|----------------|-------------|
| `customer_id` | `customerId` | Direct | UUID-Format |
| `name` | `companyName` | Direct | Min 1 char |
| `vat_id` | `vatId` | Trim + Uppercase | DE\d{9} |
| `address` | `address.street` | Split | - |
| `zip` | `address.postalCode` | Direct | 5 digits |
| `city` | `address.city` | Direct | - |
| `country_code` | `address.country` | ISO 3166-1 | DE, AT, CH |
| `payment_terms` | `paymentTerms` | Days → Enum | 14d, 30d, 60d |
| `credit_limit` | `creditLimit` | EUR cents | > 0 |

**Spezialfälle:**
- `customer_group` (L3) → `segmentation.tier` (NeuroERP) via Mapping-Tabelle
- `salesperson` (L3) → `owner.userId` (NeuroERP) via Employee-Lookup

---

## 🧪 Test-Strategie

### 1. Mapping-Tests (Dry-Run)

**Schritt 1:** Export aus L3 (10 Testkunden)
```bash
curl https://doku.service-erp.de/api/customers?limit=10 > test_customers.json
```

**Schritt 2:** Mapping ausführen (ohne Import)
```bash
npm run migrate:test -- --source test_customers.json --mapping customers.map.json
```

**Schritt 3:** Validierung
- ✅ Alle Pflichtfelder gemappt
- ✅ Keine Dubletten (customerId unique)
- ✅ Referenzen auflösbar (salesperson → userId)

**Ergebnis:** Mapping-Report mit Fehler-/Warnungsanzahl

---

### 2. Probeimport (Staging)

**Schritt 1:** 100 Kunden importieren (Staging-DB)
```bash
npm run migrate:import -- --env staging --source customers_sample.json --limit 100
```

**Schritt 2:** Plausibilitätsprüfungen
- Anzahl: 100 Datensätze in DB?
- Referenzen: Alle `ownerId` vorhanden?
- Duplikate: Keine doppelten `customerId`?

**Schritt 3:** Stichproben (manuell)
- 10 zufällige Kunden öffnen
- Felder gegen L3 vergleichen

**Ergebnis:** ✅/❌ Freigabe für Vollimport

---

### 3. Vollimport (Production)

**Schritt 1:** Backup erstellen
```bash
pg_dump -h prod-db -U valero -d neuroerp > backup_pre_migration.sql
```

**Schritt 2:** Import starten (batched)
```bash
npm run migrate:import -- --env production --source customers_full.json --batch-size 1000
```

**Monitoring:**
- Fortschritt: 1000/5000 (20%)
- Fehler: 12 (DLQ)
- Dauer: ~15 Min

**Schritt 3:** Post-Import-Validierung
```bash
# Zählung
SELECT COUNT(*) FROM customers WHERE tenant_id = 'tenant-abc';

# Integritätsprüfung
GET /audit/api/v1/integrity/check?from=<migration-start>
```

---

## 🔄 Rollback-Strategie

### Option 1: DB-Restore (für Vollimport-Fehler)

```bash
# Stop Services
kubectl scale deployment document-domain --replicas=0

# Restore Backup
psql -h prod-db -U valero -d neuroerp < backup_pre_migration.sql

# Start Services
kubectl scale deployment document-domain --replicas=3
```

**Downtime:** ~10-30 Min (abhängig von DB-Größe)

---

### Option 2: Soft-Delete (für Partial-Import-Fehler)

```sql
-- Markiere migrierte Datensätze als ungültig
UPDATE customers SET deleted_at = NOW()
WHERE created_at > '<migration-start>' AND migration_source = 'L3';
```

**Downtime:** ❌ Keine

---

### Option 3: DLQ-Nachbearbeitung (für einzelne Fehler)

```bash
# Export Failed Records
GET /integration/api/v1/dlq?source=L3&entity=customers

# Korrigieren, Re-Import
npm run migrate:retry -- --dlq-id <job-id>
```

**Downtime:** ❌ Keine

---

## 📊 Feldmapping-Tabellen (Referenz)

### Artikelgruppen (L3 → NeuroERP)

| L3-Code | L3-Name | NeuroERP-Code | NeuroERP-Name |
|---------|---------|---------------|---------------|
| `WZ` | Weizen | `WHEAT` | Weichweizen |
| `GS` | Gerste | `BARLEY` | Futtergerste |
| `RP` | Raps | `RAPESEED` | Raps (konventionell) |
| `DM` | Dünger | `FERTILIZER` | Mineraldünger |

### Zahlungsbedingungen

| L3-Code | NeuroERP-Enum | Tage |
|---------|---------------|------|
| `14T` | `NET_14` | 14 |
| `30T` | `NET_30` | 30 |
| `SKT2` | `DISCOUNT_2_14_NET_30` | 2% bei 14d, sonst 30d |

---

## ✅ Migrations-Checkliste

### Vor der Migration

- [ ] **Scope definiert** (welche Daten, welcher Zeitraum)
- [ ] **Mapping-Tabellen erstellt** (alle Felder dokumentiert)
- [ ] **Test-Exports aus L3** (10-100 Datensätze)
- [ ] **Dry-Run erfolgreich** (Mapping ohne Import)
- [ ] **Backup erstellt** (Production-DB)
- [ ] **Rollback-Plan bereit** (DB-Restore oder Soft-Delete)
- [ ] **Stakeholder informiert** (Timeline, Downtime)
- [ ] **Audit: Migration als Draft protokolliert**

### Während der Migration

- [ ] **Batch-Import läuft** (Progress-Monitoring)
- [ ] **DLQ überwacht** (Fehlerrate < 1%)
- [ ] **Logs überwacht** (keine Crashes)
- [ ] **Referenzen auflösbar** (Foreign Keys valide)
- [ ] **Notifications verschickt** (Start, Fortschritt)
- [ ] **Audit: Jede Batch geloggt**

### Nach der Migration

- [ ] **Zählung korrekt** (SELECT COUNT vs. L3-Export)
- [ ] **Stichproben** (10-20 Datensätze manuell prüfen)
- [ ] **Referenzen valide** (keine Orphans)
- [ ] **Integritätsprüfung** (Audit-Domain)
- [ ] **DLQ abgearbeitet** (Fehler korrigiert und re-imported)
- [ ] **Dokumente migriert** (PDFs in S3, Metadaten in DB)
- [ ] **UAT-Tests** (User Acceptance Testing)
- [ ] **Freigabe durch Stakeholder**
- [ ] **Audit: Migration als Completed protokolliert**
- [ ] **L3: Read-Only oder Archiv-Modus**

---

## 🔍 Qualitätssicherung

### Automatische Validierung

```typescript
// Beispiel: Validierung nach Import
async function validateCustomerMigration(tenantId: string) {
  const stats = await db.execute(`
    SELECT 
      COUNT(*) as total,
      COUNT(DISTINCT customer_id) as unique_ids,
      COUNT(CASE WHEN vat_id IS NULL THEN 1 END) as missing_vat,
      COUNT(CASE WHEN credit_limit < 0 THEN 1 END) as negative_credit
    FROM customers
    WHERE tenant_id = $1 AND migration_source = 'L3'
  `, [tenantId]);

  return {
    total: stats.total,
    duplicates: stats.total - stats.unique_ids,
    missingVat: stats.missing_vat,
    negativeCredit: stats.negative_credit,
    valid: stats.duplicates === 0 && stats.negative_credit === 0
  };
}
```

### Manuelle Stichproben

**Kriterien:**
- ✅ 10 zufällige Datensätze gegen L3 vergleichen
- ✅ Alle Pflichtfelder gefüllt
- ✅ Formatierung korrekt (Datum, Währung, PLZ)
- ✅ Referenzen auflösbar (Artikel → customerId)

---

## 🚨 Risiken & Mitigationen

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| **Dubletten** | Mittel | Hoch | Unique-Constraints, Pre-Check |
| **Referenz-Fehler** | Hoch | Hoch | Foreign-Key-Validierung vor Import |
| **Daten-Verlust** | Niedrig | Kritisch | Backup vor Migration, Vergleich Counts |
| **Fehlerhafte Mappings** | Mittel | Mittel | Dry-Run, Stichproben, DLQ |
| **Performance** | Niedrig | Mittel | Batching (1000er), Off-Peak-Import |

---

## 📁 Migrations-Artefakte

### Input
- `customers_l3_export.json` (L3-Export)
- `customers_mapping.json` (Feldmapping)
- `customers_transformations.js` (Custom-Logic)

### Output
- `migration_report_customers.pdf` (Status, Fehler, Statistiken)
- `dlq_customers.json` (fehlgeschlagene Datensätze)
- `audit_trail_migration.json` (revisionssicher)

### Speicherort
```
/migrations/
  ├── l3-to-neuroerp/
  │   ├── exports/
  │   │   ├── customers_2025-10-01.json
  │   │   ├── contracts_2025-10-01.json
  │   │   └── invoices_2025-10-01.json
  │   ├── mappings/
  │   │   ├── customers.map.json
  │   │   └── contracts.map.json
  │   ├── reports/
  │   │   ├── migration_report_customers.pdf
  │   │   └── dlq_customers.json
  │   └── backups/
  │       └── backup_pre_migration_2025-10-01.sql
```

---

## 🔄 Dual-Run-Strategie

### Phase 1-2: NeuroERP als Slave (read-only)
```
L3 (Master) ──┐
              ├──> NeuroERP (Sync, Reports)
Neue Daten  ──┘
```

### Phase 3: Dual-Write (beide Systeme parallel)
```
Neue Daten ──┬──> L3 (Master)
             └──> NeuroERP (Testing)
```

### Phase 4: NeuroERP als Master
```
Neue Daten ──> NeuroERP (Master)
                  ├──> L3 (read-only, Archiv)
                  └──> Reports, Analytics
```

**Dauer Phase 3:** 2-4 Wochen (Validierung, User-Training)

---

## 🧪 Test-Szenarien

### Szenario 1: Kundenstamm (100 Kunden)

**Input:** `customers_test.json` (100 Datensätze)

**Schritte:**
1. Dry-Run (Mapping-Validierung)
2. Staging-Import
3. Stichproben (10 Kunden manuell prüfen)
4. Freigabe für Production-Import

**Success-Kriterien:**
- ✅ 100 Datensätze importiert
- ✅ 0 Fehler in DLQ
- ✅ Alle VAT-IDs korrekt formatiert
- ✅ Payment-Terms gemappt

---

### Szenario 2: Vertragsdaten (500 Verträge)

**Input:** `contracts_test.json` (500 Datensätze, 2 Jahre Historie)

**Schritte:**
1. Referenz-Check (customerId, commodityId existieren?)
2. Datumsformat-Prüfung (ISO 8601)
3. Mengen/Preise-Plausibilität (> 0, < 1 Mio)
4. Import in contracts-domain

**Success-Kriterien:**
- ✅ 500 Verträge importiert
- ✅ Referenzen valide (0 Orphans)
- ✅ Summen korrekt (Total = Σ Lines)
- ✅ Status-Mapping korrekt (Open/Closed/Fulfilled)

---

### Szenario 3: Wiegungen (10.000 Datensätze)

**Input:** `weighings_2024.json` (komplettes Jahr 2024)

**Schritte:**
1. Batching (1000er-Schritte)
2. Progress-Monitoring
3. Performance-Check (< 2 Min/Batch)
4. Integritätsprüfung (Brutto - Tara = Netto)

**Success-Kriterien:**
- ✅ 10.000 Wiegungen importiert
- ✅ Brutto/Tara/Netto-Berechnungen korrekt
- ✅ Alle Tickets haben Document-Link (PDF)
- ✅ Import-Dauer < 20 Min

---

## 📊 KI-gestützte Mapping-Engine

### Automatische Vorschläge

```javascript
// Beispiel: Fuzzy-Matching für Artikel-Kategorien
const l3Categories = ['WZ', 'GS', 'RP', 'DM', 'SF'];
const neuroCategories = ['WHEAT', 'BARLEY', 'RAPESEED', 'FERTILIZER', 'ANIMAL_FEED'];

// KI-Modell schlägt Mapping vor:
{
  "WZ": { "suggestion": "WHEAT", "confidence": 0.95 },
  "GS": { "suggestion": "BARLEY", "confidence": 0.92 },
  "RP": { "suggestion": "RAPESEED", "confidence": 0.98 },
  "DM": { "suggestion": "FERTILIZER", "confidence": 0.88 },
  "SF": { "suggestion": "ANIMAL_FEED", "confidence": 0.75 }  // niedrig → manuell prüfen
}
```

**Integration:** analytics-domain trainiert Mapping-Modell aus Mustern

---

## 🔐 Audit-Trail für Migration

### Was wird protokolliert?

1. **Import-Files** (Original-JSON aus L3)
   - Speicherort: S3 Bucket `valero-migrations/`
   - Retention: 10 Jahre (GoBD)

2. **Mapping-Logs**
   - Welches Feld → wohin
   - Transformationen
   - Fehler/Warnings

3. **DLQ (Dead Letter Queue)**
   - Fehlgeschlagene Datensätze
   - Fehlergrund
   - Retry-Versuche

4. **Success-Metriken**
   - Importiert: 4.988 / 5.000 (99.76%)
   - DLQ: 12 (0.24%)
   - Dauer: 18 Min

5. **Audit-Events**
   ```json
   {
     "action": "IMPORT",
     "target": { "type": "Customer", "id": "migration-batch-001" },
     "payload": {
       "source": "L3",
       "count": 1000,
       "success": 998,
       "failed": 2
     }
   }
   ```

---

## 🚀 Migrations-Workflow (End-to-End)

### Woche 1-2: Vorbereitung
- [ ] L3-API-Zugang testen
- [ ] Export-Skripte erstellen
- [ ] Mapping-Tabellen definieren
- [ ] Test-Exports durchführen (10-100 Datensätze)
- [ ] Dry-Run erfolgreich

### Woche 3: Staging-Migration
- [ ] Stammdaten importieren (Kunden, Artikel, Lieferanten)
- [ ] Stichproben prüfen
- [ ] Referenzen validieren
- [ ] Freigabe durch Stakeholder

### Woche 4: Production-Migration (Stammdaten)
- [ ] Backup erstellen
- [ ] Off-Peak-Import (nachts)
- [ ] Post-Import-Validierung
- [ ] Audit-Trail vollständig

### Woche 5-6: Transaktionsdaten
- [ ] Verträge (historisch)
- [ ] Rechnungen (historisch)
- [ ] Lieferscheine (historisch)
- [ ] Wiegungen (historisch)

### Woche 7-8: Dual-Run-Phase
- [ ] Neue Daten parallel in L3 + NeuroERP
- [ ] User-Training
- [ ] Validierung durch Fachbereiche
- [ ] Freigabe für Vollumschaltung

### Woche 9: Vollumschaltung
- [ ] NeuroERP wird Master
- [ ] L3 auf read-only
- [ ] Benachrichtigungen an alle User
- [ ] Monitoring verschärft (24h)

### Woche 10+: Nachbereitung
- [ ] L3-Archivierung
- [ ] DLQ abarbeiten (Restfehler)
- [ ] Dokumentation finalisieren
- [ ] Lessons Learned
- [ ] Freigabe für L3-Abschaltung (nach 6 Monaten)

---

## 📞 Support-Kontakte

| Rolle | Name | Erreichbarkeit |
|-------|------|----------------|
| **Migration Lead** | TBD | migration@valero.de |
| **L3-Support** | Service-ERP | support@service-erp.de |
| **DevOps** | TBD | devops@valero.de |
| **Audit Officer** | TBD | audit@valero.de |

---

## 📈 Success-Kriterien

✅ **Migration erfolgreich, wenn:**
- Alle Stammdaten importiert (> 99%)
- DLQ-Rate < 1%
- Stichproben korrekt (100% Feldvergleich)
- Referenzen valide (0 Orphans)
- Audit-Trail vollständig
- Freigabe durch Stakeholder
- UAT-Tests bestanden

---

**Version:** 1.0  
**Datum:** Oktober 2025  
**Owner:** Migration Team + DevOps
