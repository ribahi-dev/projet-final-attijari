"""Tests du profil de risque client + workflow d'approbation (maker-checker).

Deux points prouvés :
  1. La calibration ne s'applique QUE si le profil est APPROUVÉ (« active ») —
     une demande « en attente » n'a aucun effet sur le score.
  2. Séparation des tâches : le conseiller PROPOSE, le directeur APPROUVE ;
     un conseiller ne peut jamais assouplir la détection seul. Tout est audité.
"""

from types import SimpleNamespace

from app.ml.features import TransactionFeatures, calibrate_for_client
from tests.test_clients_api import VALID_CLIENT


def _feat():
    return TransactionFeatures(
        amount_over_income=3.0, amount_over_avg=4.0, is_night=0, city_changed=1,
        tx_last_24h=6, cumul_72h_over_income=3.5, days_since_last_tx=2,
    )


def _client(status="active", **flags):
    base = dict(frequent_traveler=False, high_net_worth=False,
                business_account=False, risk_profile_status=status)
    base.update(flags)
    return SimpleNamespace(**base)


# ---------- 1. La calibration (unitaire) ----------
def test_calibrate_frequent_traveler_neutralises_city():
    adj, notes = calibrate_for_client(_feat(), _client(frequent_traveler=True))
    assert adj.city_changed == 0 and any("voyageur" in n for n in notes)
    assert adj.amount_over_income == 3.0  # les autres signaux intacts


def test_calibrate_high_net_worth_neutralises_income_ratios():
    adj, notes = calibrate_for_client(_feat(), _client(high_net_worth=True))
    assert adj.amount_over_income == 0.0 and adj.cumul_72h_over_income == 0.0
    assert any("fortune" in n for n in notes) and adj.city_changed == 1


def test_calibrate_business_neutralises_burst():
    adj, notes = calibrate_for_client(_feat(), _client(business_account=True))
    assert adj.tx_last_24h == 0 and any("professionnel" in n for n in notes)


def test_calibrate_pending_profile_has_no_effect():
    """Un profil EN ATTENTE (non approuvé) ne calibre RIEN."""
    adj, notes = calibrate_for_client(_feat(), _client(status="pending", high_net_worth=True))
    assert notes == [] and adj.amount_over_income == 3.0


def test_calibrate_none_client_is_noop():
    adj, notes = calibrate_for_client(_feat(), None)
    assert notes == [] and adj.city_changed == 1


# ---------- 2. Bout en bout : le score baisse après APPROBATION ----------
def _scenario_score(client, advisor, cid):
    aid = client.post("/accounts", headers=advisor,
                      json={"client_id": cid, "initial_balance": "90000"}).json()["id"]
    for _ in range(5):
        client.post("/transactions", headers=advisor,
                    json={"transaction_type": "deposit", "amount": "150", "account_id": aid, "city": "Casablanca"})
    tx = client.post("/transactions", headers=advisor,
                     json={"transaction_type": "withdrawal", "amount": "8000",
                           "account_id": aid, "city": "Agadir"}).json()
    return tx["risk_score"]["score"]


def test_workflow_request_pending_then_approve(client, auth_headers):
    advisor, director = auth_headers("advisor"), auth_headers("director")
    cid = client.post("/clients", headers=advisor,
                      json={**VALID_CLIENT, "cin": "WF111111", "monthly_income": "4000"}).json()["id"]

    # 1. Le conseiller PROPOSE « grande fortune » -> en attente.
    r = client.post(f"/clients/{cid}/risk-profile/request", headers=advisor,
                    json={"high_net_worth": True, "note": "Client fortuné"})
    assert r.status_code == 200 and r.json()["risk_profile_status"] == "pending"

    # 2. Tant que c'est « en attente », le score n'est PAS calibré (= standard).
    score_pending = _scenario_score(client, advisor, cid)

    # 3. Le directeur APPROUVE -> profil actif.
    a = client.post(f"/clients/{cid}/risk-profile/approve", headers=director)
    assert a.status_code == 200 and a.json()["risk_profile_status"] == "active"

    # 4. Le même scénario score maintenant PLUS BAS.
    cid2 = client.post("/clients", headers=advisor,
                       json={**VALID_CLIENT, "cin": "WF111112", "monthly_income": "4000"}).json()["id"]
    client.post(f"/clients/{cid2}/risk-profile/request", headers=advisor,
                json={"high_net_worth": True, "note": "Client fortuné"})
    client.post(f"/clients/{cid2}/risk-profile/approve", headers=director)
    score_active = _scenario_score(client, advisor, cid2)

    assert score_active < score_pending


# ---------- 3. Gouvernance : séparation des tâches ----------
def test_advisor_cannot_approve(client, auth_headers):
    advisor = auth_headers("advisor")
    cid = client.post("/clients", headers=advisor,
                      json={**VALID_CLIENT, "cin": "WF222222"}).json()["id"]
    client.post(f"/clients/{cid}/risk-profile/request", headers=advisor,
                json={"frequent_traveler": True, "note": "Voyage beaucoup"})
    # Un conseiller ne peut PAS approuver sa propre demande.
    assert client.post(f"/clients/{cid}/risk-profile/approve", headers=advisor).status_code == 403


def test_approve_requires_pending_request(client, auth_headers):
    advisor, director = auth_headers("advisor"), auth_headers("director")
    cid = client.post("/clients", headers=advisor,
                      json={**VALID_CLIENT, "cin": "WF333333"}).json()["id"]
    # Aucune demande -> 409.
    assert client.post(f"/clients/{cid}/risk-profile/approve", headers=director).status_code == 409


def test_reject_clears_request(client, auth_headers):
    advisor, director = auth_headers("advisor"), auth_headers("director")
    cid = client.post("/clients", headers=advisor,
                      json={**VALID_CLIENT, "cin": "WF444444"}).json()["id"]
    client.post(f"/clients/{cid}/risk-profile/request", headers=advisor,
                json={"high_net_worth": True, "note": "test"})
    r = client.post(f"/clients/{cid}/risk-profile/reject", headers=director)
    assert r.status_code == 200
    body = r.json()
    assert body["risk_profile_status"] == "none" and body["high_net_worth"] is False


def test_pending_requests_list_director_only(client, auth_headers):
    advisor, director = auth_headers("advisor"), auth_headers("director")
    cid = client.post("/clients", headers=advisor,
                      json={**VALID_CLIENT, "cin": "WF555555"}).json()["id"]
    client.post(f"/clients/{cid}/risk-profile/request", headers=advisor,
                json={"business_account": True, "note": "Entreprise"})
    listing = client.get("/clients/risk-requests", headers=director).json()
    assert any(c["id"] == cid for c in listing)
    assert client.get("/clients/risk-requests", headers=advisor).status_code == 403


def test_workflow_is_audited(client, auth_headers):
    advisor, director, admin = auth_headers("advisor"), auth_headers("director"), auth_headers("admin")
    cid = client.post("/clients", headers=advisor,
                      json={**VALID_CLIENT, "cin": "WF666666"}).json()["id"]
    client.post(f"/clients/{cid}/risk-profile/request", headers=advisor,
                json={"frequent_traveler": True, "note": "Déplacements pro"})
    client.post(f"/clients/{cid}/risk-profile/approve", headers=director)
    actions = {log["action"] for log in client.get("/audit-logs", headers=admin).json()}
    assert "risk_profile_requested" in actions and "risk_profile_approved" in actions


# ---------- 4. Le directeur peut fixer DIRECTEMENT (il est l'approbateur) ----------
def test_director_direct_set_is_active(client, auth_headers):
    advisor, director = auth_headers("advisor"), auth_headers("director")
    cid = client.post("/clients", headers=advisor,
                      json={**VALID_CLIENT, "cin": "WF777777"}).json()["id"]
    r = client.patch(f"/clients/{cid}/risk-profile", headers=director,
                     json={"high_net_worth": True, "note": "Décision directe"})
    assert r.status_code == 200 and r.json()["risk_profile_status"] == "active"
    # Un conseiller ne peut pas fixer directement.
    assert client.patch(f"/clients/{cid}/risk-profile", headers=advisor,
                        json={"frequent_traveler": True, "note": "x"}).status_code == 403
    # Motif obligatoire.
    assert client.patch(f"/clients/{cid}/risk-profile", headers=director,
                        json={"high_net_worth": True, "note": ""}).status_code == 422
