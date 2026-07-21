# 🎓 ULTRA-COURS — Maîtriser NovaBank et savoir le refaire de zéro

> **Ce document est une formation complète**, pas une documentation. Il t'apprend **chaque
> technologie** utilisée dans NovaBank, avec pour chacune : le **cours**, le **pourquoi**, son
> **usage réel dans le projet**, des **exercices**, et les **ressources officielles** pour
> approfondir.
>
> **Objectif final** : pouvoir **reconstruire NovaBank entièrement toi-même, sans IA**, et
> comprendre chaque ligne.
>
> **Comment l'utiliser ?** Ne le lis pas d'une traite. Suis les modules **dans l'ordre**, fais
> les exercices, et ne passe au suivant que quand tu peux **expliquer à voix haute** ce que tu
> viens d'apprendre. Compte **8 à 12 semaines** à raison de 1-2 h/jour pour tout maîtriser.
>
> **Documents compagnons** : [APPRENDRE_DE_ZERO.md](APPRENDRE_DE_ZERO.md) (les notions
> expliquées simplement), [../docs/GUIDE_COMPLET.md](../docs/GUIDE_COMPLET.md) (chaque fichier
> du projet), [../docs/GUIDE_CONSTRUCTION.md](../docs/GUIDE_CONSTRUCTION.md) (les commandes).

---

## 🗺️ Carte du parcours

| Partie | Modules | Ce que tu sauras faire |
|---|---|---|
| **I. Socle** | 0 → 2 | Utiliser un terminal, Git/GitHub, apprendre efficacement |
| **II. Langages** | 3 → 6 | Python, SQL, HTML/CSS, TypeScript |
| **III. Backend** | 7 → 12 | Construire une API sécurisée avec base de données |
| **IV. Frontend** | 13 → 16 | Construire une interface React professionnelle |
| **V. Intelligence artificielle** | 17 → 21 | Entraîner, évaluer, expliquer et surveiller un modèle |
| **VI. Industrialisation** | 22 → 24 | Docker, tests, intégration continue |
| **VII. Métier bancaire** | 25 | Comprendre la fraude, le KYC, la conformité LBC-FT |
| **VIII. Reconstruction** | — | Refaire NovaBank de zéro, étape par étape |
| **IX. Planning** | — | Un plan d'apprentissage semaine par semaine |

**Légende de chaque module** :
🎯 Objectif · 📚 Cours · 🤔 Pourquoi · 🏦 Dans NovaBank · ✍️ Exercices · 🔗 Ressources

---

# PARTIE I — LE SOCLE

## Module 0 — Comment apprendre à programmer (la méthode)

🎯 **Objectif** : ne pas perdre 6 mois à mal apprendre.

📚 **Cours.** Programmer ne s'apprend pas en lisant : ça s'apprend en **écrivant du code et en
débuggant**. Les 4 règles :

1. **La règle du 20/80** : 20 % de lecture, 80 % de pratique. Après chaque notion, **écris du
   code**, même 5 lignes.
2. **Ne copie jamais sans comprendre.** Si tu copies une ligne, demande-toi : *que fait-elle ?
   que se passe-t-il si je l'enlève ?* Teste ! Casser puis réparer est **la** meilleure façon
   d'apprendre.
3. **Apprends à lire une erreur.** Un message d'erreur n'est pas une punition, c'est une
   **information**. Lis-le en entier, de bas en haut (la dernière ligne dit *quoi*, les
   précédentes disent *où*).
4. **La technique du canard en plastique** : explique ton code à voix haute (à un canard, un
   mur, un ami). Si tu n'arrives pas à l'expliquer, tu ne l'as pas compris.

🤔 **Pourquoi** : un ingénieur n'est pas quelqu'un qui *connaît* tout, c'est quelqu'un qui sait
**apprendre vite** et **diagnostiquer**. C'est cette compétence qu'on construit ici.

✍️ **Exercice** : prends n'importe quel fichier de NovaBank, ouvre-le, et explique à voix haute
ce qu'il fait, ligne par ligne. Note les mots que tu ne comprends pas → ce sont tes prochains
objectifs.

---

## Module 1 — Le terminal et la ligne de commande

🎯 **Objectif** : être à l'aise avec la ligne de commande (indispensable pour tout le reste).

📚 **Cours.** Le **terminal** (ou *console*, *shell*) est une interface où tu **tapes** des
commandes au lieu de cliquer. C'est plus rapide, automatisable, et c'est **le** langage commun
des serveurs.

Les commandes vitales :
```bash
pwd                 # où suis-je ? (print working directory)
ls                  # lister les fichiers (dir sous cmd Windows)
cd dossier          # entrer dans un dossier (cd .. pour remonter)
mkdir mon_dossier   # créer un dossier
cat fichier.txt     # afficher le contenu d'un fichier
cp a.txt b.txt      # copier
mv a.txt b.txt      # déplacer / renommer
rm fichier          # supprimer (⚠️ définitif, pas de corbeille)
```

Notions clés :
- **Chemin absolu** (`C:/Users/elmeh/projet`) vs **relatif** (`./backend`, `../docs`).
- Le **pipe** `|` envoie la sortie d'une commande dans une autre : `ls | grep test`.
- La **redirection** `>` écrit dans un fichier : `echo bonjour > note.txt`.
- **Variables d'environnement** : des valeurs disponibles pour les programmes (`PATH`,
  `DATABASE_URL`).

🏦 **Dans NovaBank** : tout se lance en ligne de commande (`docker compose up -d`,
`pytest`, `npm run build`). Les scripts `demarrer.bat` / `.sh` sont des suites de commandes.

✍️ **Exercices** : (1) crée un dossier, entre dedans, crée un fichier, affiche-le, supprime-le,
sans jamais toucher la souris. (2) Ouvre le fichier `demarrer.sh` de NovaBank et explique
chaque commande.

🔗 **Ressources** : « The Missing Semester of Your CS Education » (MIT, gratuit) — le meilleur
cours sur le terminal, l'outillage et Git. Chercher : *MIT Missing Semester*.

---

## Module 2 — Git et GitHub

🎯 **Objectif** : versionner ton code, ne jamais rien perdre, travailler en équipe.

📚 **Cours.** **Git** enregistre l'**historique** de ton projet. Le cycle de base :
```bash
git init                       # créer un dépôt
git status                     # que s'est-il passé ?
git add fichier.py             # préparer (stage) les changements
git commit -m "feat: ajoute X" # enregistrer une "photo" avec un message
git log --oneline              # voir l'historique
```
Travailler avec GitHub (le serveur distant) :
```bash
git remote add origin <url>    # relier au dépôt distant
git push origin master         # envoyer ses commits
git pull                       # récupérer ceux des autres
git clone <url>                # copier un projet existant
```
Les branches (travailler sans casser le stable) :
```bash
git switch -c feat/ma-feature  # créer et aller sur une branche
git switch master              # revenir
git merge feat/ma-feature      # fusionner
```

**Bonnes pratiques** :
- Un commit = **une idée**. Message clair, format *conventional commits* : `feat:` (nouveauté),
  `fix:` (correction), `docs:`, `test:`, `refactor:`.
- Ne **jamais** committer de secrets (mots de passe, jetons) → `.gitignore`.

🤔 **Pourquoi** : sans Git, une erreur = perte de travail. Avec Git, tu reviens en arrière, tu
compares, tu collabores. Et l'historique **raconte** les décisions.

🏦 **Dans NovaBank** : historique en commits conventionnels, `.gitignore` protège le `.env`,
`.gitattributes` gère les fins de ligne (CRLF pour `.bat`).

✍️ **Exercices** : (1) crée un dépôt local, fais 3 commits, consulte `git log`. (2) Crée une
branche, modifie un fichier, fusionne. (3) Casse volontairement un fichier puis récupère la
version précédente avec `git restore`.

🔗 **Ressources** : le livre **Pro Git** (gratuit, officiel, en français sur git-scm.com/book/fr) ;
documentation GitHub (docs.github.com).

---

# PARTIE II — LES LANGAGES

## Module 3 — Python

🎯 **Objectif** : écrire du Python propre et comprendre tout le backend de NovaBank.

📚 **Cours — les fondamentaux.**
```python
# Variables et types
nom = "Amina"                 # str (chaîne)
age = 23                      # int (entier)
solde = 1500.50               # float (⚠️ jamais pour l'argent !)
actif = True                  # bool
rien = None                   # absence de valeur

# Structures de données
liste = [1, 2, 3]                       # ordonnée, modifiable
tuple_ = (1, 2)                         # ordonnée, NON modifiable
dico = {"cin": "AB123", "age": 23}      # clé → valeur
ensemble = {1, 2, 3}                    # valeurs uniques

# Conditions
if solde > 1000:
    print("riche")
elif solde > 0:
    print("ok")
else:
    print("vide")

# Boucles
for x in liste:
    print(x)

# Fonctions (avec annotations de type)
def calculer_ratio(montant: float, revenu: float) -> float:
    """Docstring : explique ce que fait la fonction."""
    if revenu <= 0:
        return 0.0
    return montant / revenu
```

**Notions intermédiaires indispensables** :
- **Classe et objet** : une classe est un *moule*, un objet une *instance*.
  ```python
  class Client:
      def __init__(self, nom: str):   # constructeur
          self.nom = nom              # attribut
      def saluer(self) -> str:        # méthode
          return f"Bonjour {self.nom}"
  ```
- **Exceptions** : gérer les erreurs sans planter.
  ```python
  try:
      risque = 100 / 0
  except ZeroDivisionError as e:
      print("erreur :", e)
  finally:
      print("toujours exécuté")
  ```
- **Modules et imports** : `from app.services import audit_service`.
- **Environnement virtuel (venv)** : un dossier isolé avec les dépendances du projet, pour ne
  pas polluer le système.
  ```bash
  python -m venv venv
  venv\Scripts\activate        # Windows
  pip install -r requirements.txt
  ```
- **Decimal** : pour l'argent. `from decimal import Decimal; Decimal("10.50")`.
- **Type hints** : `montant: Decimal`, `nom: str | None` — documentent ET sécurisent.
- **f-strings** : `f"Score {score}/100"`.
- **Dataclass** : une classe « conteneur de données » sans code répétitif.
  ```python
  from dataclasses import dataclass
  @dataclass
  class TransactionFeatures:
      amount_over_income: float
      is_night: int
  ```

🤔 **Pourquoi Python** : lisible, immense écosystème (surtout en IA), rapide à écrire.

🏦 **Dans NovaBank** : tout le backend + l'IA. Les *dataclasses* portent les features ML, les
*type hints* documentent chaque fonction, `Decimal` protège les montants.

✍️ **Exercices** : (1) écris une fonction `est_nocturne(heure)` qui renvoie True entre 0 et 6.
(2) Crée une classe `Compte` avec un solde, une méthode `deposer` et une méthode `retirer` qui
lève une exception si le solde est insuffisant. (3) Réécris `explain_features` de NovaBank de
mémoire, puis compare.

🔗 **Ressources** : documentation officielle **docs.python.org/fr** (tutoriel officiel) ;
« Automate the Boring Stuff with Python » (gratuit en ligne) ; « Real Python » (articles de
qualité).

---

## Module 4 — SQL et les bases de données relationnelles

🎯 **Objectif** : concevoir un schéma correct et savoir interroger une base.

📚 **Cours — le modèle relationnel.** Une **base relationnelle** stocke les données dans des
**tables** (lignes/colonnes) **reliées** entre elles.

Vocabulaire :
- **Clé primaire** (*primary key*) : identifiant unique d'une ligne (`id`).
- **Clé étrangère** (*foreign key*) : référence vers une autre table (`client_id`).
- **Contrainte** : règle appliquée par la base (`UNIQUE`, `NOT NULL`, `CHECK`).
- **Index** : structure qui accélère les recherches (comme l'index d'un livre).
- **Relation 1-N** : un client a *plusieurs* comptes. **N-N** : nécessite une table de liaison.

**Le SQL en 6 commandes** :
```sql
-- Lire
SELECT first_name, cin FROM clients WHERE monthly_income > 5000 ORDER BY id LIMIT 10;

-- Insérer
INSERT INTO clients (first_name, cin) VALUES ('Amina', 'AB123456');

-- Modifier
UPDATE accounts SET balance = balance - 500 WHERE id = 3;

-- Supprimer
DELETE FROM clients WHERE id = 7;

-- Joindre deux tables
SELECT c.first_name, a.balance
FROM clients c
JOIN accounts a ON a.client_id = c.id;

-- Agréger
SELECT transaction_type, COUNT(*), SUM(amount)
FROM transactions
GROUP BY transaction_type;
```

**La normalisation** (éviter la redondance) : ne stocke jamais deux fois la même information.
Le nom du client vit dans `clients`, pas répété dans chaque `transaction` — sinon, le jour où il
change, tu as des incohérences.

🤔 **Pourquoi PostgreSQL** : robuste, gratuit, standard entreprise, gère les **verrous** et les
**transactions** dont une banque a besoin.

🏦 **Dans NovaBank** : 8 tables (`users`, `clients`, `accounts`, `transactions`, `risk_scores`,
`alerts`, `audit_logs`, `app_settings`). Voir `docs/base_de_donnees.md` et
`docs/schema_cible.sql`.

✍️ **Exercices** : (1) dessine sur papier les 8 tables et leurs relations. (2) Écris la requête
SQL qui donne le nombre de transactions par client. (3) Connecte-toi à la base de NovaBank
(`docker exec -it <postgres> psql -U postgres -d novabank`) et explore avec `\dt`, `\d clients`,
puis fais des `SELECT`.

🔗 **Ressources** : documentation **postgresql.org/docs** ; « SQLBolt » (exercices interactifs
gratuits) ; « Use The Index, Luke » (pour les index et la performance).

---

## Module 5 — HTML et CSS

🎯 **Objectif** : comprendre la structure et l'apparence d'une page web.

📚 **Cours.**
- **HTML** = la **structure** (le squelette) :
  ```html
  <div class="carte">
    <h1>Titre</h1>
    <p>Un paragraphe</p>
    <button>Valider</button>
  </div>
  ```
  Notions : **balise**, **attribut** (`class`, `id`), **arbre DOM** (la page est un arbre
  d'éléments), **sémantique** (`<header>`, `<main>`, `<nav>` : utiliser la bonne balise aide
  l'accessibilité et le référencement).
- **CSS** = l'**apparence** :
  ```css
  .carte { display: flex; gap: 8px; color: #1F2427; }
  ```
  Notions clés : **sélecteur**, **box model** (marge → bordure → padding → contenu),
  **Flexbox** et **Grid** (mise en page moderne), **responsive** (`@media`), **variables CSS**
  (`--primary`).

**Tailwind CSS** (utilisé dans NovaBank) : au lieu d'écrire du CSS séparé, on compose des
**classes utilitaires** directement dans le HTML :
```html
<div class="flex gap-2 rounded-lg bg-card p-4 text-sm">…</div>
```
🤔 **Pourquoi Tailwind** : rapidité, cohérence (une échelle de tailles/couleurs), pas de
fichiers CSS qui grossissent sans fin, et le style est **visible à côté du composant**.

🏦 **Dans NovaBank** : Tailwind partout + un système de design dans `styles/index.css`
(couleurs orange Attijari, thème clair/sombre via variables CSS).

✍️ **Exercices** : (1) reproduis une carte KPI de NovaBank en HTML/CSS pur. (2) Refais-la en
Tailwind. (3) Rends-la responsive (une colonne sur mobile, trois sur desktop).

🔗 **Ressources** : **MDN Web Docs** (developer.mozilla.org) — LA référence HTML/CSS ;
**tailwindcss.com/docs** ; « Flexbox Froggy » et « Grid Garden » (jeux pour apprendre).

---

## Module 6 — JavaScript puis TypeScript

🎯 **Objectif** : maîtriser le langage du navigateur, avec un filet de sécurité.

📚 **Cours — JavaScript (JS).**
```js
const nom = "Amina";           // constante
let compteur = 0;              // variable modifiable
const carre = (x) => x * x;    // fonction fléchée

const liste = [1, 2, 3];
liste.map(x => x * 2);         // [2,4,6] — transforme
liste.filter(x => x > 1);      // [2,3]   — sélectionne
liste.find(x => x === 2);      // 2       — cherche

const client = { nom: "Amina", cin: "AB1" };
const { nom: n } = client;     // déstructuration
const copie = { ...client, actif: true };  // spread
```
**Asynchrone** (essentiel pour appeler une API) : une requête réseau prend du temps ; JS ne
bloque pas, il **promet** un résultat plus tard.
```js
async function charger() {
  const reponse = await fetch("/api/clients");  // attend sans bloquer
  const donnees = await reponse.json();
  return donnees;
}
```

📚 **Cours — TypeScript (TS).** TS = JS + **types** :
```ts
interface Client {
  id: number;
  first_name: string;
  monthly_income: string | null;   // peut être absent
}

function afficher(c: Client): string {
  return `${c.first_name} (#${c.id})`;
}
```
Notions : **interface/type**, **union** (`"a" | "b"`), **optionnel** (`nom?: string`),
**générique** (`Array<Client>`), **strict mode** (le compilateur refuse les approximations).

🤔 **Pourquoi TypeScript** : en JS, une faute de frappe (`client.frist_name`) devient un bug
**chez l'utilisateur**. En TS, l'erreur apparaît **immédiatement** à l'écriture. C'est un
énorme gain de fiabilité sur un projet qui grandit.

🏦 **Dans NovaBank** : `frontend/src/api/types.ts` définit les types **miroirs** des schémas
Pydantic du backend. Le build échoue si les deux divergent.

✍️ **Exercices** : (1) écris une fonction TS qui prend une liste de clients et renvoie ceux dont
le revenu dépasse X. (2) Ajoute volontairement une faute de frappe sur un champ et observe
l'erreur TypeScript. (3) Écris l'interface TS correspondant au schéma `AlertResponse` du backend.

🔗 **Ressources** : **MDN** (JavaScript) ; **typescriptlang.org/docs** (handbook officiel) ;
« JavaScript.info » (excellent cours progressif gratuit).

---

# PARTIE III — LE BACKEND

## Module 7 — HTTP et les API REST

🎯 **Objectif** : comprendre comment deux programmes se parlent sur le réseau.

📚 **Cours.** (Détail dans [APPRENDRE_DE_ZERO.md](APPRENDRE_DE_ZERO.md) Partie 1.)
- **Requête** = méthode (`GET`/`POST`/`PATCH`/`DELETE`) + URL + en-têtes + corps (JSON).
- **Réponse** = code de statut + corps.
- **Codes** : 200 OK · 201 Créé · 400 requête métier refusée · 401 non authentifié ·
  403 interdit · 404 introuvable · 409 conflit · 422 données invalides · 500 erreur serveur.
- **REST** : chaque **ressource** a une URL, on agit avec les méthodes HTTP, le serveur est
  **stateless** (ne retient rien entre deux requêtes).
- **Idempotence** : `GET` et `DELETE` peuvent être rejoués sans effet supplémentaire ; `POST`
  non (il crée à chaque fois).

🏦 **Dans NovaBank** : ~30 endpoints. Exemples : `POST /transactions` (créer une opération),
`GET /alerts` (lister), `PATCH /alerts/{id}` (qualifier), `POST /clients/{id}/risk-profile/approve`.

✍️ **Exercices** : (1) ouvre `http://localhost:8000/docs` (Swagger) et exécute chaque endpoint.
(2) Pour chaque endpoint, devine le code de statut attendu avant de cliquer. (3) Provoque
volontairement un 401, un 403, un 404, un 409 et un 422.

🔗 **Ressources** : **MDN — HTTP** ; « REST API Tutorial » (restfulapi.net).

---

## Module 8 — FastAPI

🎯 **Objectif** : construire une API Python moderne, validée et documentée.

📚 **Cours.**
```python
from fastapi import FastAPI, Depends, HTTPException, status

app = FastAPI(title="NovaBank API")

@app.get("/clients/{client_id}")
def get_client(client_id: int, db = Depends(get_db)):
    client = db.get(Client, client_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Introuvable")
    return client
```
Notions :
- **Décorateur** (`@app.get(...)`) : associe une fonction à une URL + méthode.
- **Paramètre de chemin** (`{client_id}`) et **de requête** (`?search=amina`).
- **`response_model`** : le schéma de sortie (filtre ce qui sort — sécurité).
- **`Depends` (injection de dépendances)** : FastAPI fournit automatiquement la session base,
  l'utilisateur connecté, la vérification de rôle.
- **Router** : regrouper les endpoints par domaine (`APIRouter(prefix="/clients")`).
- **Swagger auto** : `/docs` génère une documentation **interactive** depuis ton code.

🤔 **Pourquoi FastAPI** (vs Flask/Django) : validation forte intégrée (Pydantic), documentation
automatique, très performant, et Python → l'IA s'intègre naturellement. Flask est plus minimal
(tout à ajouter à la main), Django plus lourd pour une API pure.

🏦 **Dans NovaBank** : `app/main.py` assemble 11 routers ; `app/core/deps.py` contient
`get_current_user` et `require_role` (le RBAC).

✍️ **Exercices** : (1) crée une mini-API FastAPI avec 2 endpoints (`GET /ping`, `POST /echo`).
(2) Ajoute une dépendance qui refuse la requête si un en-tête `X-Token` est absent.
(3) Lis `app/routers/clients.py` de NovaBank et explique chaque décorateur.

🔗 **Ressources** : **fastapi.tiangolo.com** — le tutoriel officiel est excellent et progressif
(fais-le en entier, c'est ~1 semaine).

---

## Module 9 — SQLAlchemy (ORM) et Alembic (migrations)

🎯 **Objectif** : manipuler la base en Python, et faire évoluer le schéma proprement.

📚 **Cours — l'ORM.**
```python
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Client(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(primary_key=True)
    cin: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    monthly_income: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
```
Utilisation :
```python
db.add(client)                 # préparer un INSERT
db.flush()                     # envoyer à la base sans valider
db.commit()                    # valider définitivement
db.get(Client, 42)             # SELECT par clé primaire
db.scalars(select(Client).where(Client.cin == "AB1")).all()
```
Notions : **session** (l'espace de travail d'une requête), **relation** (`relationship`,
navigation objet `client.accounts`), **lazy loading** vs **eager loading** (`selectinload`)
et le **problème N+1** (1 requête + N requêtes au lieu d'1 seule → lent).

📚 **Cours — Alembic (migrations).**
```bash
alembic revision -m "add risk profile"   # créer une migration
alembic upgrade head                     # appliquer
alembic downgrade -1                     # revenir en arrière
```
Une migration décrit **ce qui change** (`op.add_column(...)`) et **comment revenir**
(`op.drop_column(...)`).

🤔 **Pourquoi un ORM** : on écrit du Python (lisible), on est **protégé de l'injection SQL**, et
le code reste portable. ⚠️ Mais il faut **connaître le SQL derrière** : un ORM mal utilisé génère
des requêtes catastrophiques (N+1).

🏦 **Dans NovaBank** : les **modèles sont la source de vérité** du schéma ; Alembic versionne les
6 évolutions (resolution → shap_values → contacts → app_settings → profil de risque → workflow).

✍️ **Exercices** : (1) ajoute une colonne `nationalite` au modèle `Client` et écris la migration.
(2) Écris une requête SQLAlchemy qui compte les transactions par type. (3) Active
`echo=True` sur l'engine et **observe le SQL généré** — c'est très instructif.

🔗 **Ressources** : **docs.sqlalchemy.org** (tutoriel 2.0) ; **alembic.sqlalchemy.org**.

---

## Module 10 — Pydantic et la validation

🎯 **Objectif** : ne jamais laisser entrer une donnée invalide.

📚 **Cours.**
```python
from pydantic import BaseModel, Field, ConfigDict

class ClientCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    cin: str = Field(pattern=r"^[A-Za-z]{1,2}\d{1,8}$")
    monthly_income: Decimal | None = Field(default=None, ge=0)

class ClientResponse(ClientCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)  # lire depuis un objet ORM
```
Notions : **validation déclarative** (la règle vit dans le schéma, pas éparpillée),
**contraintes** (`ge`, `min_length`, `pattern`), **from_attributes** (pont ORM → Pydantic),
et la distinction **Create / Update / Response**.

🤔 **Pourquoi séparer modèle (ORM) et schéma (API)** — 3 raisons à savoir par cœur :
1. **Sécurité** : le modèle `User` contient `password_hash` ; le schéma de sortie garantit qu'il
   **ne sort jamais**.
2. **Découplage** : renommer une colonne ne casse pas le frontend.
3. **Validation** : on rejette à la porte, avec un 422 explicite.

Cela protège aussi du **mass assignment** (un client HTTP qui enverrait `is_admin: true`).

🏦 **Dans NovaBank** : un trio Create/Update/Response par entité, plus `RiskProfileUpdate` (avec
motif obligatoire) et `ModelHealthResponse`.

✍️ **Exercices** : (1) essaie de créer un client avec un CIN invalide → observe le 422 détaillé.
(2) Ajoute un champ interdit dans le corps JSON → constate qu'il est ignoré. (3) Écris un schéma
`VirementCreate` avec montant > 0 et deux comptes différents.

🔗 **Ressources** : **docs.pydantic.dev**.

---

## Module 11 — La sécurité applicative

🎯 **Objectif** : construire une application qu'on peut confier à une banque.

📚 **Cours.**
1. **Hachage des mots de passe** — jamais de stockage en clair. Fonction **à sens unique** +
   **sel** aléatoire. **bcrypt** est volontairement **lent** (résiste au brute-force).
   ```python
   hash_ = hash_password("MonMotDePasse")   # à l'inscription
   verify_password("MonMotDePasse", hash_)  # à la connexion
   ```
2. **JWT (JSON Web Token)** — un « badge » signé : `en-tête.charge_utile.signature`. Le serveur
   **vérifie la signature** sans base de données (*stateless*). Contient l'identité et le rôle,
   **jamais** de secret (il est lisible !). Bonnes pratiques : **durée courte**, un **refresh
   token** séparé, **vérifier le type** du jeton, **refuser l'algorithme `none`**.
3. **RBAC** — droits par rôle, vérifiés **côté serveur à chaque requête**. Cacher un bouton ne
   protège rien : un attaquant appelle l'API directement.
4. **OWASP API Security Top 10** — la liste des failles à connaître : autorisation cassée au
   niveau objet (BOLA/IDOR : accéder à l'objet d'un autre en changeant l'id !), authentification
   cassée, exposition excessive de données, absence de limitation de débit, mauvaise
   configuration…
5. **Autres réflexes** : anti-force brute (verrouillage après N échecs), messages d'erreur
   **non révélateurs** (anti-énumération), **journal d'audit** append-only, secrets dans `.env`
   **jamais versionné**, HTTPS en production.

🏦 **Dans NovaBank** : bcrypt, JWT access+refresh, `require_role`, verrouillage après 5 échecs,
audit inviolable, et la règle **« l'IA assiste, l'humain décide »** sur les actions sensibles.

✍️ **Exercices** : (1) connecte-toi, copie ton JWT et décode-le (site jwt.io) → observe qu'il est
**lisible** (donc : jamais de secret dedans). (2) Tente d'appeler `/analytics/kpi` avec un jeton
de conseiller → 403. (3) Fais 5 tentatives de connexion ratées → observe le verrouillage.

🔗 **Ressources** : **owasp.org** (API Security Top 10, Cheat Sheet Series) ; **jwt.io**.

---

## Module 12 — Transactions, ACID et concurrence

🎯 **Objectif** : garantir qu'un virement ne corrompt jamais un solde.

📚 **Cours.**
- Une **transaction** groupe des opérations en **tout-ou-rien**.
- **ACID** : **A**tomicité, **C**ohérence, **I**solation, **D**urabilité.
- **Le problème (*lost update*)** : deux virements simultanés lisent le même solde (1000),
  calculent chacun de leur côté, écrivent → l'un **écrase** l'autre → solde faux.
- **La solution : le verrou pessimiste**
  ```python
  account = db.get(Account, id, with_for_update=True)   # SELECT ... FOR UPDATE
  ```
  La ligne est **verrouillée** jusqu'au commit ; l'autre transaction **attend**.
- **Le deadlock (interblocage)** : A verrouille 1 puis attend 2 ; B verrouille 2 puis attend 1 →
  blocage éternel. **Parade** : verrouiller **toujours dans le même ordre** (ici par id
  croissant) — un ordre global unique **brise le cycle**.
- **Niveaux d'isolation** (culture générale) : *read committed* (défaut PostgreSQL),
  *repeatable read*, *serializable* — plus c'est strict, plus c'est sûr mais lent.

🏦 **Dans NovaBank** : `transaction_service.py` — verrou + ordre par id + un **seul commit** pour
la transaction, le score, l'alerte et l'audit. C'est **l'argument technique le plus fort** du
projet pour un jury.

✍️ **Exercices** : (1) explique à voix haute pourquoi l'ordre de verrouillage évite le deadlock.
(2) Lis `transaction_service.py` et identifie où commence et finit la transaction. (3) Réfléchis :
que se passerait-il si on retirait `with_for_update` ?

🔗 **Ressources** : documentation **PostgreSQL — Concurrency Control** (chapitre 13) ; « Designing
Data-Intensive Applications » (M. Kleppmann) pour aller loin.

---

# PARTIE IV — LE FRONTEND

## Module 13 — React

🎯 **Objectif** : construire une interface avec des composants.

📚 **Cours.**
```tsx
import { useState, useEffect } from "react";

function ListeClients() {
  const [clients, setClients] = useState<Client[]>([]);   // état
  const [chargement, setChargement] = useState(true);

  useEffect(() => {                                        // effet au montage
    api.get("/clients").then(({ data }) => {
      setClients(data);
      setChargement(false);
    });
  }, []);                                                  // [] = une seule fois

  if (chargement) return <Skeleton />;
  return (
    <ul>
      {clients.map((c) => <li key={c.id}>{c.first_name}</li>)}
    </ul>
  );
}
```
Notions essentielles :
- **Composant** = une fonction qui renvoie du **JSX** (du HTML dans du JS).
- **État (`useState`)** : quand il change, React **re-dessine** le composant.
- **Props** : les paramètres d'un composant (`<ScoreBadge score={80} />`).
- **`useEffect`** : exécuter du code après le rendu (charger des données). Le **tableau de
  dépendances** contrôle *quand* il se relance.
- **`key`** dans une liste : aide React à identifier chaque élément (ne jamais l'oublier).
- **Rendu conditionnel** : `{isDirector && <Bouton />}`.
- **Contexte (`useContext`)** : partager un état global (utilisateur connecté, thème) sans le
  passer de composant en composant.
- **Hooks personnalisés** : factoriser une logique réutilisable.

🤔 **Pourquoi React** : composants réutilisables → cohérence et moins de code ; l'interface est
une **fonction de l'état** (tu décris *quoi* afficher, pas *comment* manipuler le DOM).

🏦 **Dans NovaBank** : 15 écrans, des composants `ui/` (boutons, cartes), `layout/` (sidebar,
bottom nav mobile), `shared/` (KpiCard, ScoreBadge, ShapChart), et 3 contextes (Auth, Thème,
Toasts).

✍️ **Exercices** : (1) crée un composant `Compteur` avec un bouton +1. (2) Crée un composant
`ScoreBadge` qui affiche un score avec une couleur selon sa valeur. (3) Charge la liste des
clients depuis l'API et affiche-la, avec un état de chargement.

🔗 **Ressources** : **react.dev/learn** — la nouvelle documentation officielle est excellente
(fais tout le tutoriel « Thinking in React »).

---

## Module 14 — Le frontend en pratique : routing, appels API, formulaires

🎯 **Objectif** : assembler une vraie application, pas juste des composants.

📚 **Cours.**
- **Routing** (React Router) : associer une URL à un écran, avec des **gardes** de rôle.
  ```tsx
  <Route path="/fraude" element={<Guard roles={["director"]}><Fraud /></Guard>} />
  ```
  ⚠️ Une garde frontend est du **confort**, pas de la sécurité : le vrai contrôle est serveur.
- **Appels API** (axios) : un **intercepteur** ajoute automatiquement le jeton JWT à chaque
  requête et **renouvelle** le jeton expiré de façon transparente.
- **Formulaires contrôlés** : la valeur du champ vient de l'état React.
  ```tsx
  <input value={form.cin} onChange={(e) => setForm({ ...form, cin: e.target.value })} />
  ```
- **Gestion des erreurs** : afficher un message utile (`try/catch` + toast).
- **Build** (Vite) : compile TS/React en JS optimisé, avec des noms **hashés** pour le cache.
- **PWA** : `manifest` + `service worker` pour rendre l'app **installable** sur mobile.
  ⚠️ Dans une app bancaire, **ne jamais mettre l'API en cache** (données périmées = danger).

🏦 **Dans NovaBank** : `api/client.ts` (axios + refresh auto), `App.tsx` (routes + gardes),
`contexts/` (état global), `public/sw.js` (service worker passif, zéro cache).

✍️ **Exercices** : (1) ajoute une page « À propos » avec sa route. (2) Ajoute un champ au
formulaire de création de client. (3) Provoque une erreur API et vérifie que le message
s'affiche proprement.

🔗 **Ressources** : **reactrouter.com** ; **axios-http.com** ; **vitejs.dev** ;
**web.dev** (section PWA).

---

# PARTIE V — L'INTELLIGENCE ARTIFICIELLE

## Module 15 — Les bases du Machine Learning

🎯 **Objectif** : comprendre ce qu'est (et n'est pas) l'apprentissage automatique.

📚 **Cours.**
- **ML** = apprendre des **règles à partir d'exemples**, au lieu de les écrire.
- **Supervisé** : on a des exemples **étiquetés** (fraude / normal) → classification ou
  régression. **Non supervisé** : pas d'étiquettes → détection d'anomalies, clustering.
- **Le vocabulaire** :
  - **Feature** (caractéristique) : un signal numérique en entrée.
  - **Label** (étiquette) : la réponse attendue.
  - **Entraînement** : le modèle ajuste ses paramètres sur des exemples.
  - **Inférence** (prédiction) : utiliser le modèle sur une donnée nouvelle.
  - **Jeu d'entraînement / de test** : on évalue sur des données **jamais vues**.
  - **Sur-apprentissage (*overfitting*)** : le modèle « apprend par cœur » et généralise mal.
    Symptôme : excellent en entraînement, mauvais en test.
  - **Sous-apprentissage (*underfitting*)** : le modèle est trop simple.
- **Le pipeline ML** : données → features → entraînement → évaluation → déploiement →
  surveillance.

🤔 **Le point crucial** : le ML n'est **pas magique**. La **qualité des features et des données**
compte plus que le choix du modèle. (NovaBank en a fait l'expérience deux fois — voir Module 19.)

✍️ **Exercices** : (1) explique la différence entre entraînement et inférence. (2) Donne un
exemple d'overfitting dans la vie réelle. (3) Liste les 7 features de NovaBank et dis quel
schéma de fraude chacune vise.

🔗 **Ressources** : **scikit-learn.org** (« User Guide », section *Supervised learning ») ;
« Machine Learning » d'Andrew Ng (Coursera, référence historique) ; « Hands-On Machine Learning »
(A. Géron) — le meilleur livre pratique.

---

## Module 16 — scikit-learn et le Random Forest

🎯 **Objectif** : entraîner un vrai modèle et comprendre ce qu'il fait.

📚 **Cours.**
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=42
)
model = RandomForestClassifier(
    n_estimators=300, max_depth=10, class_weight="balanced", random_state=42
)
model.fit(X_train, y_train)          # entraînement
proba = model.predict_proba(X_test)  # probabilité de fraude
```
Notions :
- **Arbre de décision** : une suite de questions (« montant/revenu > 2 ? »). Simple mais
  instable.
- **Random Forest** : des **centaines d'arbres** entraînés sur des sous-échantillons ; ils
  **votent**. → robuste, peu sensible au sur-apprentissage.
- **Hyperparamètres** : `n_estimators` (nombre d'arbres), `max_depth` (profondeur) —
  se règlent, ce ne sont pas des paramètres appris.
- **`stratify=y`** : garde la même proportion de fraudes dans train et test (essentiel quand
  c'est déséquilibré).
- **`class_weight="balanced"`** : compense le déséquilibre **sans** rééchantillonner
  artificiellement.
- **`random_state`** : fixe l'aléatoire → **résultats reproductibles** (indispensable en science).
- **Importance des variables** : quelle feature pèse le plus (`feature_importances_`).
- **Persistance** : `joblib.dump(model, "model.joblib")` → un **artefact** réutilisable.

🏦 **Dans NovaBank** : `scripts/train_model.py` compare Random Forest, Isolation Forest et la
baseline de règles ; l'artefact est entraîné **au build de l'image Docker**.

✍️ **Exercices** : (1) entraîne un Random Forest sur un jeu simple (iris de scikit-learn).
(2) Fais varier `max_depth` et observe l'effet. (3) Lance `python -m scripts.train_model` sur
NovaBank et lis `metrics.json`.

🔗 **Ressources** : **scikit-learn.org/stable/user_guide.html** ; le tutoriel officiel
« An introduction to machine learning with scikit-learn ».

---

## Module 17 — Évaluer honnêtement (données déséquilibrées)

🎯 **Objectif** : ne jamais publier un chiffre trompeur. **C'est le module le plus important
pour ton jury.**

📚 **Cours.**
- **Matrice de confusion** : VP (vrais positifs), FP (faux positifs), VN, FN (fraudes ratées).
- **Exactitude (accuracy)** = (VP+VN)/tout → **TROMPEUSE** quand une classe est rare : avec
  1,5 % de fraudes, un modèle qui ne détecte **rien** obtient **98,5 %**.
- **Précision** = VP/(VP+FP) → *parmi mes alertes, combien sont justes ?* (coût : temps perdu)
- **Rappel (recall)** = VP/(VP+FN) → *parmi les fraudes, combien j'attrape ?* (coût : argent perdu)
- **F1** = moyenne harmonique précision/rappel (l'équilibre).
- **AUC-PR** (aire sous la courbe précision-rappel) → **la** métrique des problèmes déséquilibrés.
- **Le compromis** : baisser le seuil → plus de rappel, moins de précision. C'est un **choix
  métier**, pas technique ! (D'où le seuil configurable par le directeur dans NovaBank.)
- **Baseline** : toujours comparer à une solution simple (ici, le moteur de règles). Un modèle
  qui ne bat pas la baseline ne sert à rien.

🏦 **Dans NovaBank** : RF **F1 0,58 / AUC-PR 0,61 / précision 0,77** contre **F1 0,31** pour la
baseline. Valeurs **modérées et assumées** — on a introduit un chevauchement volontaire entre
classes pour ne pas produire de métriques irréalistes.

✍️ **Exercices** : (1) calcule à la main précision/rappel/F1 à partir d'une matrice de confusion.
(2) Explique pourquoi l'accuracy est inutile ici. (3) Prépare ta réponse à : *« vos chiffres ne
sont pas très élevés, pourquoi ? »*

🔗 **Ressources** : scikit-learn — « Metrics and scoring » ; chercher *precision-recall curve
imbalanced data*.

---

## Module 18 — L'explicabilité (SHAP / XAI)

🎯 **Objectif** : rendre une décision d'IA compréhensible et défendable.

📚 **Cours.**
- **Pourquoi** : en banque, une décision inexpliquée est **inutilisable** (responsabilité du
  décideur, droit du client, exigences **RGPD** et **EU AI Act**).
- **SHAP** (*SHapley Additive exPlanations*) : issu de la **théorie des jeux** (valeurs de
  Shapley). Il répartit la prédiction entre les variables : chaque feature reçoit une
  **contribution** positive (pousse vers la fraude) ou négative.
  ```python
  import shap
  explainer = shap.TreeExplainer(model)   # rapide et exact pour les arbres
  values = explainer.shap_values(X)
  ```
- **Global vs local** : l'importance des variables est **globale** (le modèle en général) ;
  SHAP est **local** (cette décision précise) — c'est ce dont le directeur a besoin.
- **Alternative** : LIME (approximation locale). SHAP est préféré pour les modèles d'arbres.

🏦 **Dans NovaBank** : SHAP calculé à chaque score, **stocké** en base (`risk_scores.shap_values`)
et **affiché** en barres bidirectionnelles ; repris dans le **dossier de déclaration de soupçon**
avec des libellés lisibles par un juriste.

✍️ **Exercices** : (1) crée une opération suspecte et lis le graphique SHAP : quelle variable
domine ? (2) Explique en une phrase, à quelqu'un de non technique, pourquoi le score est élevé.

🔗 **Ressources** : **shap.readthedocs.io** ; « Interpretable Machine Learning » (C. Molnar,
livre gratuit en ligne) — la référence sur le sujet.

---

## Module 19 — MLOps : faire vivre un modèle en production

🎯 **Objectif** : comprendre que livrer un modèle n'est **pas** la fin du travail.

📚 **Cours.**
- **Dérive (drift)** : le monde change (les fraudeurs s'adaptent) → le modèle se **dégrade**.
  *Data drift* (les entrées changent) vs *concept drift* (la relation entrée→sortie change).
- **Surveillance en production** : mesurer la performance **réelle** (pas celle du jeu de test).
- **Human-in-the-loop** : les décisions des experts deviennent les **étiquettes** du prochain
  entraînement.
- **Versionner le modèle** (`model_version`) : savoir **quel** modèle a produit **quelle**
  décision → auditabilité.
- **Reproductibilité** : graine aléatoire fixée, dépendances épinglées, artefact + métriques
  sauvegardés.
- **⚠️ Le piège n°1 : le *training/serving skew*** — tout écart entre l'entraînement et la
  production. Deux formes :
  1. **Code différent** → parade : **partager** le code d'extraction des features.
  2. **Données incohérentes** → NovaBank l'a vécu : le générateur produisait des combinaisons
     **physiquement impossibles** (cumul 72 h inférieur au montant courant) → les vraies
     transactions tombaient **hors distribution** → un retrait de 13× le revenu ne scorait que
     49/100 ! Après correction : 80/100.
  3. **Fuite temporelle** (*data leakage*) → NovaBank l'a vécu aussi : au réentraînement, on
     recalculait les features d'une transaction **déjà en base**, donc l'historique la contenait
     elle-même (et le futur !) → étiquettes faussées. Parade : **rejeu point-in-time**.

> 🧠 **La leçon à retenir de tout le projet** : *la qualité des données prime sur la
> sophistication du modèle.*

🏦 **Dans NovaBank** : page « Santé du modèle » (précision réelle, faux positifs, histogramme,
volume de feedback), règle de réentraînement (≥ 50 étiquettes ou précision < 50 %).

✍️ **Exercices** : (1) qualifie 3 alertes et observe l'évolution de la page Santé du modèle.
(2) Explique le *training/serving skew* avec tes propres mots. (3) Cite les 2 bugs vécus par le
projet et leur correction.

🔗 **Ressources** : « Machine Learning Engineering » (A. Burkov) ; « Designing Machine Learning
Systems » (Chip Huyen) ; Google — *Rules of Machine Learning* (guide gratuit).

---

# PARTIE VI — L'INDUSTRIALISATION

## Module 20 — Docker

🎯 **Objectif** : que ton projet démarre à l'identique sur n'importe quelle machine.

📚 **Cours.**
- **Image** = gabarit figé (app + environnement), décrit par un **Dockerfile**.
- **Conteneur** = instance en cours d'exécution d'une image.
- **Volume** = stockage **persistant** (les données survivent au redémarrage).
- **Réseau** = les conteneurs se parlent par leur **nom de service**.
- **Docker Compose** = orchestrer plusieurs conteneurs (`docker-compose.yml`).

Dockerfile commenté :
```dockerfile
FROM python:3.14-slim          # image de base
WORKDIR /app                   # dossier de travail
COPY requirements.txt .        # copier d'abord les dépendances…
RUN pip install -r requirements.txt   # …pour profiter du CACHE de couches
COPY app ./app                 # puis le code (qui change souvent)
RUN useradd appuser            # utilisateur non-root (sécurité)
CMD ["python", "-m", "scripts.docker_entrypoint"]
```
**Notion clé : le cache de couches.** Chaque instruction crée une **couche**. Si rien n'a changé
au-dessus, Docker réutilise le cache → build ultra-rapide. D'où l'ordre : dépendances **avant**
le code.

Commandes vitales :
```bash
docker compose up -d --build   # construire et démarrer
docker compose ps              # état
docker compose logs api        # journaux
docker compose down            # arrêter (garde les données)
docker compose down -v         # arrêter + SUPPRIMER la base (reset)
```

🏦 **Dans NovaBank** : 3 conteneurs (postgres, api, frontend nginx) ; le **modèle ML est entraîné
pendant le build** ; `demarrer.bat` fait tout en un double-clic ; `reconstruire.bat` réinitialise
la base quand le schéma change.

✍️ **Exercices** : (1) écris un Dockerfile pour un script Python « hello ». (2) Lis le Dockerfile
du backend NovaBank et explique **pourquoi** `COPY requirements.txt` vient avant `COPY app`.
(3) Fais `docker compose logs api` et suis le démarrage.

🔗 **Ressources** : **docs.docker.com/get-started** ; « Docker Curriculum » (gratuit).

---

## Module 21 — Les tests

🎯 **Objectif** : modifier ton code sans peur de tout casser.

📚 **Cours.**
```python
def test_retrait_refuse_si_solde_insuffisant(client, auth_headers):
    resp = client.post("/transactions", headers=auth_headers("advisor"), json={...})
    assert resp.status_code == 400
```
Notions :
- **Test unitaire** (une fonction isolée) vs **test d'intégration** (plusieurs couches ensemble).
- **Assertion** (`assert`) : ce qu'on affirme être vrai.
- **Fixture** (pytest) : préparer un contexte réutilisable (une base de test, un utilisateur).
- **Isolation** : chaque test doit être **indépendant** — dans NovaBank, chaque test tourne dans
  une **transaction annulée à la fin**.
- **Tester les échecs** : un tiers des tests de NovaBank vérifient qu'on **refuse** correctement
  (solde insuffisant, 403, 409, 422). *Savoir dire non est aussi important que savoir dire oui.*
- **Couverture** (*coverage*) : % de code exécuté par les tests (utile, mais 100 % n'est pas un
  but en soi).
- **TDD** (*Test-Driven Development*) : écrire le test **avant** le code — excellent exercice.

🏦 **Dans NovaBank** : **92 tests** pytest, base dédiée `novabank_test`, moteur de règles forcé
pour être **déterministe**.

✍️ **Exercices** : (1) lance `pytest -v` et lis les noms des tests — ils **racontent** le
comportement du système. (2) Casse volontairement une règle métier et observe le test rouge.
(3) Écris un test pour une règle non couverte.

🔗 **Ressources** : **docs.pytest.org** ; « Python Testing with pytest » (B. Okken).

---

## Module 22 — Intégration continue (CI/CD)

🎯 **Objectif** : automatiser la vérification à chaque modification.

📚 **Cours.**
- **CI** (*Continuous Integration*) : à chaque `push`, un robot installe, **lint** et **teste**
  sur une machine neuve. Si c'est rouge, tu le sais **tout de suite**.
- **CD** (*Continuous Delivery/Deployment*) : automatiser aussi la mise en production.
- **GitHub Actions** : un fichier `.github/workflows/ci.yml` décrit les étapes (*jobs*, *steps*),
  déclenchées par un événement (`on: push`).
- **Services** : la CI peut lancer un vrai PostgreSQL pour tester en conditions réelles.
- **Linter** (**ruff**) : analyse statique du code (style, imports inutilisés, erreurs).

🏦 **Dans NovaBank** : ruff + 92 tests contre un vrai PostgreSQL, à chaque push. Le **badge vert**
est une preuve de qualité pour ton jury.

✍️ **Exercices** : (1) lis `.github/workflows/ci.yml` et explique chaque étape. (2) Pousse un
code volontairement mal formaté et observe la CI échouer. (3) Corrige et observe le vert.

🔗 **Ressources** : **docs.github.com/actions** ; **docs.astral.sh/ruff**.

---

# PARTIE VII — LE MÉTIER BANCAIRE

## Module 23 — Comprendre la banque, la fraude et la conformité

🎯 **Objectif** : parler le langage du métier (ce qui te distinguera à la soutenance).

📚 **Cours — vocabulaire essentiel.**
- **KYC** (*Know Your Customer*) : connaître son client (identité, CIN, profession, revenu,
  origine des fonds). Obligation légale, et **base du scoring** (le revenu sert de référence).
- **LBC-FT** : Lutte contre le Blanchiment de Capitaux et le Financement du Terrorisme.
- **Blanchiment** : donner une apparence légale à de l'argent illicite. Trois phases :
  **placement** (introduire l'argent), **empilage** (multiplier les opérations pour brouiller la
  piste), **intégration** (réinvestir dans l'économie légale).
- **Fractionnement (*structuring*/*smurfing*)** : découper un gros montant en petits pour passer
  sous les seuils de déclaration. → d'où la feature **cumul 72 h** de NovaBank.
- **Compte dormant réactivé** : signature classique d'usurpation ou de compte compromis.
- **Compte mule** : compte d'un tiers (parfois complice, parfois victime) servant à faire
  transiter des fonds.
- **Déclaration de soupçon** : signalement obligatoire d'une opération suspecte à la cellule de
  renseignement financier — au Maroc, l'**ANRF**, cadre de la **loi 43-05**.
- **Faux positif** : alerte à tort (coûte du temps d'enquête et de la crédibilité).
  **Faux négatif** : fraude ratée (coûte de l'argent et du risque réglementaire).
- **Maker-checker** (principe des **quatre yeux**) : celui qui **propose** une action sensible
  n'est **jamais** celui qui l'**approuve**. Parade de référence contre la **fraude interne**.
- **Piste d'audit** (*audit trail*) : trace inviolable de qui a fait quoi.

🤔 **Pourquoi c'est décisif** : un ingénieur qui comprend le métier construit la bonne
fonctionnalité. Les 2 features les plus performantes de NovaBank (cumul 72 h, inactivité) ne
viennent pas d'un catalogue technique — elles viennent de la **connaissance de la fraude**.

🏦 **Dans NovaBank** : déclaration de soupçon PDF, profil de risque KYC, workflow maker-checker,
surveillance de la fraude interne, audit append-only.

✍️ **Exercices** : (1) explique le fractionnement à quelqu'un qui n'y connaît rien. (2) Donne un
exemple de faux positif coûteux. (3) Explique pourquoi laisser un conseiller assouplir seul la
détection serait dangereux.

🔗 **Ressources** : site de **Bank Al-Maghrib** (publications sur les moyens de paiement et le
suivi de la fraude) ; **GAFI/FATF** (normes internationales LBC-FT) ; textes de la **loi 43-05**.

---

# PARTIE VIII — REFAIRE NOVABANK DE ZÉRO

> Règle d'or : **un squelette qui marche d'abord**, puis on muscle. Ne passe à l'étape suivante
> que quand la **vérification** passe. Commite à chaque étape.

### Étape 0 — Préparer (½ journée)
Installer Python 3.14, Node 22, Docker Desktop, Git, VS Code.
✅ *Vérif* : `python --version`, `node -v`, `docker --version`, `git --version` répondent.

### Étape 1 — Concevoir sur PAPIER (1 journée)
Liste les entités et leurs relations **avant** de coder : users, clients, accounts,
transactions, risk_scores, alerts, audit_logs, app_settings. Dessine les liens (1-N).
✅ *Vérif* : tu peux expliquer chaque table et chaque relation à voix haute.

### Étape 2 — Fondations backend (1 jour)
`venv`, `requirements.txt`, `app/core/config.py` (lit le `.env`), `app/db/session.py`
(engine + session), `app/main.py` avec un endpoint `/health`.
✅ *Vérif* : `uvicorn app.main:app --reload` → `/health` renvoie `{"status":"ok"}`.

### Étape 3 — PostgreSQL avec Docker (½ jour)
Un `docker-compose.yml` avec le seul service `postgres` (port hôte **5433**).
✅ *Vérif* : `docker compose up -d postgres` et tu te connectes avec `psql`.

### Étape 4 — Les modèles (1-2 jours)
Une classe SQLAlchemy par table. `Numeric` pour l'argent, `server_default=func.now()` pour les
dates, index sur le CIN. Script `create_tables.py`.
✅ *Vérif* : `\dt` liste les 8 tables.

### Étape 5 — Les schémas Pydantic (1 jour)
Create / Update / Response par entité. Contraintes (regex du CIN, `ge=0`).
✅ *Vérif* : un CIN invalide renvoie 422.

### Étape 6 — La sécurité (2 jours)
`security.py` (bcrypt + JWT), `deps.py` (`get_current_user`, `require_role`), router `auth`
(login, refresh, me), verrouillage après 5 échecs.
✅ *Vérif* : login OK ; un jeton de conseiller reçoit 403 sur une route directeur.

### Étape 7 — Les services (2-3 jours)
`transaction_service` (virement **verrouillé**, ordre par id), `audit_service`, `auth_service`.
✅ *Vérif* : un retrait supérieur au solde est refusé ; l'audit enregistre l'action.

### Étape 8 — Les routers (2 jours)
clients, accounts, transactions, alerts, analytics, users, audit. Tester dans **Swagger**.
✅ *Vérif* : le parcours complet fonctionne dans `/docs`.

### Étape 9 — Tests + CI (2 jours)
`conftest.py` (base dédiée, transaction annulée), tests par domaine, `.github/workflows/ci.yml`.
✅ *Vérif* : `pytest` vert en local **et** badge vert sur GitHub.

### Étape 10 — Le module IA (3-4 jours)
`features.py` (extraction **partagée**), `train_model.py` (génération des données, RF vs
IsolationForest vs règles, métriques honnêtes), `model.py` (chargement + SHAP + garde-fou sur
les noms de features), `scoring_service` (double moteur), boucle de feedback.
✅ *Vérif* : une opération suspecte score haut, avec explication et SHAP ; `metrics.json` montre
que le RF bat la baseline.

### Étape 11 — Rapports serveur (1 jour)
PDF (reportlab) et Excel (openpyxl).
✅ *Vérif* : les fichiers se téléchargent et s'ouvrent.

### Étape 12 — Le frontend (4-6 jours)
Vite + React + TS + Tailwind ; `api/client.ts` (axios + refresh) ; contextes ; composants `ui/` ;
les écrans par rôle ; routes + gardes.
✅ *Vérif* : `tsc --noEmit` sans erreur, et le parcours complet fonctionne dans le navigateur.

### Étape 13 — Dockerisation complète (1-2 jours)
Dockerfiles (backend qui **entraîne le modèle au build**, frontend en 2 étapes + nginx),
`docker_entrypoint.py`, scripts `demarrer` / `reconstruire`.
✅ *Vérif* : `docker compose up -d --build` et tout fonctionne sur une machine vierge.

### Étape 14 — Migrations Alembic (1 jour)
✅ *Vérif* : `alembic upgrade head` puis `downgrade -1` fonctionnent.

### Étape 15 — Les fonctionnalités métier (3-5 jours)
Fractionnement, comptes dormants, déclaration de soupçon, santé du modèle, seuil configurable,
fraude interne, profil de risque + workflow maker-checker.
✅ *Vérif* : chaque fonctionnalité a **ses tests** et une **preuve chiffrée**.

### Étape 16 — Mobile (PWA) (1 jour)
Manifest + service worker (**sans cache API**) + navigation mobile + cibles tactiles 44 px.
✅ *Vérif* : installable sur téléphone, aucun débordement à 375 px.

---

# PARTIE IX — PLAN D'APPRENTISSAGE (10 semaines)

| Semaine | Focus | Livrable personnel |
|---|---|---|
| 1 | Terminal, Git, Python bases (M0-M3) | Un mini-script Python versionné sur GitHub |
| 2 | Python objet + SQL (M3-M4) | Un schéma de base dessiné + requêtes SQL |
| 3 | HTTP/REST + FastAPI (M7-M8) | Une API CRUD à 2 entités |
| 4 | SQLAlchemy + Pydantic (M9-M10) | La même API, avec vraie base et validation |
| 5 | Sécurité + ACID (M11-M12) | Auth JWT + rôles + un virement verrouillé |
| 6 | Tests + Docker + CI (M20-M22) | Ton API testée, dockerisée, CI verte |
| 7 | HTML/CSS/TS (M5-M6) | Une page statique propre en Tailwind |
| 8 | React (M13-M14) | Une interface qui consomme ton API |
| 9 | ML : bases, sklearn, métriques (M15-M17) | Un modèle entraîné et **honnêtement** évalué |
| 10 | SHAP, MLOps, métier (M18-M19, M23) | Le scoring expliqué + surveillé |

> Puis : **refais NovaBank en entier** (Partie VIII) en t'appuyant sur tout ça. C'est en le
> refaisant que tu le maîtriseras vraiment.

---

## 🧭 Les 10 principes d'ingénierie à emporter

1. **Sépare les responsabilités** (router / service / modèle) — chaque chose à sa place.
2. **Valide à la frontière** — ne fais jamais confiance à une entrée.
3. **La sécurité est côté serveur** — l'interface n'est que du confort.
4. **Jamais de float pour l'argent** — `Decimal`, toujours.
5. **Rends l'état cohérent** — transactions, verrous, ordre déterministe.
6. **Trace les actions sensibles** — un audit inviolable.
7. **Mesure honnêtement** — les bonnes métriques, jamais de chiffre gonflé.
8. **Explique tes décisions** — un modèle inexplicable est inutilisable.
9. **La qualité des données prime sur le modèle** — la leçon n°1 du projet.
10. **Automatise la vérification** — tests + CI, sinon la peur du changement paralyse.

---

> ✅ **Si tu suis ce cours module par module, en faisant les exercices, tu ne sauras pas
> seulement « utiliser » NovaBank : tu sauras le reconstruire, et surtout construire
> *autre chose*.** C'est ça, devenir ingénieur : comprendre les principes, pas mémoriser
> des recettes.
>
> Pose-toi toujours **la question de l'ingénieur** : *« pourquoi ce choix, et quelle serait
> l'alternative ? »* Bon courage, El Mehdi. 🚀
