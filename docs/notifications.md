# 🔔 Notifications (Telegram & Email)

NovaBank prévient le **directeur d'agence** en temps réel lors d'un événement
sensible :

- une **transaction à risque** détectée par l'IA (score ≥ seuil) ;
- un **verrouillage de compte** après des échecs de connexion répétés.

## Principe

Le système est **robuste par conception** (`app/services/notification_service.py`) :

- **non bloquant** — l'envoi part dans un thread d'arrière-plan, l'API répond
  instantanément ;
- **jamais fatal** — une notification qui échoue ne casse jamais l'opération ;
- **dégradation propre** — sans configuration, la notification est simplement
  **journalisée** (visible dans `docker logs`). La démo fonctionne sans rien
  configurer.

## Activer Telegram (recommandé pour la démo)

Telegram est gratuit, instantané, et parfait pour une démonstration en direct.

1. Sur Telegram, ouvrir une conversation avec **@BotFather**, envoyer `/newbot`,
   suivre les instructions → on obtient un **TOKEN** (ex. `123456:ABC-DEF...`).
2. Ouvrir une conversation avec le nouveau bot et lui envoyer un message (`/start`).
3. Écrire à **@userinfobot** pour obtenir son **CHAT ID** (un nombre).
4. Renseigner ces valeurs :
   - soit dans le fichier **`.env` racine** (pour Docker) :
     ```
     TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
     TELEGRAM_CHAT_ID=votre_chat_id
     ```
   - soit **par directeur**, via l'interface Admin → Utilisateurs : chaque
     directeur peut avoir son propre `telegram_chat_id`.
5. Relancer la plateforme. À la prochaine transaction à risque, une notification
   Telegram arrive **en direct**. 🎉

## Activer l'email (SMTP)

Renseigner dans le `.env` (exemple Gmail — utiliser un **mot de passe
d'application**, pas le mot de passe du compte) :

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre.adresse@gmail.com
SMTP_PASSWORD=mot_de_passe_application
SMTP_FROM=votre.adresse@gmail.com
```

Le directeur est alors notifié à l'adresse **email de son compte**.

## Vérifier sans rien configurer

Même sans Telegram ni SMTP, on peut voir les notifications dans les logs :

```bash
docker compose logs -f api | grep NOTIFICATION
```

Chaque événement sensible y apparaît — preuve que le déclenchement fonctionne.

## Pour la soutenance

Configurer Telegram **la veille** (5 minutes). Le jour J, saisir une transaction
suspecte devant le jury et montrer la notification qui arrive sur le téléphone :
c'est un moment fort et concret.
