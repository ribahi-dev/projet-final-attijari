"""Tests des notifications : canaux, dégradation propre, non-fatalité, déclenchement.

On teste `_deliver` (synchrone) plutôt que `notify` (qui lance un thread),
et on patche `notify` / `notify_directors` pour vérifier le câblage sans
envoyer de vrais messages.
"""

import json as _json

from app.services import notification_service as notif
from tests.conftest import TEST_PASSWORD
from tests.test_clients_api import VALID_CLIENT


def _login(client, user):
    login = client.post("/auth/login", data={"username": user.email, "password": TEST_PASSWORD}).json()
    return {"Authorization": f"Bearer {login['access_token']}"}


def test_deliver_never_raises_without_channels(monkeypatch):
    """Sans canal configuré, la notification est journalisée sans erreur."""
    monkeypatch.setattr(notif.settings, "telegram_bot_token", "")
    monkeypatch.setattr(notif.settings, "telegram_chat_id", "")
    monkeypatch.setattr(notif.settings, "smtp_host", "")
    notif._deliver("Sujet", "Message", email_to="dir@novabank.ma", telegram_chat_id=None)


def test_deliver_sends_telegram_when_configured(monkeypatch):
    sent = {}
    monkeypatch.setattr(notif.settings, "telegram_bot_token", "TOKEN")
    monkeypatch.setattr(notif.settings, "telegram_chat_id", "999")  # défaut agence
    monkeypatch.setattr(notif, "_post_telegram", lambda chat, text: sent.update(chat=chat, text=text))

    notif._deliver("Alerte", "Corps du message", email_to=None, telegram_chat_id="123")

    assert sent["chat"] == "123"  # le chat explicite prime sur le défaut agence
    assert "Alerte" in sent["text"] and "Corps du message" in sent["text"]


def test_telegram_uses_agency_default_chat(monkeypatch):
    sent = {}
    monkeypatch.setattr(notif.settings, "telegram_bot_token", "TOKEN")
    monkeypatch.setattr(notif.settings, "telegram_chat_id", "555")
    monkeypatch.setattr(notif, "_post_telegram", lambda chat, text: sent.update(chat=chat))

    notif._deliver("S", "M", email_to=None, telegram_chat_id=None)  # pas de chat perso

    assert sent["chat"] == "555"  # repli sur le canal agence par défaut


def test_channel_failure_is_never_fatal(monkeypatch):
    monkeypatch.setattr(notif.settings, "telegram_bot_token", "TOKEN")
    monkeypatch.setattr(notif.settings, "telegram_chat_id", "999")

    def boom(chat, text):
        raise RuntimeError("réseau coupé")

    monkeypatch.setattr(notif, "_post_telegram", boom)
    # Ne doit PAS lever : une notif ratée ne casse jamais l'opération bancaire.
    notif._deliver("X", "Y", email_to=None, telegram_chat_id=None)


def test_notify_directors_targets_only_active_directors(db, make_user, monkeypatch):
    make_user("director", email="dir1@novabank.ma")
    make_user("director", email="dir2@novabank.ma")
    make_user("advisor", email="adv@novabank.ma")
    make_user("director", email="inactif@novabank.ma", is_active=False)

    reached = []
    monkeypatch.setattr(notif, "notify", lambda s, m, **kw: reached.append(kw.get("email_to")))
    notif.notify_directors(db, "Sujet", "Message")

    assert set(reached) == {"dir1@novabank.ma", "dir2@novabank.ma"}  # ni conseiller ni inactif


def test_suspicious_transaction_triggers_notification(client, auth_headers, monkeypatch):
    captured = {}
    monkeypatch.setattr(
        notif, "notify_directors",
        lambda db, subject, message: captured.update(subject=subject, message=message),
    )
    headers = auth_headers("advisor")
    cid = client.post(
        "/clients", headers=headers, json={**VALID_CLIENT, "monthly_income": "4000"}
    ).json()["id"]
    aid = client.post(
        "/accounts", headers=headers, json={"client_id": cid, "initial_balance": "0"}
    ).json()["id"]

    # Historique : 5 petits dépôts à Casablanca (fréquence + ville de référence).
    for _ in range(5):
        client.post(
            "/transactions", headers=headers,
            json={"transaction_type": "deposit", "amount": "150",
                  "account_id": aid, "city": "Casablanca"},
        )

    # Dépôt énorme + ville inhabituelle -> score élevé -> alerte -> notification.
    resp = client.post(
        "/transactions", headers=headers,
        json={"transaction_type": "deposit", "amount": "80000", "account_id": aid, "city": "Oujda"},
    )
    assert resp.status_code == 201
    assert resp.json()["risk_score"]["score"] >= 70
    assert "fraude" in captured.get("subject", "").lower()  # le directeur a été notifié
    assert "Client" in captured.get("message", "")  # message enrichi (nom du client)


def test_fetch_latest_telegram_chat_takes_most_recent(monkeypatch):
    monkeypatch.setattr(notif.settings, "telegram_bot_token", "TOKEN")
    payload = {
        "ok": True,
        "result": [
            {"update_id": 1, "message": {"chat": {"id": 111, "first_name": "Ancien"}}},
            {"update_id": 2, "message": {"chat": {"id": 222, "first_name": "Récent"}}},
        ],
    }

    class FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return _json.dumps(payload).encode()

    monkeypatch.setattr(notif.urllib.request, "urlopen", lambda *a, **k: FakeResp())
    info = notif.fetch_latest_telegram_chat()
    assert info == {"chat_id": "222", "name": "Récent"}  # le message le plus récent


def test_link_telegram_captures_and_persists(client, make_user, monkeypatch):
    monkeypatch.setattr(notif.settings, "telegram_bot_token", "TOKEN")
    monkeypatch.setattr(notif, "fetch_latest_telegram_chat", lambda: {"chat_id": "42", "name": "Mehdi"})
    user = make_user("director", email="link@novabank.ma")
    headers = _login(client, user)

    resp = client.post("/notifications/telegram/link-me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["telegram_chat_id"] == "42"
    # Persisté : /auth/me renvoie le chat_id enregistré.
    assert client.get("/auth/me", headers=headers).json()["telegram_chat_id"] == "42"


def test_link_telegram_404_when_no_message(client, make_user, monkeypatch):
    monkeypatch.setattr(notif.settings, "telegram_bot_token", "TOKEN")
    monkeypatch.setattr(notif, "fetch_latest_telegram_chat", lambda: None)
    headers = _login(client, make_user("director", email="nolink@novabank.ma"))

    resp = client.post("/notifications/telegram/link-me", headers=headers)
    assert resp.status_code == 404


def test_send_test_notification(client, make_user, monkeypatch):
    monkeypatch.setattr(notif.settings, "telegram_bot_token", "TOKEN")
    monkeypatch.setattr(notif.settings, "telegram_chat_id", "999")
    sent = {}
    monkeypatch.setattr(notif, "notify", lambda s, m, **kw: sent.update(subject=s))
    headers = _login(client, make_user("director", email="test-notif@novabank.ma"))

    resp = client.post("/notifications/test", headers=headers)
    assert resp.status_code == 200
    assert "Test" in sent["subject"]
