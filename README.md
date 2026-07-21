<div align="center">

# 🏦 NovaBank — Plateforme bancaire intelligente d'aide à la décision

**Plateforme web pour agence bancaire** : gestion des clients, comptes et transactions,
**détection d'anomalies par Machine Learning (Random Forest) avec explication lisible**,
boucle de feedback, centre d'alertes, tableau de bord analytique et cybersécurité
(JWT, RBAC, audit).

> 🎓 **Version PFE** — cette version enrichit le MVP d'un véritable modèle de Machine
> Learning entraîné et évalué, d'une boucle de feedback humain et de migrations Alembic.

Projet de stage — El Mehdi Ribahi 
Encadrante : Raiss Bouchra

</div>

---

## 🚀 Démarrage en 1 clic (le plus simple)

> **Prérequis unique : [Docker Desktop](https://www.docker.com/products/docker-desktop/) installé.**
> Rien d'autre à installer (ni Python, ni Node, ni PostgreSQL).

| Système | Comment lancer |
|---|---|
| **Windows** | Double-cliquer sur **`demarrer.bat`** |
| **macOS / Linux** | Exécuter **`./demarrer.sh`** dans un terminal |
| **N'importe où** | Taper **`docker compose up -d`** |

Le script démarre **toute la plateforme** (base de données + backend + frontend), crée les
tables et injecte les données de démonstration **automatiquement**.

> ⚡ **1ᵉ lancement** : construction des images — **connexion internet requise** (2–5 min,
> pour télécharger les images de base Docker). **Lancements suivants** : les images sont
> réutilisées → démarrage en **quelques secondes, même hors-ligne**. Idéal pour une démo :
> lance-le une fois chez toi avec internet, ensuite tout démarre en local le jour J.
>
> **As-tu mis à jour le code** (nouveau ZIP / `git pull`) ? Utilise **`reconstruire.bat`**
> (Windows) ou **`./reconstruire.sh`** : il reconstruit les images **et réinitialise la base**
> (indispensable si le schéma a évolué, ex. nouvelles colonnes) puis recrée les données de démo.
> Un simple `demarrer.bat` garde l'ancienne base — si tu vois « les clients ne s'affichent pas »
> ou une erreur à la création après une mise à jour, lance **`reconstruire.bat`** une fois.

Au bout de ~1 minute (2–5 min la première fois), l'application est prête :

| Adresse | Contenu |
|---|---|
| 👉 **http://localhost:8090** | **L'application** (interface web) |
| http://localhost:8000/docs | Documentation interactive de l'API (Swagger) |

### 🔑 Comptes de démonstration

| Rôle | Email | Mot de passe |
|---|---|---|
| Directeur d'agence | `directeur@novabank.ma` | `Directeur@2026!` |
| Conseiller bancaire | `conseiller@novabank.ma` | `Conseiller@2026!` |
| Administrateur | `admin@novabank.ma` | `Admin@2026!` |

**Pour arrêter** : double-clic sur `arreter.bat` (Windows) ou `docker compose down`.

---

## 🎬 Le scénario démontré

```
  Conseiller saisit une transaction
          │
          ▼
  Le backend l'enregistre (verrou anti-corruption des soldes)
          │
          ▼
  Le moteur de risque calcule un score 0–100 + une explication lisible
          │
          ▼
  Si le score dépasse le seuil → une ALERTE est créée automatiquement
          │
          ▼
  Le directeur voit l'alerte sur son dashboard, lit l'explication,
  la qualifie et la clôture  →  tout est tracé dans le journal d'audit
```

**Exemple d'explication produite** : *« Signaux détectés : montant 3,2× supérieur au
revenu mensuel du client ; opération nocturne, hors des horaires habituels ; ville
inhabituelle. »*

---

## 🧱 Architecture

```
┌────────────────────┐   HTTP    ┌──────────────────────────┐   SQL   ┌──────────────┐
│   Frontend React   │  + JWT    │      Backend FastAPI     │ ──────► │  PostgreSQL  │
│  (nginx, port 8090)│ ────────► │      (port 8000)         │         │  (port 5433) │
│                    │  /api/... │                          │         │              │
│  Login, Dashboard, │           │  routers  (HTTP)         │         │  8 tables    │
│  Clients, Comptes, │           │  services (métier)       │         │  contraintes │
│  Transactions,     │           │  schemas  (Pydantic)     │         │  index       │
│  Fraude, Rapports… │           │  models   (SQLAlchemy)   │         │              │
└────────────────────┘           └──────────────────────────┘         └──────────────┘
        │                                     │                              │
        └─────────────────────────────────────┴──────────────────────────────┘
                    Tout est orchestré par Docker Compose
```

**Architecture en couches** (`routers → services → models`) : un router ne touche jamais
la base directement, un service ne connaît jamais HTTP. C'est ce qui rend le code
testable et évolutif.

---

## 🛠️ Stack technique

| Couche | Technologie | Pourquoi |
|---|---|---|
| Frontend | React 18 + **TypeScript** + Vite | Typage fort, écosystème riche, build rapide |
| UI | Tailwind CSS + Framer Motion | Design premium, mode sombre, animations |
| Backend | **FastAPI** (Python) | Performant, validation Pydantic, Swagger auto |
| ORM | **SQLAlchemy 2.0** | Modèles Python ↔ tables PostgreSQL |
| Base | **PostgreSQL 16** | SGBD relationnel robuste, standard entreprise |
| IA | **scikit-learn (Random Forest)** | Scoring de risque entraîné + évalué, repli sur règles |
| Explicabilité | **SHAP** | Contribution de chaque variable au score (XAI) |
| Rapports | **reportlab + openpyxl** | Export PDF et Excel côté serveur |
| Migrations | **Alembic** | Versionnage du schéma de la base |
| Sécurité | **JWT + bcrypt + RBAC** | Auth stateless, rôles vérifiés côté serveur |
| Conteneurs | **Docker Compose** | Déploiement reproductible en une commande |
| Tests / CI | **pytest + GitHub Actions** | 92 tests d'intégration, badge vert à chaque push |

---

## ✨ Fonctionnalités (10 modules du cahier des charges)

- 🔐 **Authentification & rôles** — JWT, 3 rôles (Admin / Directeur / Conseiller),
  verrouillage anti force-brute après 5 échecs, refresh token.
- 👥 **Clients** — création, recherche (nom/CIN), fiche complète, désactivation logique.
- 💳 **Comptes** — ouverture, numéro généré par le système, blocage/déblocage.
- 🔁 **Transactions** — dépôt, retrait, **virement avec verrou PostgreSQL** (pas de
  corruption de solde en cas d'opérations simultanées).
- 🤖 **Scoring de risque par IA** — modèle **Random Forest** (scikit-learn) sur **7 signaux**
  (montant/revenu, heure, ville, fréquence, **cumul 72h anti-fractionnement**, **inactivité
  du compte**), score 0–100 **avec explication lisible**. Repli automatique sur un moteur
  de règles si le modèle est absent.
- 🧩 **Détection du fractionnement** (*structuring*) — le cumul des opérations sur 72h
  rapporté au revenu attrape les gros montants découpés en petits pour passer sous les
  seuils (1ʳᵉ feature du modèle en importance : 0,40).
- 💤 **Comptes dormants réactivés** — un compte inactif depuis des mois qui « se réveille »
  avec une grosse opération (signature d'usurpation) est signalé.
- 🔍 **Explicabilité SHAP** — contribution de chaque variable au score, affichée en
  graphique (méthode XAI de référence, exigence de conformité RGPD / EU AI Act).
- 📑 **Rapports serveur** — génération PDF (reportlab) et Excel (openpyxl) téléchargeables.
- 🔁 **Boucle de feedback** — la qualification des alertes par le directeur
  (fraude confirmée / faux positif) alimente le réentraînement du modèle.
- 🚨 **Centre d'alertes** — création automatique, cycle de vie (ouverte → en cours →
  clôturée avec qualification obligatoire), détail explicable.
- ⚖️ **Déclaration de soupçon (LBC-FT)** — dossier PDF réglementaire généré en un clic
  depuis une alerte confirmée : identité KYC, opération, analyse IA + SHAP, chronologie
  du compte, cadre légal marocain (loi 43-05 / ANRF). Modèle indicatif, audité.
- 📈 **Suivi de la fraude & santé du modèle (MLOps)** — précision réelle en production
  calculée sur les qualifications du directeur, taux de faux positifs, volume de feedback,
  distribution des scores — pour savoir **quand réentraîner** (inspiré du Suivi de la
  fraude de Bank Al-Maghrib).
- 🕵️ **Fraude interne** — profils d'activité des conseillers calculés depuis les
  opérations et le journal d'audit (saisies nocturnes, concentration sur un compte,
  volume vs pairs, part d'opérations risquées) avec drapeaux explicables.
- ⚙️ **Seuil d'alerte configurable** — le directeur ajuste la sensibilité de la
  détection depuis l'interface ; chaque changement est tracé dans l'audit
  (le `.env` ne fournit plus que la valeur par défaut).
- 🎚️ **Profil de risque par client** — calibre le scoring pour un client donné en
  neutralisant les signaux non pertinents (✈️ voyageur fréquent → ignore le changement
  de ville, 💎 grande fortune → ignore les ratios montant/revenu, 🏢 compte professionnel
  → ignore la rafale d'opérations). Le modèle n'est pas modifié : la feature passe à 0
  (visible dans SHAP).
- ✅ **Workflow d'approbation (maker-checker)** — séparation des tâches : le **conseiller
  PROPOSE** un profil (à la création ou sur la fiche), le **directeur APPROUVE ou REJETTE**.
  Tant qu'elle n'est pas approuvée, la demande n'affecte pas le score. Un conseiller ne
  peut donc jamais assouplir la détection seul (parade à la fraude interne) ; motif
  obligatoire et chaque étape (demande, approbation, rejet) tracée dans l'audit.
- 📊 **Tableau de bord** — KPI et graphiques Plotly (activité, répartition, risque).
- 📄 **Rapports** — export des données (CSV/Excel).
- 📜 **Audit** — journal append-only de toutes les actions sensibles (qui, quoi, quand, IP).
- 📱 **Version mobile installable (PWA)** — l'application s'installe sur le téléphone du
  directeur (icône sur l'écran d'accueil, plein écran) : navigation par barre basse,
  page de fraude optimisée pour la décision au pouce (détail auto-centré, gros boutons
  de qualification). Le service worker ne met jamais l'API en cache — données toujours
  fraîches et authentifiées.
- 🌗 **Interface premium** — mode clair/sombre, responsive (mobile → desktop), glassmorphism.

---

## 👩‍💻 Développement (sans Docker)

Pour développer avec rechargement à chaud (modifier le code sans reconstruire) :

<details>
<summary><b>Backend</b> (Python 3.14)</summary>

```bash
docker compose up -d postgres     # juste la base
cd backend
python -m venv venv
venv\Scripts\activate             # Windows  (source venv/bin/activate sur macOS/Linux)
pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env            # puis adapter si besoin
python -m scripts.create_tables   # crée les tables
python -m scripts.seed            # données de démo
uvicorn app.main:app --reload     # http://localhost:8000/docs
```

Tests : `pytest -v`  ·  Lint : `ruff check .`
</details>

<details>
<summary><b>Frontend</b> (Node 22)</summary>

```bash
cd frontend
npm install
npm run dev                       # http://localhost:5173
```
</details>

---

## 📚 Documentation

| Document | Contenu |
|---|---|
| **[docs_v2/ULTRA_COURS.md](docs_v2/ULTRA_COURS.md)** | ⭐⭐ **La formation complète** : 24 modules (terminal, Git, Python, SQL, HTML/CSS, TypeScript, HTTP/REST, FastAPI, SQLAlchemy, Pydantic, sécurité, ACID, React, ML, SHAP, MLOps, Docker, tests, CI, métier bancaire) avec cours, exercices et ressources officielles + le plan pour **refaire NovaBank de zéro** + un planning sur 10 semaines. |
| **[docs_v2/APPRENDRE_DE_ZERO.md](docs_v2/APPRENDRE_DE_ZERO.md)** | ⭐ **Apprendre de zéro** : chaque notion, chaque langage, chaque mot informatique expliqué pour un débutant total, avec le POURQUOI de chaque décision + glossaire A→Z. |
| **[docs/GUIDE_COMPLET.md](docs/GUIDE_COMPLET.md)** | ⭐ **Comprendre tout le projet** : chaque fichier, le module IA en détail, les améliorations métier (pourquoi + comment + où), 18 concepts clés, glossaire, questions du jury. |
| **[docs/GUIDE_CONSTRUCTION.md](docs/GUIDE_CONSTRUCTION.md)** | ⭐ **Reconstruire le projet de zéro**, en 16 parties ordonnées (base → sécurité → services → IA → frontend → Docker → améliorations → mobile), avec les pièges vécus. |
| [docs/evaluation_ml.md](docs/evaluation_ml.md) | Méthodologie et métriques du module IA (7 features, SHAP, feedback, leçons ML) |
| [docs/notifications.md](docs/notifications.md) | Le système de notifications Telegram/email |
| [docs/plan_directeur.md](docs/plan_directeur.md) | Vision finale et étapes de réalisation |
| [docs/base_de_donnees.md](docs/base_de_donnees.md) | Modèle de données |
| [docs/schema_cible.sql](docs/schema_cible.sql) | Architecture PostgreSQL « grande échelle » (partitionnement, RLS, triggers) documentée pour l'évolution |

Chaque fichier de code contient un en-tête expliquant **son rôle, le problème qu'il
résout et les choix techniques** — la documentation vit dans le code.

---

## ⚠️ Périmètre

Prototype pédagogique sur **données simulées et anonymisées**. Aucune connexion à un
système bancaire réel, aucun mouvement d'argent réel. Environnement de démonstration
local (Docker).
