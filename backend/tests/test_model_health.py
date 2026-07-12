"""Tests du suivi de la fraude & santé du modèle (MLOps).

La métrique centrale — précision réelle en production — est calculée sur
les QUALIFICATIONS du directeur (boucle de feedback), pas sur le jeu de
test d'entraînement : c'est la santé du modèle telle que l'agence la vit.
"""

from tests.test_clients_api import VALID_CLIENT


def _seed_two_alerts(client, advisor):
    """Un client, un compte, 7 transactions dont 2 suspectes -> 2 alertes."""
    cid = client.post(
        "/clients", headers=advisor, json={**VALID_CLIENT, "monthly_income": "4000"}
    ).json()["id"]
    aid = client.post(
        "/accounts", headers=advisor, json={"client_id": cid, "initial_balance": "90000"}
    ).json()["id"]
    for _ in range(5):
        client.post(
            "/transactions", headers=advisor,
            json={"transaction_type": "deposit", "amount": "150",
                  "account_id": aid, "city": "Casablanca"},
        )
    for amount, city in (("40000", "Agadir"), ("35000", "Tanger")):
        client.post(
            "/transactions", headers=advisor,
            json={"transaction_type": "withdrawal", "amount": amount,
                  "account_id": aid, "city": city},
        )


def _qualify(client, director, alert_id, resolution):
    client.patch(f"/alerts/{alert_id}", headers=director, json={"status": "in_progress"})
    client.patch(
        f"/alerts/{alert_id}", headers=director,
        json={"status": "closed", "resolution": resolution},
    )


def test_model_health_empty_state(client, auth_headers):
    """Sans aucune donnée : pas de division par zéro, valeurs neutres."""
    health = client.get("/analytics/model-health", headers=auth_headers("director")).json()

    assert health["alerts_processed"] == 0
    assert health["precision_production"] is None
    assert health["false_positive_rate"] is None
    assert health["score_distribution"] == []
    assert health["model_version"] is None


def test_model_health_reflects_feedback(client, auth_headers):
    advisor, director = auth_headers("advisor"), auth_headers("director")
    _seed_two_alerts(client, advisor)

    alerts = client.get("/alerts", headers=director).json()
    assert len(alerts) == 2
    _qualify(client, director, alerts[0]["id"], "confirmed_fraud")
    _qualify(client, director, alerts[1]["id"], "false_positive")

    health = client.get("/analytics/model-health", headers=director).json()

    assert health["alerts_processed"] == 2
    assert health["confirmed_fraud"] == 1
    assert health["false_positives"] == 1
    assert health["precision_production"] == 0.5      # 1 confirmée / 2 qualifiées
    assert health["false_positive_rate"] == 0.5
    assert health["feedback_available"] == 2          # étiquettes pour réentraîner
    assert health["open_alerts"] == 0
    assert health["model_version"] == "mvp-rules-v1"  # conftest force les règles
    assert health["total_scored"] == 7                # chaque transaction est scorée
    assert sum(b["count"] for b in health["score_distribution"]) == 7
    assert health["avg_processing_hours"] is not None


def test_model_health_requires_director(client, auth_headers):
    assert (
        client.get("/analytics/model-health", headers=auth_headers("advisor")).status_code == 403
    )
