# 📘 Guide complet du projet NovaBank (version PFE)

> **But de ce document** : te faire comprendre **chaque fichier**, son rôle et son
> pourquoi, pour que tu maîtrises le projet de A à Z et répondes à **n'importe quelle
> question du jury**. Lis-le dans l'ordre une première fois, puis utilise-le comme
> référence. Pour **reconstruire** le projet toi-même étape par étape, suis
> [GUIDE_CONSTRUCTION.md](GUIDE_CONSTRUCTION.md) en parallèle.

## Sommaire
1. [Vision d'ensemble en 1 minute](#1-vision-densemble)
2. [Les 3 couches et le flux d'une requête](#2-les-3-couches)
3. [Arborescence commentée](#3-arborescence)
4. [Le BACKEND fichier par fichier](#4-backend)
5. [Le module IA en détail (ML, SHAP, feedback)](#5-ia)
6. [Les 4 améliorations métier v2.1 (pourquoi + comment)](#6-ameliorations)
7. [Le FRONTEND fichier par fichier](#7-frontend)
8. [L'INFRASTRUCTURE (Docker, CI, Alembic)](#8-infrastructure)
9. [Les 18 concepts clés à maîtriser](#9-concepts)
10. [Glossaire](#10-glossaire)
11. [Questions du jury + réponses](#11-jury)

---

<a name="1-vision-densemble"></a>
## 1. Vision d'ensemble en 1 minute

NovaBank est une **application web d'aide à la décision** pour une agence bancaire. Un
**conseiller** saisit des opérations (dépôt, retrait, virement). À chaque opération, un
**moteur d'IA** (Random Forest) calcule un risque de 0 à 100 **avec une explication
lisible et un graphique SHAP**. Si le risque dépasse le seuil, une **alerte** est créée
et le **directeur** est **notifié sur Telegram**. Il traite l'alerte et la **qualifie**
(fraude confirmée / faux positif) — et cette décision **réentraîne le modèle** (boucle
de feedback). Pour une fraude confirmée, un clic génère le **dossier de déclaration de
soupçon** (PDF réglementaire LBC-FT). Une page **Santé du modèle** surveille la
performance réelle du moteur en production. Tout est **sécurisé** (JWT, rôles, audit)
et **conteneurisé** (Docker, 1 commande).

Le récit en une phrase : **détecter mieux → déclarer plus vite → rester fiable dans le
temps.**

Le projet a **3 grandes parties** :
- **`frontend/`** — ce que l'utilisateur voit (React + TypeScript).
- **`backend/`** — le cerveau : l'API qui reçoit les requêtes, applique la logique,
  score les opérations, parle à la base (FastAPI + Python + scikit-learn).
- **`docker-compose.yml` + Dockerfiles** — l'emballage qui fait tourner le tout d'un coup.

---

<a name="2-les-3-couches"></a>
## 2. Les 3 couches et le flux d'une requête

### Le schéma mental le plus important

```
  UTILISATEUR (navigateur)
        │  clique "valider un retrait"
        ▼
┌─────────────────────┐
│  FRONTEND (React)   │   construit une requête HTTP + jeton JWT
└─────────────────────┘
        │  POST /transactions  { montant, compte... }
        ▼
┌──────────────────────────────────────────────────────┐
│  BACKEND (FastAPI)                                    │
│                                                       │
│  1. ROUTER      reçoit la requête HTTP                │
│  2. SCHÉMA      valide les données (Pydantic)         │
│  3. DÉPENDANCE  vérifie le jeton + le rôle (RBAC)     │
│  4. SERVICE     applique la logique métier :          │
│                 verrou du compte, SCORING IA (7       │
│                 features → RandomForest → SHAP),      │
│                 alerte si score ≥ 70, notification    │
│                 Telegram, journal d'audit             │
│  5. MODÈLE      traduit en SQL (SQLAlchemy)           │
└──────────────────────────────────────────────────────┘
        │  INSERT / UPDATE
        ▼
┌─────────────────────┐
│  BASE (PostgreSQL)  │   stocke durablement (y compris le score
└─────────────────────┘    ET ses valeurs SHAP → traçabilité)
```

### La règle de dépendance (à connaître par cœur)

> **`router → service → modèle`**. Une route ne parle **jamais** directement à la base ;
> un service ne connaît **jamais** le protocole HTTP.

**Pourquoi ?** Parce que ça sépare les responsabilités : on peut tester la logique métier
sans lancer de serveur web, changer la base sans réécrire les routes, et réutiliser un
service ailleurs. C'est le principe qui rend un code **professionnel et maintenable**.

---

<a name="3-arborescence"></a>
## 3. Arborescence commentée

```
NovaBank/
├── docker-compose.yml      Orchestre les 3 services (base + api + frontend)
├── demarrer.bat / .sh      Lancement en 1 clic (Windows / Mac-Linux)
├── arreter.bat             Arrêt de la plateforme
├── .gitattributes          Force les bonnes fins de ligne (CRLF pour .bat)
├── .gitignore              Fichiers que git doit ignorer (.env, venv, artefacts…)
├── README.md               Vitrine du projet (démarrage, comptes de démo)
│
├── .github/workflows/
│   └── ci.yml              Intégration continue : lint + 70 tests à chaque push
│
├── docs/                   Documentation
│   ├── GUIDE_COMPLET.md    (ce fichier — comprendre chaque fichier)
│   ├── GUIDE_CONSTRUCTION.md  Reconstruire le projet de zéro, étape par étape
│   ├── evaluation_ml.md    Méthodologie et résultats du Machine Learning
│   ├── notifications.md    Le système Telegram/email expliqué
│   ├── plan_directeur.md   Vision et étapes du projet
│   ├── base_de_donnees.md  Explication du modèle de données
│   └── schema_cible.sql    Architecture BDD "grande échelle" (perspective)
│
├── backend/                L'API (le cerveau)
│   ├── app/
│   │   ├── main.py         Point d'entrée : assemble l'application FastAPI
│   │   ├── core/           Config, sécurité (JWT/bcrypt), dépendances (RBAC)
│   │   ├── db/             Connexion à la base (Engine, Session, Base)
│   │   ├── models/         Les 7 tables (classes SQLAlchemy)
│   │   ├── schemas/        Contrats d'entrée/sortie de l'API (Pydantic)
│   │   ├── services/       La logique métier (7 services)
│   │   ├── routers/        Les points d'entrée HTTP (10 routers)
│   │   └── ml/             Le module IA : extraction des features + modèle + SHAP
│   ├── ml_artifacts/       Le modèle entraîné (model.joblib) + ses métriques
│   ├── alembic/            Les migrations versionnées du schéma
│   ├── scripts/            create_tables, seed, train_model, docker_entrypoint
│   ├── tests/              70 tests automatisés (10 fichiers)
│   ├── requirements.txt    Dépendances Python (versions figées)
│   ├── pytest.ini          Configuration des tests
│   └── Dockerfile          Recette de l'image (ENTRAÎNE LE MODÈLE au build ⭐)
│
└── frontend/               L'interface (ce que l'on voit)
    ├── index.html          Page HTML de base
    ├── src/
    │   ├── main.tsx        Point d'entrée : monte l'application React
    │   ├── App.tsx         Le routage (quelle page pour quelle URL + gardes de rôle)
    │   ├── api/            Communication avec le backend (axios + types)
    │   ├── contexts/       États globaux (utilisateur, thème, notifications)
    │   ├── components/     Composants réutilisables (ui / layout / métier)
    │   ├── pages/          Les 14 écrans (Login, Dashboard, Fraud, SanteModele…)
    │   ├── lib/            Fonctions utilitaires (formats MAD, dates)
    │   └── styles/         Le design (couleurs orange, thème clair/sombre)
    ├── package.json        Dépendances JavaScript
    ├── vite.config.ts      Outil de build (+ proxy /api en dev)
    ├── nginx.conf          Serveur web de production (sert l'app + relaie /api)
    └── Dockerfile          Construit puis sert l'app (image ~50 Mo)
```

---

<a name="4-backend"></a>
## 4. Le BACKEND fichier par fichier

> 💡 **Astuce** : chaque fichier du code contient déjà un **en-tête de commentaires** qui
> explique son rôle. Ce guide en donne la synthèse. Ouvre les fichiers en parallèle.

### 4.1 — Point d'entrée & configuration (`app/main.py`, `app/core/`)

| Fichier | Rôle | Point clé pour le jury |
|---|---|---|
| **`app/main.py`** | Crée l'application FastAPI, **branche** les 10 routers + le CORS + le logging. Aucune logique métier. | « Un `main.py` qui grossit est le signe d'une mauvaise architecture. Le nôtre ne fait qu'assembler. » |
| **`app/core/config.py`** | Charge la configuration depuis `.env` (base, clé JWT, **seuil d'alerte**, jeton Telegram, SMTP) et la **valide au démarrage**. | « Code et configuration séparés (*12-factor*). Une variable manquante fait échouer le démarrage **tout de suite**, pas en pleine démo. » |
| **`app/core/security.py`** | Hachage **bcrypt** des mots de passe, **création/vérification des JWT** (access + refresh, le type est vérifié). | « On rejette l'algorithme `none` — attaque JWT classique. Un refresh token ne peut pas servir d'access token. » |
| **`app/core/deps.py`** | Les **dépendances** : `get_current_user` (qui est connecté ?) et `require_role` (a-t-il le droit ?). | « C'est ici que vit le **RBAC**. 401 = "je ne sais pas qui tu es" ; 403 = "je sais, mais tu n'as pas le droit". » |

### 4.2 — Base de données (`app/db/`)

| Fichier | Rôle | Point clé |
|---|---|---|
| **`app/db/base.py`** | Définit `Base`, la classe mère de tous les modèles. | Toute table hérite de `Base` pour être "reconnue" par SQLAlchemy. |
| **`app/db/session.py`** | Crée l'**Engine** (moteur + pool de connexions) et la **Session**. Fournit `get_db()`. | « Chaque requête HTTP obtient **sa propre** session, fermée à la fin quoi qu'il arrive — sinon fuite de connexions. » |

### 4.3 — Les modèles = les tables (`app/models/`)

Chaque fichier = une table. Un modèle décrit les colonnes en Python ; SQLAlchemy génère
le SQL. **Les modèles sont la source de vérité du schéma** (pas de init.sql), et Alembic
versionne les évolutions.

| Fichier | Table | Contenu |
|---|---|---|
| **`user.py`** | `users` | Employés de la plateforme : email, mot de passe **haché**, rôle, compteur d'échecs, **téléphone + telegram_chat_id** (pour les notifications). |
| **`client.py`** | `clients` | Clients bancaires : nom, CIN, profession, **revenu mensuel** (sert au scoring). |
| **`account.py`** | `accounts` | Comptes : numéro généré, type, **solde `Numeric`**, statut, lien client. |
| **`transaction.py`** | `transactions` | Opérations : type, montant, ville, compte source/destinataire, auteur. |
| **`risk_score.py`** | `risk_scores` | Verdict du scoring : score 0-100, confiance, **explication**, **`model_version`** (traçabilité MLOps) et **`shap_values`** (JSON des contributions). |
| **`alert.py`** | `alerts` | Alertes : type, niveau, statut, **`resolution`** (confirmed_fraud / false_positive — l'étiquette de la boucle de feedback ⭐). |
| **`audit_log.py`** | `audit_logs` | Journal : qui a fait quoi, quand, depuis quelle IP (append-only). |

> **Points clés à retenir :**
> - **`User` vs `Client`** : `User` = qui se **connecte** ; `Client` = qui possède des
>   **comptes**. Les confondre est l'erreur n°1.
> - **Montants en `Numeric` (décimal exact), jamais `float`** : un float ne représente
>   pas 0,10 exactement — inacceptable en banque.
> - **Horodatage par PostgreSQL** (`server_default=func.now()`) : une seule horloge de
>   référence.
> - **`model_version` sur chaque score** : on sait toujours QUEL moteur a produit QUELLE
>   décision — exigence d'auditabilité d'un système IA bancaire.

### 4.4 — Les schémas Pydantic (`app/schemas/`)

Les schémas définissent ce que l'API **accepte** et **renvoie**.

| Fichier | Contenu |
|---|---|
| **`client.py`**, **`account.py`**, **`transaction.py`**, **`user.py`** | Pour chaque entité : `...Create`, `...Update`, `...Response`. |
| **`alert.py`** | `AlertUpdate` (statut + **resolution**), `AlertResponse` (embarque la transaction et son score). |
| **`auth.py`** | Le format des jetons renvoyés à la connexion. |
| **`analytics.py`** | KPI, tendances, distribution + **`ModelHealthResponse`** (santé du modèle). |

> **LA question de jury : « pourquoi ne pas renvoyer directement les objets de la base ? »**
> 1. **Sécurité** : le modèle `User` contient `password_hash` — le schéma de sortie
>    garantit qu'il ne sort **jamais** (parade au *mass assignment* aussi en entrée).
> 2. **Découplage** : renommer une colonne ne casse pas le frontend.
> 3. **Validation** : Pydantic rejette une donnée invalide **avant** la logique (422).

### 4.5 — Les services = la logique métier (`app/services/`)

C'est le cœur intelligent. Aucun code HTTP ici.

| Fichier | Rôle | Point clé ⭐ |
|---|---|---|
| **`transaction_service.py`** | Dépôt/retrait/virement : vérifie le solde, **verrouille les comptes** (`SELECT ... FOR UPDATE`, ordre d'id croissant anti-deadlock), déclenche scoring + alerte + notification + audit, **atomiquement**. | « Deux virements simultanés s'exécutent **en série** : jamais de solde corrompu. C'est le A et le I de ACID. » |
| **`scoring_service.py`** | **Double moteur derrière une interface unique** : RandomForest si l'artefact existe (`ml-rf-v2.1`), sinon règles pondérées (`mvp-rules-v1`). | « L'application n'est **jamais** en panne de scoring, et chaque score garde la trace de son moteur. » |
| **`auth_service.py`** | Connexion : vérifie le mot de passe, **verrouille après 5 échecs**, journalise. | « Message d'erreur **identique** pour "email inconnu" et "mauvais mot de passe" — sinon on révèle quels emails existent. » |
| **`audit_service.py`** | Enregistre chaque action sensible (append-only). | « Un journal d'audit ne se modifie jamais. » |
| **`notification_service.py`** | Envoie Telegram + email sur événement sensible (transaction à risque, compte verrouillé). | « **Non bloquant** (thread), **jamais fatal** (erreurs capturées), **dégradation propre** (journalise si non configuré). Une notification qui échoue ne doit jamais faire échouer un virement. » |
| **`report_service.py`** | Génère les rapports serveur : PDF d'activité (reportlab) et Excel des transactions (openpyxl). | « Générés côté serveur : données complètes et à jour, pas de logique métier dans le navigateur. » |
| **`suspicion_report_service.py`** | Génère le **dossier de déclaration de soupçon** (PDF LBC-FT) d'une alerte confirmée. | Voir §6.3 — l'argument conformité du projet. |

### 4.6 — Les routers = les points d'entrée HTTP (`app/routers/`)

Un router **valide → délègue au service → traduit en réponse HTTP**.

| Fichier | Endpoints (principaux) | Accès |
|---|---|---|
| **`auth.py`** | `POST /auth/login`, `/refresh`, `GET /auth/me` | Public |
| **`users.py`** | `GET/POST/PATCH /users` | Admin |
| **`clients.py`** | `GET/POST/PATCH/DELETE /clients` (+ recherche nom/CIN) | Conseiller, Directeur |
| **`accounts.py`** | `GET/POST/PATCH /accounts` (blocage/déblocage) | Conseiller, Directeur |
| **`transactions.py`** | `POST /transactions` (scoring temps réel), `GET /transactions` | Conseiller (saisie) |
| **`alerts.py`** | `GET/PATCH /alerts` (qualification obligatoire à la clôture), **`GET /alerts/{id}/declaration-soupcon.pdf`** | Directeur |
| **`analytics.py`** | `GET /analytics/kpi`, `/trends`, `/distribution`, **`/model-health`** | Directeur |
| **`reports.py`** | `GET /reports/activity.pdf`, `/transactions.xlsx` | Directeur |
| **`notifications.py`** | `POST /notifications/test`, `/telegram/link-me` (auto-liaison du chat) | Selon rôle |
| **`audit.py`** | `GET /audit-logs` | Admin |

> **Point clé : les codes HTTP.** 200 OK, 201 créé, 400 requête métier refusée (solde
> insuffisant, clôture sans qualification), 401 non authentifié, 403 non autorisé,
> 404 introuvable, 409 conflit (CIN existant, alerte immuable, déclaration exigeant une
> fraude confirmée), 422 données invalides.

### 4.7 — Les scripts (`scripts/`)

| Fichier | Rôle |
|---|---|
| **`create_tables.py`** | Crée les tables à partir des modèles (`create_all`). |
| **`seed.py`** | Données de démo réalistes (30 clients, ~400 transactions, alertes). Reproductible (graine fixe). |
| **`train_model.py`** | **Entraîne et évalue le modèle ML** : génère le jeu simulé (+ étiquettes du feedback), compare RandomForest / IsolationForest / règles, sauvegarde `model.joblib` + `metrics.json`. Voir §5. |
| **`docker_entrypoint.py`** | Au démarrage du conteneur : attend la base, crée les tables, seed si base vide, lance uvicorn. **C'est ce qui rend `docker compose up` "magique".** |

### 4.8 — Les tests (`tests/`) — 70 tests

| Fichier | Vérifie |
|---|---|
| **`conftest.py`** | Base de test **dédiée** (`novabank_test`), chaque test dans une transaction annulée, fabriques d'utilisateurs/jetons. Force le moteur de règles (déterministe) en pointant `ML_MODEL_PATH` vers un fichier absent. |
| **`test_health.py`** | L'API démarre et répond. |
| **`test_auth.py`** | Connexion, verrouillage après 5 échecs, refresh token. |
| **`test_rbac.py`** | Un conseiller reçoit 403 sur les routes directeur/admin. |
| **`test_clients_api.py`**, **`test_accounts_api.py`** | CRUD, unicité CIN, désactivation logique, blocage. |
| **`test_transactions_api.py`** | Soldes corrects, virement atomique, refus solde insuffisant, alerte si risque élevé. |
| **`test_alerts_analytics_api.py`** | Cycle de vie d'une alerte, **clôture sans qualification refusée**, immuabilité, exactitude des KPI. |
| **`test_ml_scoring.py`** | Extraction des 7 features, explications (fractionnement, dormant), chargement du modèle, garde-fou sur les noms de features, SHAP. |
| **`test_suspicion_report.py`** | Le PDF de déclaration : contenu, préconditions (409 si non confirmée), RBAC, trace d'audit. |
| **`test_model_health.py`** | Les calculs de santé du modèle (état vide sans division par zéro, précision réelle, RBAC). |
| **`test_schemas_client.py`** | La validation Pydantic. |

> **Point clé : 70 tests, dont un tiers testent les ÉCHECS.** « Savoir qu'un système
> refuse correctement une mauvaise opération est aussi important que de savoir qu'il
> accepte une bonne. »

### 4.9 — Configuration du backend

| Fichier | Rôle |
|---|---|
| **`requirements.txt`** | Dépendances **versions figées** (`==`) — reproductibilité. |
| **`requirements-dev.txt`** | Outils de dev (pytest, ruff) — pas dans l'image de production. |
| **`pytest.ini`** | `pythonpath = .` pour que `pytest` trouve le module `app` (indispensable en CI). |
| **`Dockerfile`** | Image légère, utilisateur non-root, et **`RUN python -m scripts.train_model`** : le modèle ML est entraîné **pendant la construction de l'image** → l'image livrée contient un vrai modèle prêt. |
| **`.dockerignore`** | Exclut venv/caches du build. |
| **`.env.example`** | Modèle de configuration. Le vrai `.env` (secrets, jeton Telegram) n'est **jamais** versionné. |

---

<a name="5-ia"></a>
## 5. Le module IA en détail (`app/ml/` + `scripts/train_model.py`)

C'est LE cœur différenciant du PFE. Quatre fichiers à connaître parfaitement.

### 5.1 — `app/ml/features.py` : les 7 signaux

Transforme une transaction en **vecteur numérique**. Ce code est **partagé entre
l'entraînement et l'inférence** — même logique des deux côtés, sinon *training/serving
skew* (le bug classique du ML en production).

| # | Feature | Signification | Schéma de fraude visé |
|---|---|---|---|
| 1 | `amount_over_income` | montant ÷ revenu mensuel | Montant disproportionné |
| 2 | `amount_over_avg` | montant ÷ moyenne du compte | Rupture d'habitude |
| 3 | `is_night` | opération 00h-06h | Créneau anormal |
| 4 | `city_changed` | ville ≠ opération précédente | Déplacement suspect |
| 5 | `tx_last_24h` | nb d'opérations sur 24h | Rafale |
| 6 | `cumul_72h_over_income` ⭐v2.1 | cumul 72h ÷ revenu (inclut l'op courante) | **Fractionnement** |
| 7 | `days_since_last_tx` ⭐v2.1 | jours d'inactivité (plafonné 365) | **Compte dormant réactivé** |

Le fichier contient aussi `explain_features()` : la traduction des signaux en phrase
française lisible (« cumul des opérations sur 72h élevé (13.1x le revenu) — possible
fractionnement »). **L'explication n'est pas un luxe : le directeur décide, il doit
comprendre.**

### 5.2 — `app/ml/model.py` : charger et expliquer

- Charge `ml_artifacts/model.joblib` **une seule fois** (au premier score).
- **Garde-fou** : vérifie que les noms de features de l'artefact correspondent à
  `FEATURE_NAMES` — un artefact obsolète est refusé (sinon prédictions silencieusement
  fausses).
- Calcule les **valeurs SHAP** de chaque prédiction (`shap.TreeExplainer`) : la
  contribution de chaque variable au score, stockée en base et affichée en graphique.
- **Robuste** : si SHAP indisponible → renvoie `None`, l'application continue.

### 5.3 — `scripts/train_model.py` : entraîner honnêtement

1. **Données** : ~20 000 transactions simulées (1,5 % de fraudes — la fraude est RARE,
   on n'équilibre pas le jeu de test). **Chevauchement volontaire** : 7 % des opérations
   légitimes sont "atypiques", et les fraudes se répartissent sur **7 profils** dont un
   "discret". Sans chevauchement, les métriques seraient parfaites et sans valeur.
2. **Cohérence physique** ⭐ : `_make_features()` impose les lois du réel — le cumul 72h
   inclut l'opération courante (donc cumul ≥ montant/revenu), un compte inactif ≥ 1 jour
   n'a rien sur 24h, ≥ 3 jours rien sur 72h. **Leçon apprise** : la première version
   tirait ces valeurs indépendamment → combinaisons impossibles → les vraies
   transactions tombaient hors distribution (un retrait de 13x le revenu scorait 49 !).
3. **Boucle de feedback** : `load_feedback_labels()` ajoute les alertes qualifiées par
   le directeur comme exemples d'entraînement. **Le système apprend de l'agence.**
4. **Comparaison** : RandomForest (retenu) vs IsolationForest vs baseline de règles.
5. **Métriques honnêtes** : précision/rappel/F1/AUC-PR — jamais l'accuracy (trompeuse à
   98,5 % de classe majoritaire). Résultats : RF F1 0,58 / AUC-PR 0,61 / précision 0,77
   vs baseline F1 0,31. Détails dans [evaluation_ml.md](evaluation_ml.md).

### 5.4 — `app/services/scoring_service.py` : l'intégration

```
extract_features (code partagé)
        │
        ├── modèle ML présent ?  → RandomForest → score + SHAP   (ml-rf-v2.1)
        └── sinon                → règles pondérées              (mvp-rules-v1)
```

Chaque `RiskScore` enregistre `model_version` + `shap_values`. La baseline n'est pas
jetée : elle sert de **comparaison chiffrée** et de **secours opérationnel**.

---

<a name="6-ameliorations"></a>
## 6. Les 4 améliorations métier v2.1 (pourquoi + comment)

> Chacune répond à un **vrai problème documenté** des banques marocaines (Attijariwafa
> cible fraude/risque/conformité ; Bank Al-Maghrib publie un « Suivi de la fraude »).
> Le récit : *détecter mieux (1+2) → déclarer plus vite (3) → rester fiable (4)*.

### 6.1 — Détection du fractionnement (*structuring*)

- **Le problème réel** : les fraudeurs découpent un gros montant en plusieurs petits
  (4 × 9 500 au lieu de 38 000) pour passer sous les seuils unitaires. Un scoring
  transaction-par-transaction ne le voit **jamais**.
- **La solution** : la feature `cumul_72h_over_income` — somme des opérations du compte
  sur 72h (opération courante incluse) rapportée au revenu. Chaque opération isolée est
  banale ; **seul le cumul trahit le schéma**.
- **Où c'est codé** : `features.py` (calcul SQL `SUM` sur 72h + explication),
  `scoring_service.py` (poids dans les règles), `train_model.py` (profil de fraude
  "structuring"), tests dans `test_ml_scoring.py`.
- **Résultat mesurable** : c'est devenue **la feature la plus importante du modèle**
  (0,32) — la démonstration chiffrée que l'ingénierie de features guidée par le métier
  vaut plus qu'un modèle plus complexe.

### 6.2 — Comptes dormants réactivés

- **Le problème réel** : un compte inactif depuis des mois qui « se réveille » avec un
  gros retrait = signature classique de **compte compromis / usurpation** (fraude au
  virement, ingénierie sociale — en croissance au Maroc).
- **La solution** : la feature `days_since_last_tx` (jours depuis la dernière opération,
  plafonnée à 365 pour borner l'influence d'un compte très ancien).
- **Où c'est codé** : mêmes fichiers que 6.1 (profil "dormant" à l'entraînement, seuils
  30/90 jours dans les règles et l'explication).

### 6.3 — Dossier de déclaration de soupçon (PDF LBC-FT) 🥇

- **Le problème réel** : la loi marocaine **43-05** (LBC-FT) oblige les banques à
  déclarer les opérations suspectes à l'**ANRF**. En agence, constituer ce dossier est
  manuel, lent, et source d'oublis.
- **La solution** : sur une alerte **qualifiée fraude confirmée**, un clic génère un PDF
  complet : référence du dossier, **identité KYC** du client, compte, opération
  incriminée, **analyse IA (score + SHAP traduit en français juridique)**, chronologie
  des opérations, cadre légal. Toujours présenté comme **modèle indicatif** (données
  simulées).
- **Les règles métier** (à savoir défendre) :
  - C'est **la décision humaine** du directeur qui déclenche le droit de générer — jamais
    le score seul (l'IA assiste, l'humain décide) → 409 si l'alerte n'est pas confirmée.
  - La génération est **tracée dans l'audit** (qui, quand, quelle alerte) — l'édition
    d'un document réglementaire est un événement sensible.
  - RBAC : réservé au directeur (403 sinon).
- **Où c'est codé** : `services/suspicion_report_service.py` (composition du PDF),
  `routers/alerts.py` (endpoint + préconditions + audit), `Fraud.tsx` (bouton),
  `test_suspicion_report.py` (6 tests).

### 6.4 — Page « Suivi de la fraude & santé du modèle » (MLOps)

- **Le problème réel** : un modèle de fraude **se dégrade avec le temps** — les fraudeurs
  s'adaptent (*dérive conceptuelle*). Sans surveillance, on laisse passer des fraudes en
  silence, ou on noie le directeur sous les faux positifs.
- **La solution** : `GET /analytics/model-health` calcule, **à partir des qualifications
  réelles du directeur** (pas du jeu de test !) :
  - la **précision en production** = fraudes confirmées ÷ alertes qualifiées ;
  - le **taux de faux positifs** (la charge de travail inutile) ;
  - le **volume de feedback** disponible pour réentraîner ;
  - le temps moyen de traitement d'une alerte ;
  - l'**histogramme des scores** (tranches ≥ 70 en rouge) ;
  - la **version du moteur actif**.
- **Le geste MLOps à défendre** : « quand réentraîner ? » → dès que le feedback est
  significatif (≥ 50 étiquettes) ou si la précision passe sous 50 %.
- **Où c'est codé** : `routers/analytics.py` (agrégations **côté PostgreSQL** :
  `FILTER`, `date_trunc`, `LEAST/FLOOR` pour l'histogramme), `schemas/analytics.py`
  (`ModelHealthResponse`), `pages/SanteModele.tsx` (KPI + Plotly), `test_model_health.py`.

---

<a name="7-frontend"></a>
## 7. Le FRONTEND fichier par fichier

### 7.1 — Point d'entrée et routage

| Fichier | Rôle |
|---|---|
| **`index.html`** | La page HTML minimale qui accueille React. |
| **`src/main.tsx`** | Monte l'application dans les fournisseurs globaux (Thème, Toasts, Auth, Router). |
| **`src/App.tsx`** | Le **routage** avec **gardes de rôle** : `/fraude`, `/sante-modele`, `/rapports`, `/dashboard` → directeur ; `/users`, `/audit` → admin. « Le vrai contrôle est le RBAC serveur ; la garde frontend n'est que du confort de navigation. » |

### 7.2 — Communication avec le backend (`src/api/`)

| Fichier | Rôle | Point clé |
|---|---|---|
| **`api/client.ts`** | Client axios unique : ajoute le JWT à chaque requête et **renouvelle le jeton expiré** de façon transparente. | « L'utilisateur n'est jamais déconnecté brutalement. » |
| **`api/types.ts`** | Les types TypeScript **miroirs des schémas Pydantic** (User, Client, Transaction, `Alert.resolution`, `ModelHealth`…). | « Le typage attrape les erreurs **avant** l'exécution. » |

### 7.3 — États globaux (`src/contexts/`)

| Fichier | Rôle |
|---|---|
| **`AuthContext.tsx`** | Qui est connecté, son rôle, login/logout, page d'accueil par rôle. |
| **`ThemeContext.tsx`** | Mode clair/sombre, mémorisé dans le navigateur. |
| **`ToastContext.tsx`** | Notifications animées (« Client créé », « Erreur »). |

### 7.4 — Composants réutilisables (`src/components/`)

- **`ui/`** — briques de base style *shadcn/ui* : `button`, `card`, `input`, `badge`,
  `table`, `dialog`, `skeleton`. Écrites une fois, utilisées partout.
- **`layout/`** — `Sidebar` (menu par rôle, animé), `Navbar`, `AppLayout`.
- **`shared/`** — métier : `KpiCard`, `ScoreBadge` (la couleur EST l'information),
  `Plot` (Plotly avec thème partagé), **`ShapChart`** (les barres bidirectionnelles
  SHAP : à droite orange = pousse vers la fraude, à gauche = vers le normal).

### 7.5 — Les pages (`src/pages/`) — 14 écrans

| Fichier | Écran |
|---|---|
| **`Login.tsx`** | Connexion (dégradé de marque + carte en verre). |
| **`Dashboard.tsx`** | Tableau de bord directeur (KPI + graphiques Plotly). |
| **`Clients.tsx`** / **`ClientDetail.tsx`** | Liste/recherche / fiche détaillée. |
| **`Accounts.tsx`** | Gestion des comptes (filtres, blocage). |
| **`NewTransaction.tsx`** | Saisie d'opération avec **score + SHAP en temps réel** ⭐. |
| **`Transactions.tsx`** | Historique filtrable. |
| **`Fraud.tsx`** | Centre d'alertes : détail explicable (SHAP), **qualification obligatoire à la clôture** (Fraude confirmée / Faux positif) ⭐, **bouton « Générer la déclaration de soupçon »** sur une fraude confirmée. |
| **`SanteModele.tsx`** ⭐v2.1 | Suivi de la fraude & santé du modèle : KPI MLOps + histogramme des scores + pédagogie « quand réentraîner ». |
| **`Reports.tsx`** | Exports PDF/Excel serveur + CSV client. |
| **`Assistant.tsx`** | Assistant qui répond avec les vraies données de l'API. |
| **`Users.tsx`** / **`Audit.tsx`** | Gestion des utilisateurs (+ contacts Telegram) / journal d'audit. |
| **`Settings.tsx`** | Profil, thème, **liaison Telegram en 1 clic** + bouton test. |

### 7.6 — Utilitaires et style

| Fichier | Rôle |
|---|---|
| **`lib/format.ts`** | Formats des montants (MAD) et dates, au même endroit. |
| **`lib/utils.ts`** | Fusion intelligente des classes CSS. |
| **`styles/index.css`** | **Le système de design** : couleurs orange Attijari, thème clair/sombre, glassmorphism. Changer la marque = changer ce fichier. |

### 7.7 — Configuration du frontend

| Fichier | Rôle |
|---|---|
| **`package.json`** | Dépendances + commandes (`npm run dev`, `npm run build`). |
| **`vite.config.ts`** | Build + **proxy `/api`** vers le backend en dev (évite CORS). |
| **`tsconfig.json`** | TypeScript **strict**. |
| **`nginx.conf`** | En production : sert l'app et **relaie `/api`** vers le conteneur backend. |
| **`Dockerfile`** | Build puis nginx (image ~50 Mo). |

---

<a name="8-infrastructure"></a>
## 8. L'INFRASTRUCTURE (Docker, CI, Alembic)

| Fichier | Rôle | Point clé |
|---|---|---|
| **`docker-compose.yml`** | Les **3 services** (postgres, api, frontend) sur un réseau privé. Ports hôte : frontend **8090**, api **8000**, postgres **5433** (5432 souvent occupé par un PostgreSQL local). | « Une seule commande lance tout. Les services se parlent par **nom de service**. » |
| **`backend/Dockerfile`** | Installe, copie le code, **entraîne le modèle ML au build**, utilisateur non-root. | « L'image livrée contient un modèle prêt — pas d'étape manuelle. » |
| **`demarrer.bat` / `.sh`** | Lancement 1 clic (vérifie Docker, build, up, ouvre le navigateur). | Pensé pour des collègues non techniques. |
| **`.github/workflows/ci.yml`** | À chaque push : ruff + **70 tests** sur machine neuve avec un vrai PostgreSQL (service). | « Le badge vert prouve que tout fonctionne, à chaque modification. » |
| **`backend/alembic/`** | Migrations versionnées : baseline → resolution (feedback) → shap_values → contacts user. | « `create_all` crée une base neuve, mais n'ALTÈRE pas une base existante — c'est le rôle des migrations. » |
| **`.gitattributes`** | CRLF pour `.bat`, LF pour `.sh`. | Évite le bug « la fenêtre se ferme toute seule ». |

### Comment les conteneurs communiquent

```
  Navigateur ──► http://localhost:8090 ──► [ FRONTEND (nginx) ]
                                                │  /api/...
                                                ▼
                                          [ API (FastAPI) ]  ← modèle ML dans l'image
                                                │  postgres:5432
                                                ▼
                                          [ BASE (PostgreSQL) ]
```

---

<a name="9-concepts"></a>
## 9. Les 18 concepts clés à maîtriser

1. **API REST** — communication frontend/backend via HTTP (GET lire, POST créer, PATCH modifier, DELETE supprimer).
2. **ORM (SQLAlchemy)** — objets Python ↔ tables SQL. Protège des injections SQL.
3. **Pydantic vs SQLAlchemy** — le **contrat de l'API** vs la **base**. Deux choses différentes.
4. **JWT** — badge signé remis à la connexion, vérifié à chaque requête sans session serveur.
5. **RBAC** — droits par rôle, vérifiés **côté serveur à chaque requête**.
6. **bcrypt** — hachage à sens unique des mots de passe.
7. **ACID + verrou `FOR UPDATE`** — virements atomiques et isolés.
8. **Injection de dépendances (`Depends`)** — FastAPI fournit session/utilisateur à chaque endpoint. Rend le code testable.
9. **Architecture en couches** — router → service → modèle.
10. **Docker** — l'application ET son environnement dans un colis reproductible.
11. **CI** — tests automatiques à chaque push.
12. **CORS** — liste blanche des origines autorisées à appeler l'API.
13. **Feature engineering** ⭐ — transformer une transaction en signaux numériques guidés par la connaissance métier. Nos 2 features v2.1 (cumul 72h, inactivité) battent en importance toutes les autres.
14. **Métriques déséquilibrées** ⭐ — précision/rappel/F1/AUC-PR, jamais l'accuracy quand la classe positive fait 1,5 %.
15. **SHAP (XAI)** ⭐ — répartition mathématique du score entre les variables (valeurs de Shapley). Exigence d'explicabilité (RGPD / EU AI Act).
16. **Boucle de feedback (human-in-the-loop)** ⭐ — les qualifications du directeur deviennent les étiquettes du prochain entraînement.
17. **Training/serving skew** ⭐ — tout écart entre l'entraînement et l'inférence (code OU distribution des données). Notre leçon v2.1 : des données simulées **physiquement incohérentes** rendent le modèle imprévisible sur les vraies transactions.
18. **Dérive conceptuelle & MLOps** ⭐ — un modèle se dégrade quand le monde change ; on surveille sa performance réelle en production (page Santé du modèle) et on réentraîne sur signal.

---

<a name="10-glossaire"></a>
## 10. Glossaire express

- **MVP** — la plus petite version qui résout le problème de bout en bout.
- **Endpoint** — une adresse de l'API (ex. `POST /transactions`).
- **CRUD** — Create, Read, Update, Delete.
- **Migration** — modification versionnée du schéma de la base.
- **Seed** — remplir la base avec des données de départ.
- **Suppression logique** — marquer "inactif" au lieu de supprimer (garde l'historique).
- **Feature (IA)** — caractéristique numérique extraite d'une donnée.
- **Baseline** — solution simple de référence à battre (notre moteur de règles).
- **Artefact (ML)** — le fichier du modèle entraîné (`model.joblib`) + ses métadonnées.
- **LBC-FT** — Lutte contre le Blanchiment de Capitaux et le Financement du Terrorisme.
- **ANRF** — Autorité Nationale du Renseignement Financier (Maroc) : reçoit les déclarations de soupçon.
- **KYC** — *Know Your Customer* : l'identité vérifiée du client (nom, CIN, profession, revenu).
- **Fractionnement / structuring** — découper un gros montant en petits pour éviter les seuils.
- **AUC-PR** — aire sous la courbe précision-rappel : LA métrique des problèmes déséquilibrés.
- **Dérive conceptuelle** — le phénomène que les données réelles s'éloignent de celles de l'entraînement.

---

<a name="11-jury"></a>
## 11. Questions du jury + réponses

> Prépare ces réponses à voix haute. Ce sont les questions les plus probables.

**Q : Pourquoi FastAPI plutôt que Django ou Flask ?**
R : FastAPI est très performant, offre une **validation forte** avec Pydantic, génère la
**documentation Swagger automatiquement**, et c'est du Python — le module IA
(scikit-learn) s'intègre nativement. Flask est plus minimal, Django plus lourd pour une
API pure.

**Q : Pourquoi PostgreSQL ?**
R : Données très relationnelles (client → comptes → transactions → scores → alertes).
PostgreSQL est robuste, standard en entreprise, et gère nativement les verrous
transactionnels de nos virements ET les agrégations de nos tableaux de bord.

**Q : Comment garantissez-vous qu'un virement ne corrompt pas les soldes ?**
R : `SELECT ... FOR UPDATE` sur les deux comptes (verrouillés par id croissant pour
éviter les deadlocks), dans une transaction unique. Deux virements simultanés
s'exécutent en série. Propriétés **ACID**.

**Q : Votre IA, c'est du vrai Machine Learning ?**
R : Oui. Un **Random Forest supervisé** (scikit-learn) entraîné sur ~20 000 transactions
simulées et comparé à deux références : un Isolation Forest (non supervisé) et notre
moteur de règles (baseline). Il gagne sur toutes les métriques (F1 0,58 vs 0,31 ;
AUC-PR 0,61 vs 0,26). Chaque score est **expliqué** (texte + SHAP), **versionné**
(`model_version`), et le système **se replie automatiquement** sur les règles si
l'artefact manque. Et surtout : il **apprend des décisions du directeur** (boucle de
feedback).

**Q : Vos données sont simulées — quelle valeur a votre évaluation ?**
R : L'accès au SI réel était hors périmètre (confidentialité). Nous avons compensé par
trois exigences : un **chevauchement volontaire** des classes (7 profils de fraude dont
un "discret" — métriques réalistes, pas parfaites), la **cohérence physique** des
features simulées (le cumul 72h inclut l'opération courante, un compte dormant n'a rien
dans ses fenêtres — sinon le modèle est imprévisible sur les vraies transactions), et
des **métriques adaptées au déséquilibre** (AUC-PR, jamais l'accuracy). La méthodologie
est reproductible sur données réelles.

**Q : Pourquoi le fractionnement nécessite-t-il une feature dédiée ?**
R : Parce que chaque opération isolée est **banale** — 9 500 MAD ne déclenche rien. Seul
le **cumul temporel** (72h, opération courante incluse, rapporté au revenu) révèle le
schéma. C'est d'ailleurs devenue la feature la plus importante du modèle (0,32) : la
connaissance métier LBC-FT injectée dans l'ingénierie de features vaut plus qu'un modèle
plus complexe.

**Q : Un score élevé déclenche-t-il automatiquement la déclaration de soupçon ?**
R : **Non — jamais.** L'IA crée une alerte et notifie ; c'est le **directeur** qui
qualifie (fraude confirmée / faux positif). La génération du dossier ANRF n'est possible
QUE sur une alerte qualifiée fraude confirmée (409 sinon), elle est réservée au rôle
directeur et **tracée dans l'audit**. L'IA assiste, l'humain décide — c'est aussi
l'esprit des exigences réglementaires sur l'IA.

**Q : Comment savez-vous que votre modèle reste bon dans le temps ?**
R : Page « Santé du modèle » : nous calculons la **précision réelle en production**
(fraudes confirmées ÷ alertes qualifiées) et le taux de faux positifs **à partir des
décisions du directeur** — pas du jeu de test. Si la précision chute ou dès que le
feedback dépasse ~50 étiquettes, on réentraîne : les qualifications deviennent des
exemples d'entraînement. C'est la réponse à la **dérive conceptuelle**.

**Q : Expliquez SHAP simplement.**
R : SHAP répartit le score entre les variables selon les valeurs de Shapley (théorie des
jeux) : chaque variable reçoit sa **contribution** — positive (pousse vers la fraude) ou
négative (vers le normal). Le directeur voit non seulement *que* c'est risqué mais
*pourquoi*, variable par variable. Ces contributions sont **stockées** avec chaque score
et reprises dans le dossier de déclaration.

**Q : Comment sécurisez-vous l'application ?**
R : bcrypt, JWT courts + refresh, RBAC serveur, ORM (anti-injection), validation
Pydantic (anti mass-assignment), verrouillage après 5 échecs, journal d'audit
append-only, secrets hors dépôt (.env). Alignés sur l'**OWASP API Security Top 10**.

**Q : Comment testez-vous le projet ?**
R : **70 tests** pytest (auth, RBAC, transactions, ML, déclaration, santé du modèle),
dont un tiers testent les **échecs**. Base de test dédiée, chaque test dans une
transaction annulée. CI GitHub Actions à chaque push. Les tests forcent le moteur de
règles pour être **déterministes** ; le ML a ses propres tests avec artefacts jetables.

**Q : Un collègue peut-il lancer le projet facilement ?**
R : `docker compose up` ou un double-clic : la base démarre, l'API attend la base, crée
les tables, injecte la démo, et le modèle ML est **déjà dans l'image** (entraîné au
build). Prérequis unique : Docker Desktop.

**Q : Quelles sont les limites de votre projet ?**
R : Données simulées (SI réel hors périmètre), réentraînement déclenché manuellement
(l'automatisation périodique est une perspective), et pas de streaming temps réel.
Limites **assumées et documentées**. Perspectives citées : screening de listes de
sanctions, analyse de graphes, streaming Kafka, XGBoost/LightGBM.

**Q : Qu'avez-vous appris ?**
R : Le cycle complet d'une application professionnelle — architecture en couches,
sécurité, base de données transactionnelle — PLUS le cycle complet d'un système de ML :
ingénierie de features guidée métier, évaluation honnête sur classes déséquilibrées,
explicabilité, déploiement (modèle dans l'image), et surveillance en production. Et une
leçon précieuse : **la qualité des données prime sur la sophistication du modèle**.

---

> ✅ **Si tu comprends ce guide, tu maîtrises le projet.** Relis-le avec les fichiers
> ouverts en parallèle, refais le parcours de démonstration (transaction suspecte →
> alerte → qualification → déclaration → santé du modèle), et entraîne-toi à répondre
> aux questions du §11 à voix haute. Pour reconstruire de zéro :
> [GUIDE_CONSTRUCTION.md](GUIDE_CONSTRUCTION.md). Bonne chance !
