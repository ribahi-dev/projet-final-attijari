"""Tests du dossier de déclaration de soupçon (PDF LBC-FT).

Règle métier testée : le PDF n'est délivré QUE pour une alerte
transactionnelle qualifiée en fraude confirmée par le directeur — c'est
la décision humaine qui déclenche l'obligation de déclarer, pas le score.
"""

from tests.test_alerts_analytics_api import _create_suspicious_alert


def _qualified_alert_id(client, advisor, director, resolution="confirmed_fraud"):
    """Scénario complet : transaction suspecte -> alerte -> qualification."""
    _create_suspicious_alert(client, advisor)
    alert = client.get("/alerts", headers=director).json()[0]
    client.patch(f"/alerts/{alert['id']}", headers=director, json={"status": "in_progress"})
    client.patch(
        f"/alerts/{alert['id']}", headers=director,
        json={"status": "closed", "resolution": resolution},
    )
    return alert["id"]


def test_suspicion_report_pdf_downloads(client, auth_headers):
    advisor, director = auth_headers("advisor"), auth_headers("director")
    alert_id = _qualified_alert_id(client, advisor, director)

    resp = client.get(f"/alerts/{alert_id}/declaration-soupcon.pdf", headers=director)

    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:4] == b"%PDF"      # signature d'un vrai fichier PDF
    assert len(resp.content) > 1500         # dossier complet, pas une page vide
    assert "declaration_soupcon" in resp.headers["content-disposition"]


def test_suspicion_report_refused_if_not_qualified(client, auth_headers):
    """Alerte encore ouverte (non qualifiée) -> 409, pas de dossier."""
    advisor, director = auth_headers("advisor"), auth_headers("director")
    _create_suspicious_alert(client, advisor)
    alert = client.get("/alerts", headers=director).json()[0]

    resp = client.get(f"/alerts/{alert['id']}/declaration-soupcon.pdf", headers=director)
    assert resp.status_code == 409


def test_suspicion_report_refused_for_false_positive(client, auth_headers):
    """Un faux positif ne se déclare pas : 409 également."""
    advisor, director = auth_headers("advisor"), auth_headers("director")
    alert_id = _qualified_alert_id(client, advisor, director, resolution="false_positive")

    resp = client.get(f"/alerts/{alert_id}/declaration-soupcon.pdf", headers=director)
    assert resp.status_code == 409


def test_suspicion_report_404_unknown_alert(client, auth_headers):
    resp = client.get("/alerts/99999/declaration-soupcon.pdf", headers=auth_headers("director"))
    assert resp.status_code == 404


def test_suspicion_report_forbidden_for_advisor(client, auth_headers):
    """RBAC : le dossier réglementaire est réservé au directeur."""
    resp = client.get("/alerts/1/declaration-soupcon.pdf", headers=auth_headers("advisor"))
    assert resp.status_code == 403


def test_suspicion_report_generation_is_audited(client, auth_headers):
    """L'édition d'un dossier réglementaire laisse une trace d'audit."""
    advisor, director = auth_headers("advisor"), auth_headers("director")
    alert_id = _qualified_alert_id(client, advisor, director)
    client.get(f"/alerts/{alert_id}/declaration-soupcon.pdf", headers=director)

    logs = client.get(
        "/audit-logs", headers=auth_headers("admin"),
        params={"action": "suspicion_report_generated"},
    ).json()
    assert len(logs) == 1
    assert logs[0]["entity_type"] == "alert"
    assert logs[0]["entity_id"] == alert_id
