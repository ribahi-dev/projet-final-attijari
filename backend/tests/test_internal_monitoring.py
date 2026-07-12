"""Tests de la surveillance de fraude interne (comportement des conseillers).

Les indicateurs viennent des transactions et du journal d'audit ; les
drapeaux sont des raisons LISIBLES, comme pour le scoring client.
"""

from datetime import datetime, timezone

from sqlalchemy import update

from app.models import Transaction
from tests.test_clients_api import VALID_CLIENT


def _seed_activity(client, advisor, cin, n_deposits=3, withdrawals=("40000", "35000")):
    """Un conseiller saisit n dépôts + des retraits suspects sur UN compte."""
    cid = client.post(
        "/clients", headers=advisor,
        json={**VALID_CLIENT, "cin": cin, "monthly_income": "4000"},
    ).json()["id"]
    aid = client.post(
        "/accounts", headers=advisor, json={"client_id": cid, "initial_balance": "90000"}
    ).json()["id"]
    for _ in range(n_deposits):
        client.post(
            "/transactions", headers=advisor,
            json={"transaction_type": "deposit", "amount": "150",
                  "account_id": aid, "city": "Casablanca"},
        )
    for amount, city in zip(withdrawals, ("Agadir", "Tanger")):
        client.post(
            "/transactions", headers=advisor,
            json={"transaction_type": "withdrawal", "amount": amount,
                  "account_id": aid, "city": city},
        )


def test_internal_monitoring_counts_and_risk_flag(client, auth_headers):
    """3 dépôts + 2 retraits à haut risque -> 2/5 = 40 % d'opérations
    risquées : le drapeau 'part élevée' se lève."""
    advisor, director = auth_headers("advisor"), auth_headers("director")
    _seed_activity(client, advisor, cin="IM111111")

    resp = client.get("/analytics/internal-monitoring", headers=director)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["advisors"]) == 1

    row = data["advisors"][0]
    assert row["tx_count"] == 5
    assert row["high_risk_count"] == 2
    assert row["max_ops_same_account"] == 5   # tout sur le même compte
    assert any("haut risque" in f for f in row["flags"])
    assert row["is_anomalous"] is True


def test_internal_monitoring_night_flag(client, auth_headers, db):
    """3 opérations forcées à 02h00 UTC (2-3h à Casablanca) -> drapeau nuit."""
    advisor, director = auth_headers("advisor"), auth_headers("director")
    _seed_activity(client, advisor, cin="IM222222", n_deposits=3, withdrawals=())

    night = datetime.now(timezone.utc).replace(hour=2, minute=0, second=0)
    db.execute(update(Transaction).values(created_at=night))

    row = client.get("/analytics/internal-monitoring", headers=director).json()["advisors"][0]
    assert row["night_count"] == 3
    assert any("nuit" in f for f in row["flags"])


def test_internal_monitoring_concentration_flag(client, auth_headers):
    """12 opérations sur le même compte -> concentration signalée."""
    advisor, director = auth_headers("advisor"), auth_headers("director")
    _seed_activity(client, advisor, cin="IM333333", n_deposits=12, withdrawals=())

    row = client.get("/analytics/internal-monitoring", headers=director).json()["advisors"][0]
    assert row["max_ops_same_account"] == 12
    assert any("même compte" in f for f in row["flags"])


def test_internal_monitoring_clean_advisor_has_no_flags(client, auth_headers):
    """Une activité banale (2 dépôts) ne lève AUCUN drapeau — pas de
    suspicion généralisée."""
    advisor, director = auth_headers("advisor"), auth_headers("director")
    _seed_activity(client, advisor, cin="IM444444", n_deposits=2, withdrawals=())

    row = client.get("/analytics/internal-monitoring", headers=director).json()["advisors"][0]
    assert row["tx_count"] == 2
    assert row["flags"] == []
    assert row["is_anomalous"] is False


def test_internal_monitoring_requires_director(client, auth_headers):
    assert client.get(
        "/analytics/internal-monitoring", headers=auth_headers("advisor")
    ).status_code == 403
