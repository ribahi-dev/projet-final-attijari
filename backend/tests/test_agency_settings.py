"""Tests du seuil d'alerte configurable (gouvernance du dispositif).

Le point fonctionnel VÉRIFIÉ de bout en bout : changer le seuil change
réellement le déclenchement des alertes sur les transactions suivantes.
"""

from tests.test_clients_api import VALID_CLIENT


def _tx_score_80(client, advisor, cin):
    """Scénario calibré : score RÈGLES = 80 exactement.

    retrait 2x le revenu (+45) + changement de ville (+20)
    + cumul 72h à 2,1x le revenu (+15) = 80.
    """
    cid = client.post(
        "/clients", headers=advisor,
        json={**VALID_CLIENT, "cin": cin, "monthly_income": "4000"},
    ).json()["id"]
    aid = client.post(
        "/accounts", headers=advisor, json={"client_id": cid, "initial_balance": "90000"}
    ).json()["id"]
    for _ in range(2):
        client.post(
            "/transactions", headers=advisor,
            json={"transaction_type": "deposit", "amount": "150",
                  "account_id": aid, "city": "Casablanca"},
        )
    return client.post(
        "/transactions", headers=advisor,
        json={"transaction_type": "withdrawal", "amount": "8000",
              "account_id": aid, "city": "Agadir"},
    ).json()


def _alerted(client, director, tx_id) -> bool:
    return any(
        a["transaction_id"] == tx_id
        for a in client.get("/alerts", headers=director).json()
    )


def test_default_threshold_comes_from_config(client, auth_headers):
    resp = client.get("/agency-settings/alert-threshold", headers=auth_headers("director"))
    assert resp.status_code == 200
    assert resp.json() == {"threshold": 70, "overridden": False}


def test_update_threshold_changes_alerting(client, auth_headers):
    """LA preuve fonctionnelle : le même scénario (score 80) alerte ou non
    selon la décision du directeur."""
    advisor, director = auth_headers("advisor"), auth_headers("director")

    # 1. Seuil par défaut (70) : score 80 -> alerte.
    tx = _tx_score_80(client, advisor, cin="ST111111")
    assert tx["risk_score"]["score"] == 80
    assert _alerted(client, director, tx["id"])

    # 2. Le directeur relève le seuil à 90 : le même scénario n'alerte PLUS.
    updated = client.patch(
        "/agency-settings/alert-threshold", headers=director, json={"threshold": 90}
    )
    assert updated.json() == {"threshold": 90, "overridden": True}
    tx2 = _tx_score_80(client, advisor, cin="ST222222")
    assert tx2["risk_score"]["score"] == 80
    assert not _alerted(client, director, tx2["id"])

    # 3. Seuil redescendu à 75 : l'alerte se déclenche de nouveau.
    client.patch("/agency-settings/alert-threshold", headers=director, json={"threshold": 75})
    tx3 = _tx_score_80(client, advisor, cin="ST333333")
    assert _alerted(client, director, tx3["id"])


def test_threshold_validation_and_rbac(client, auth_headers):
    director = auth_headers("director")
    # Bornes 1-100 (validées par Pydantic -> 422).
    assert client.patch(
        "/agency-settings/alert-threshold", headers=director, json={"threshold": 0}
    ).status_code == 422
    assert client.patch(
        "/agency-settings/alert-threshold", headers=director, json={"threshold": 101}
    ).status_code == 422
    # RBAC : réservé au directeur.
    assert client.get(
        "/agency-settings/alert-threshold", headers=auth_headers("advisor")
    ).status_code == 403


def test_threshold_change_is_audited(client, auth_headers):
    client.patch(
        "/agency-settings/alert-threshold", headers=auth_headers("director"),
        json={"threshold": 80},
    )
    logs = client.get(
        "/audit-logs", headers=auth_headers("admin"),
        params={"action": "alert_threshold_changed"},
    ).json()
    assert len(logs) == 1
    assert "70 -> 80" in logs[0]["details"]
