import json
from pathlib import Path
from random import choice, randint, uniform
from typing import Dict, List

import numpy as np
from sklearn.ensemble import IsolationForest

from app.models.schemas import FraudEvaluationRequest


class FraudEngine:
    def __init__(self) -> None:
        self._model = IsolationForest(
            n_estimators=120,
            contamination=0.14,
            random_state=42,
        )
        self._fit_model()
        self._network = self._load_network()

    def _fit_model(self) -> None:
        rng = np.random.default_rng(42)
        normal = np.column_stack(
            [
                rng.normal(42000, 12000, 900),
                rng.normal(10, 4, 900),
                rng.normal(650, 220, 900),
                rng.normal(8, 5, 900),
                rng.normal(45, 10, 900),
                rng.normal(0.32, 0.12, 900),
            ]
        )

        anomalies = np.column_stack(
            [
                rng.normal(118000, 25000, 150),
                rng.normal(28, 8, 150),
                rng.normal(1250, 400, 150),
                rng.normal(42, 14, 150),
                rng.normal(12, 5, 150),
                rng.normal(0.74, 0.15, 150),
            ]
        )

        train_data = np.vstack([normal, anomalies])
        self._model.fit(train_data)

    def _load_network(self) -> Dict:
        root = Path(__file__).resolve().parents[3]
        file_path = root / "backend" / "data" / "supplier_network.json"
        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _anomaly_score(self, payload: FraudEvaluationRequest) -> float:
        sample = np.array(
            [
                [
                    payload.invoice_amount,
                    payload.invoice_count_last_30d,
                    payload.shipment_distance_km,
                    payload.shipment_delay_hours,
                    payload.payment_term_days,
                    payload.country_risk_index,
                ]
            ]
        )
        raw = self._model.decision_function(sample)[0]
        normalized = float(np.clip((0.35 - raw) / 0.7, 0, 1))
        return normalized

    def _rule_score(self, payload: FraudEvaluationRequest) -> float:
        score = 0.0
        if payload.sanctions_hit:
            score += 0.45
        if payload.beneficial_owner_mismatch:
            score += 0.2
        if payload.split_invoice_pattern:
            score += 0.15
        if payload.shipment_delay_hours > 36:
            score += 0.1
        if payload.invoice_amount > (payload.contract_value * 0.85):
            score += 0.1
        return float(np.clip(score, 0, 1))

    def _network_score(self, payload: FraudEvaluationRequest) -> float:
        suppliers = self._network.get("suppliers", {})
        supplier = suppliers.get(payload.supplier_id)
        if not supplier:
            return 0.3

        intrinsic = supplier.get("base_risk", 0.3)
        upstream = supplier.get("upstream", [])
        upstream_avg = (
            sum(suppliers.get(node, {}).get("base_risk", 0.3) for node in upstream) / len(upstream)
            if upstream
            else intrinsic
        )

        tier_pressure = min(payload.tier_level / 6.0, 1.0)
        geo_pressure = payload.country_risk_index * 0.35

        return float(np.clip((intrinsic * 0.45) + (upstream_avg * 0.35) + (tier_pressure * 0.2) + geo_pressure, 0, 1))

    @staticmethod
    def _band(score: float) -> str:
        if score >= 0.78:
            return "Critical"
        if score >= 0.58:
            return "High"
        if score >= 0.36:
            return "Medium"
        return "Low"

    def evaluate(self, payload: FraudEvaluationRequest) -> Dict:
        anomaly = self._anomaly_score(payload)
        rule = self._rule_score(payload)
        network = self._network_score(payload)

        weighted = (anomaly * 0.44) + (rule * 0.28) + (network * 0.28)
        risk_score = float(np.clip(weighted, 0, 1))
        risk_band = self._band(risk_score)

        reason_codes: List[str] = []
        if anomaly > 0.6:
            reason_codes.append("ANOMALOUS_TRANSACTION_PATTERN")
        if rule > 0.4:
            reason_codes.append("RULE_ALERT_TRIGGERED")
        if network > 0.55:
            reason_codes.append("SUPPLIER_NETWORK_RISK_PROPAGATION")
        if payload.sanctions_hit:
            reason_codes.append("SANCTIONS_PROXIMITY")
        if payload.split_invoice_pattern:
            reason_codes.append("INVOICE_SPLITTING_SIGNAL")
        if not reason_codes:
            reason_codes.append("NO_MATERIAL_ALERTS")

        recommendation = {
            "Critical": "Block payment, run enhanced due diligence, and notify compliance immediately.",
            "High": "Hold transaction, request ownership proof, and perform manual review.",
            "Medium": "Approve conditionally and monitor counterparty activity for 30 days.",
            "Low": "Approve with standard controls.",
        }[risk_band]

        return {
            "transaction_id": payload.transaction_id,
            "risk_score": round(risk_score, 4),
            "risk_band": risk_band,
            "score_breakdown": {
                "anomaly_score": round(anomaly, 4),
                "rule_score": round(rule, 4),
                "network_score": round(network, 4),
            },
            "reason_codes": reason_codes,
            "recommendation": recommendation,
        }

    def network_summary(self) -> Dict:
        suppliers = self._network.get("suppliers", {})
        tiers = [entry.get("tier", 1) for entry in suppliers.values()]
        avg_risk = sum(entry.get("base_risk", 0.3) for entry in suppliers.values()) / max(len(suppliers), 1)
        return {
            "total_suppliers": len(suppliers),
            "max_tier": max(tiers) if tiers else 1,
            "average_base_risk": round(avg_risk, 3),
            "critical_suppliers": [supplier_id for supplier_id, value in suppliers.items() if value.get("base_risk", 0) > 0.75],
        }

    def random_assessment(self) -> Dict:
        supplier_id = choice(list(self._network.get("suppliers", {}).keys()))
        payload = FraudEvaluationRequest(
            transaction_id=f"SIM-{randint(10000, 99999)}",
            supplier_id=supplier_id,
            buyer_id=f"BUY-{randint(100, 999)}",
            invoice_amount=round(uniform(18000, 130000), 2),
            invoice_currency="USD",
            invoice_count_last_30d=randint(4, 34),
            shipment_distance_km=round(uniform(100, 1700), 2),
            shipment_delay_hours=round(uniform(0, 56), 2),
            payment_term_days=randint(7, 70),
            contract_value=round(uniform(60000, 180000), 2),
            country_risk_index=round(uniform(0.12, 0.88), 3),
            sanctions_hit=choice([False, False, False, True]),
            beneficial_owner_mismatch=choice([False, False, True]),
            split_invoice_pattern=choice([False, False, True]),
            tier_level=randint(1, 5),
        )
        return self.evaluate(payload)
