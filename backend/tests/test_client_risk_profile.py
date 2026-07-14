"""Tests du profil de risque client (calibrage du scoring par client).

Le point fonctionnel prouvé : le MÊME scénario suspect score PLUS BAS quand
le directeur a marqué le client « grande fortune » ou « voyageur fréquent »
— sans jamais toucher au modèle, et avec une trace d'audit obligatoire.
"""

from types import SimpleNamespace

from app.ml.features import TransactionFeatures, calibrate_for_client
from tests.test_clients_api import VALID_CLIENT


# ---------- 1. La calibration elle-même (unitaire) ----------
def _feat():
    return TransactionFeatures(
        amount_over_income=3.0, amount_over_avg=4.0, is_night=0, city_changed=1,
        tx_last_24h=6, cumul_72h_over_income=3.5, days_since_last_tx=2,
    )


def test_calibrate_frequent_traveler_neutralises_city():
    adj, notes = calibrate_for_client(_feat(), SimpleNamespace(frequent_traveler=True))
    assert adj.city_changed == 0
    assert any("voyageur" in n for n in notes)
    # les autres signaux sont intacts
    assert adj.amount_over_income == 3.0


def test_calibrate_high_net_worth_neutralises_income_ratios():
    adj, notes = calibrate_for_client(_feat(), SimpleNamespace(high_net_worth=True))
    assert adj.amount_over_income == 0.0 and adj.cumul_72h_over_income == 0.0
    assert any("fortune" in n for n in notes)
    assert adj.city_changed == 1  # non concerné


def test_calibrate_business_neutralises_burst():
    adj, notes = calibrate_for_client(_feat(), SimpleNamespace(business_account=True))
    assert adj.tx_last_24h == 0
    assert any("professionnel" in n for n in notes)


def test_calibrate_none_client_is_noop():
    adj, notes = calibrate_for_client(_feat(), None)
    assert notes == [] and adj.city_changed == 1


# ---------- 2. Bout en bout : le score baisse avec le profil ----------
def _suspicious_score(client, advisor, cin):
    cid = client.post(
        "/clients", headers=advisor, json={**VALID_CLIENT, "cin": cin, "monthly_income": "4000"}
    ).json()["id"]
    aid = client.post(
        "/accounts", headers=advisor, json={"client_id": cid, "initial_balance": "90000"}
    ).json()["id"]
    for _ in range(5):
        client.post("/transactions", headers=advisor,
                    json={"transaction_type": "deposit", "amount": "150",
                          "account_id": aid, "city": "Casablanca"})
    tx = client.post("/transactions", headers=advisor,
                     json={"transaction_type": "withdrawal", "amount": "8000",
                           "account_id": aid, "city": "Agadir"}).json()
    return cid, tx["risk_score"]


def test_high_net_worth_lowers_score(client, auth_headers):
    advisor, director = auth_headers("advisor"), auth_headers("director")

    # Client A : profil standard -> score de référence.
    _, rs_a = _suspicious_score(client, advisor, "HN111111")

    # Client B : marqué « grande fortune » AVANT l'opération.
    cid_b = client.post("/clients", headers=advisor,
                        json={**VALID_CLIENT, "cin": "HN222222", "monthly_income": "4000"}).json()["id"]
    r = client.patch(f"/clients/{cid_b}/risk-profile", headers=director,
                     json={"high_net_worth": True, "note": "Client fortuné, revenu déclaré non représentatif"})
    assert r.status_code == 200 and r.json()["high_net_worth"] is True
    aid_b = client.post("/accounts", headers=advisor,
                        json={"client_id": cid_b, "initial_balance": "90000"}).json()["id"]
    for _ in range(5):
        client.post("/transactions", headers=advisor,
                    json={"transaction_type": "deposit", "amount": "150", "account_id": aid_b, "city": "Casablanca"})
    tx_b = client.post("/transactions", headers=advisor,
                       json={"transaction_type": "withdrawal", "amount": "8000",
                             "account_id": aid_b, "city": "Agadir"}).json()
    rs_b = tx_b["risk_score"]

    # Même scénario, mais le score du client fortuné est PLUS BAS.
    assert rs_b["score"] < rs_a["score"]
    assert "grande fortune" in rs_b["explanation"]


# ---------- 3. Gouvernance : RBAC, motif obligatoire, audit ----------
def test_risk_profile_reserved_to_director(client, auth_headers):
    advisor = auth_headers("advisor")
    cid = client.post("/clients", headers=advisor,
                      json={**VALID_CLIENT, "cin": "HN333333"}).json()["id"]
    r = client.patch(f"/clients/{cid}/risk-profile", headers=advisor,
                     json={"frequent_traveler": True, "note": "test"})
    assert r.status_code == 403  # un conseiller ne peut PAS assouplir la détection


def test_risk_profile_requires_motif(client, auth_headers):
    advisor, director = auth_headers("advisor"), auth_headers("director")
    cid = client.post("/clients", headers=advisor,
                      json={**VALID_CLIENT, "cin": "HN444444"}).json()["id"]
    # motif vide -> 422 (la justification est obligatoire)
    r = client.patch(f"/clients/{cid}/risk-profile", headers=director,
                     json={"frequent_traveler": True, "note": ""})
    assert r.status_code == 422


def test_risk_profile_change_is_audited(client, auth_headers):
    advisor, director, admin = auth_headers("advisor"), auth_headers("director"), auth_headers("admin")
    cid = client.post("/clients", headers=advisor,
                      json={**VALID_CLIENT, "cin": "HN555555"}).json()["id"]
    client.patch(f"/clients/{cid}/risk-profile", headers=director,
                 json={"frequent_traveler": True, "note": "Voyage souvent pour affaires"})
    logs = client.get("/audit-logs", headers=admin,
                      params={"action": "client_risk_profile_changed"}).json()
    assert len(logs) == 1
    assert "voyageur fréquent" in logs[0]["details"] and "affaires" in logs[0]["details"]
