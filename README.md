# SentinelChain AI

SentinelChain AI is a premium AI-based fraud detection project for multi-tier supply chains. It combines anomaly detection, graph-aware supplier risk propagation, and explainable decision intelligence.

## What You Get

- Enterprise-style FastAPI backend with typed API contracts
- Hybrid AI scoring engine (anomaly + rules + network risk)
- Premium dashboard UI for real-time investigation
- Multi-tier supplier graph dataset and simulation endpoint
- One-command launch scripts for Windows

## Project Structure

```text
Intellitrance/
  backend/
    app/
      api/
      models/
      services/
      main.py
    data/
      supplier_network.json
  frontend/
    index.html
    assets/
      styles.css
      app.js
  scripts/
    start.ps1
    start.bat
  tests/
    smoke_test.ps1
  requirements.txt
  README.md
```

## Quick Start

1. Create and activate virtual environment:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start.ps1
```

4. Open in browser:

- App URL: `http://127.0.0.1:8000`
- API Docs: `http://127.0.0.1:8000/docs`

## API Endpoints

- `GET /api/health`
- `GET /api/network/summary`
- `POST /api/fraud/evaluate`
- `POST /api/fraud/simulate`

## Example Evaluate Payload

```json
{
  "transaction_id": "TXN-22044",
  "supplier_id": "SUP-108",
  "buyer_id": "BUY-208",
  "invoice_amount": 98000,
  "invoice_currency": "USD",
  "invoice_count_last_30d": 18,
  "shipment_distance_km": 870,
  "shipment_delay_hours": 28,
  "payment_term_days": 15,
  "contract_value": 140000,
  "country_risk_index": 0.62,
  "sanctions_hit": false,
  "beneficial_owner_mismatch": true,
  "split_invoice_pattern": true,
  "tier_level": 3
}
```

## Premium Product Positioning

SentinelChain AI is designed as a premium fraud-intelligence platform that can sit on top of ERP, procurement, and logistics systems. It emphasizes explainable outcomes and network-aware controls to reduce payment fraud, shell-entity abuse, and hidden upstream risk.
