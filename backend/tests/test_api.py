"""
Integration tests for the FastAPI API endpoints.

Uses FastAPI's TestClient (backed by httpx) — no running server required.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestHealth:
    def test_health_returns_ok(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_health_content_type_is_json(self):
        response = client.get("/api/health")
        assert "application/json" in response.headers["content-type"]


class TestListApplications:
    def test_returns_200(self):
        response = client.get("/api/applications")
        assert response.status_code == 200

    def test_returns_all_fixtures(self):
        response = client.get("/api/applications")
        data = response.json()
        assert data["count"] == 7
        assert len(data["items"]) == 7

    def test_each_item_has_required_fields(self):
        response = client.get("/api/applications")
        items = response.json()["items"]
        required_fields = {
            "id", "applicant_name", "programme_applied",
            "review_status", "submitted_at", "eligibility_outcome", "data_source",
        }
        for item in items:
            assert required_fields.issubset(item.keys()), (
                f"Item {item.get('id')} is missing fields: {required_fields - item.keys()}"
            )

    def test_data_source_is_fixture_for_all(self):
        response = client.get("/api/applications")
        items = response.json()["items"]
        for item in items:
            assert item["data_source"] == "fixture", (
                f"Application {item['id']} has unexpected data_source '{item['data_source']}'"
            )

    def test_eligibility_outcome_is_valid_enum(self):
        valid_outcomes = {"eligible", "ineligible", "requires_review"}
        response = client.get("/api/applications")
        for item in response.json()["items"]:
            assert item["eligibility_outcome"] in valid_outcomes


class TestGetApplication:
    def test_returns_known_application(self):
        response = client.get("/api/applications/APP-2024-001")
        assert response.status_code == 200
        data = response.json()
        assert data["application"]["id"] == "APP-2024-001"
        assert data["application"]["applicant_name"] == "Priya Rajan"

    def test_returns_404_for_unknown_id(self):
        response = client.get("/api/applications/DOES-NOT-EXIST")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_detail_contains_eligibility(self):
        response = client.get("/api/applications/APP-2024-001")
        data = response.json()
        assert "eligibility" in data
        assert "outcome" in data["eligibility"]
        assert "rules" in data["eligibility"]
        assert "summary" in data["eligibility"]

    def test_detail_rules_have_evidence(self):
        response = client.get("/api/applications/APP-2024-001")
        rules = response.json()["eligibility"]["rules"]
        assert len(rules) == 5
        for rule in rules:
            assert rule["evidence"], f"Rule {rule['rule_id']} has empty evidence"

    def test_documents_have_status_field(self):
        response = client.get("/api/applications/APP-2024-001")
        docs = response.json()["application"]["documents"]
        for doc in docs:
            assert "status" in doc
            assert doc["status"] in {"present", "missing", "unreadable"}

    def test_academic_record_has_source_note(self):
        response = client.get("/api/applications/APP-2024-001")
        record = response.json()["application"]["academic_record"]
        assert "source_note" in record
        assert "fixture" in record["source_note"].lower()

    def test_detail_contains_consistency(self):
        response = client.get("/api/applications/APP-2024-001")
        data = response.json()
        assert "consistency" in data
        assert data["consistency"]["status"] == "consistent"
        assert data["consistency"]["application_id"] == "APP-2024-001"
        assert len(data["consistency"]["findings"]) == 4

    def test_detail_consistency_mismatch(self):
        response = client.get("/api/applications/APP-2024-002")
        assert response.status_code == 200
        consistency = response.json()["consistency"]
        assert consistency["status"] == "mismatch"
        assert any(f["status"] == "mismatch" for f in consistency["findings"])

    def test_detail_consistency_inconclusive(self):
        response = client.get("/api/applications/APP-2024-004")
        assert response.status_code == 200
        findings = response.json()["consistency"]["findings"]
        assert any(f["status"] == "inconclusive" for f in findings)

    def test_unknown_application_returns_404(self):
        response = client.get("/api/applications/UNKNOWN-ID")
        assert response.status_code == 404
        assert "consistency" not in response.json()

    def test_all_fixture_ids_return_200(self):
        ids = [
            "APP-2024-001", "APP-2024-002", "APP-2024-003",
            "APP-2024-004", "APP-2024-005", "APP-2024-006", "APP-2024-007",
        ]
        for app_id in ids:
            response = client.get(f"/api/applications/{app_id}")
            assert response.status_code == 200, f"Expected 200 for {app_id}"
