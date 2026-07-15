# 🎓 Apprendre de zéro — Comprendre et refaire NovaBank soi-même

> **Pour qui ?** Un étudiant qui ne connaît (presque) rien et veut **tout comprendre** :
> chaque mot, chaque langage, chaque notion, et surtout **POURQUOI chaque choix**.
>
> **Objectif** : à la fin, tu dois pouvoir **expliquer** le projet à n'importe qui et le
> **refaire toi-même, sans IA**. Ce document t'apprend à *penser* comme un ingénieur, pas
> seulement à copier du code.
>
> **Comment le lire ?** Dans l'ordre, une première fois, lentement. Chaque notion est
> expliquée avec : une **analogie** (pour comprendre), une **définition** (pour le
> vocabulaire), le **pourquoi** (pour l'ingénierie), et **où c'est dans NovaBank** (pour
> l'ancrer). Reviens-y comme référence.
>
> Ce guide complète [GUIDE_COMPLET.md](GUIDE_COMPLET.md) (chaque fichier) et
> [GUIDE_CONSTRUCTION.md](GUIDE_CONSTRUCTION.md) (les étapes). Ici, on part de **zéro**.

---

## 📖 Sommaire

- [Partie 0 — C'est quoi un logiciel, au fond ?](#p0)
- [Partie 1 — Les fondations d'Internet et du web](#p1)
- [Partie 2 — Les 3 couches : frontend, backend, base de données](#p2)
- [Partie 3 — Les langages, et POURQUOI chacun](#p3)
- [Partie 4 — La base de données expliquée (SQL, ORM, ACID)](#p4)
- [Partie 5 — Le backend : API, REST, FastAPI](#p5)
- [Partie 6 — La sécurité expliquée (hash, JWT, RBAC)](#p6)
- [Partie 7 — Le frontend : React, TypeScript, composants](#p7)
- [Partie 8 — L'intelligence artificielle, sans magie](#p8)
- [Partie 9 — L'explicabilité (SHAP) et la conformité](#p9)
- [Partie 10 — Docker et le déploiement](#p10)
- [Partie 11 — Tests, qualité, intégration continue](#p11)
- [Partie 12 — Git et le travail en équipe](#p12)
- [Partie 13 — Les grandes décisions du projet, justifiées](#p13)
- [Partie 14 — Comment refaire le projet toi-même](#p14)
- [Glossaire A → Z](#glossaire)

---

<a name="p0"></a>
## Partie 0 — C'est quoi un logiciel, au fond ?

**Analogie.** Un ordinateur est une machine bête mais rapide : il sait faire des opérations
simples (additionner, comparer, déplacer des données) des milliards de fois par seconde. Un
**programme** (ou **logiciel**) est une **recette** : une suite d'instructions précises qui
disent à la machine quoi faire, étape par étape.

**Un langage de programmation** est la *langue* dans laquelle on écrit la recette. La machine,
elle, ne comprend que des 0 et des 1 (le *binaire*). Un langage comme Python ou JavaScript est
**lisible par un humain** ; un autre programme (un *interpréteur* ou un *compilateur*) le
traduit en binaire pour la machine.

- **Compilé** (ex. C, Java) : on traduit tout le programme AVANT de l'exécuter → rapide.
- **Interprété** (ex. Python, JavaScript) : on traduit *ligne par ligne* pendant l'exécution →
  plus souple, un peu plus lent.

**Une application web** (comme NovaBank) est un logiciel qu'on utilise **dans un navigateur**
(Chrome, Edge…), sans rien installer. Elle vit sur deux endroits à la fois : une partie sur
**ton ordinateur** (ce que tu vois) et une partie sur un **serveur** (l'ordinateur distant qui
fait le travail et garde les données). C'est le principe **client-serveur** — la fondation de
tout le web.

---

<a name="p1"></a>
## Partie 1 — Les fondations d'Internet et du web

### Client et serveur
- **Client** : le programme qui *demande* quelque chose (ton navigateur).
- **Serveur** : le programme qui *répond* (une machine allumée en permanence).
- Ils se parlent par le **réseau** (Internet ou ton réseau local).

**Analogie** : le client est un client au restaurant, le serveur est… le serveur. Tu demandes
(commande), il apporte (réponse). Le menu, c'est l'**API** (voir plus bas).

### HTTP : la langue du web
**HTTP** (*HyperText Transfer Protocol*) est le **protocole** (l'ensemble de règles) que le
client et le serveur utilisent pour se parler. Chaque échange = une **requête** (question) +
une **réponse**.

Une requête HTTP contient :
- une **méthode** (le verbe : que veut-on faire ?) :
  - `GET` = *lire* (« donne-moi la liste des clients »)
  - `POST` = *créer* (« crée ce nouveau client »)
  - `PATCH`/`PUT` = *modifier*
  - `DELETE` = *supprimer*
- une **URL** (l'adresse : sur quoi ?) : ex. `/clients/42`
- des **en-têtes** (*headers*) : métadonnées (qui suis-je, quel format…)
- un **corps** (*body*) : les données (pour un POST, le nouveau client en **JSON**)

Une réponse HTTP contient un **code de statut** (le résultat en un nombre) :
- `200 OK` : réussi
- `201 Created` : créé
- `400 Bad Request` : ta demande est mauvaise (règle métier violée)
- `401 Unauthorized` : je ne sais pas qui tu es (pas connecté)
- `403 Forbidden` : je sais qui tu es, mais tu n'as pas le droit
- `404 Not Found` : ça n'existe pas
- `409 Conflict` : conflit (ex. cet email existe déjà)
- `422 Unprocessable Entity` : données mal formées
- `500 Internal Server Error` : le serveur a planté

> **Savoir distinguer 401 et 403 est un signe de maturité** : « je ne sais pas qui tu es » vs
> « je sais, mais c'est interdit ». Dans NovaBank, un conseiller qui ouvre le dashboard reçoit
> **403**.

### JSON : le format d'échange
**JSON** (*JavaScript Object Notation*) est une façon **texte** d'écrire des données, lisible
par l'humain ET par la machine. Exemple :
```json
{ "first_name": "Amina", "cin": "AB123456", "monthly_income": 8000 }
```
C'est le « langage commun » entre le frontend et le backend : les deux parlent JSON.

### CORS (une sécurité du navigateur)
**CORS** (*Cross-Origin Resource Sharing*) : par sécurité, un navigateur interdit à un site A
d'appeler l'API d'un site B, sauf si B l'autorise explicitement (liste blanche). Dans NovaBank,
en production, le frontend et l'API sont sur la **même origine** (nginx relaie `/api`), donc
pas de problème CORS.

---

<a name="p2"></a>
## Partie 2 — Les 3 couches : frontend, backend, base de données

C'est **LE** schéma mental le plus important. Retiens-le par cœur.

```
  UTILISATEUR (navigateur)
        │  clique "valider un retrait"
        ▼
┌─────────────────────┐
│  FRONTEND (React)   │  ce qu'on VOIT. Construit une requête HTTP + jeton.
└─────────────────────┘
        │  POST /transactions  { montant, compte… }   (en JSON)
        ▼
┌─────────────────────────────────────────────┐
│  BACKEND (FastAPI)                           │  le CERVEAU. Reçoit, vérifie,
│   router → service → modèle                  │  applique la logique métier.
└─────────────────────────────────────────────┘
        │  INSERT / UPDATE   (en SQL)
        ▼
┌─────────────────────┐
│  BASE (PostgreSQL)  │  la MÉMOIRE. Stocke durablement.
└─────────────────────┘
```

- **Frontend** = *ce que l'utilisateur voit et touche* (boutons, formulaires, graphiques).
- **Backend** = *la logique invisible* (règles, calculs, sécurité, accès aux données).
- **Base de données** = *la mémoire durable* (même si on éteint tout, les données restent).

**Pourquoi séparer ?** Parce que chaque couche a **un seul métier**. On peut changer l'apparence
(frontend) sans toucher aux règles (backend), changer la base sans réécrire l'interface, et
**tester** la logique sans lancer de navigateur. C'est la **séparation des responsabilités** —
le principe qui rend un logiciel **maintenable**.

---

<a name="p3"></a>
## Partie 3 — Les langages, et POURQUOI chacun

Un projet web sérieux utilise **plusieurs langages**, chacun pour ce qu'il fait de mieux :

| Langage | Où | Rôle | Pourquoi lui |
|---|---|---|---|
| **Python** | Backend + IA | logique métier, scoring | Lisible, immense écosystème IA (scikit-learn), rapide à écrire |
| **TypeScript** | Frontend | interface | JavaScript + **typage** (attrape les erreurs avant l'exécution) |
| **SQL** | Base | interroger les données | LE langage universel des bases relationnelles |
| **HTML** | Frontend | structure de la page | La « charpente » de toute page web |
| **CSS** | Frontend | apparence (couleurs, mise en page) | La « décoration » (via Tailwind ici) |

### Python (backend + IA)
Langage **interprété**, réputé pour sa **lisibilité**. On l'a choisi car :
- l'écosystème **IA** est en Python (scikit-learn, SHAP, numpy) → le module de fraude s'y
  intègre naturellement ;
- **FastAPI** (le framework web) est en Python et très performant.

Notion clé Python : le **typage optionnel** (`amount: Decimal`) documente et sécurise le code.

### TypeScript (frontend)
JavaScript est **le** langage des navigateurs (le seul qu'ils comprennent). Mais JavaScript
n'a pas de **types** : `"5" + 3` donne `"53"` (bug silencieux). **TypeScript** ajoute les types
par-dessus JavaScript : tu déclares `montant: number`, et si tu écris une bêtise, l'erreur
apparaît **à la compilation**, pas chez l'utilisateur. C'est un **filet de sécurité**.

### SQL (base de données)
**SQL** (*Structured Query Language*) sert à **interroger** une base relationnelle :
```sql
SELECT * FROM clients WHERE cin = 'AB123456';
```
Dans NovaBank, on n'écrit presque jamais de SQL à la main : un **ORM** (voir Partie 4) le génère
pour nous à partir de code Python. Mais **comprendre SQL reste essentiel**.

---

<a name="p4"></a>
## Partie 4 — La base de données expliquée

### Qu'est-ce qu'une base de données relationnelle ?
**Analogie** : un ensemble de **tableaux Excel** (appelés **tables**) reliés entre eux. Chaque
table a des **colonnes** (les champs) et des **lignes** (les enregistrements).

Exemple — la table `clients` :
| id | first_name | cin | monthly_income |
|---|---|---|---|
| 1 | Amina | AB123456 | 8000 |
| 2 | Omar | KH100001 | 5000 |

**Relationnelle** = les tables sont **reliées**. Un `compte` appartient à un `client` (via une
**clé étrangère** `client_id`). Une `transaction` appartient à un `compte`. C'est une chaîne :
`client → comptes → transactions → scores → alertes`.

**PostgreSQL** est le **SGBD** (Système de Gestion de Base de Données) choisi : robuste, gratuit,
standard en entreprise, et il gère les **verrous transactionnels** dont on a besoin (voir ACID).

### Les 8 tables de NovaBank
`users` (employés), `clients` (clients de la banque), `accounts` (comptes), `transactions`
(opérations), `risk_scores` (verdicts IA), `alerts` (alertes), `audit_logs` (journal), et
`app_settings` (réglages d'agence).

> ⚠️ **`User` ≠ `Client`** : `User` = qui se **connecte** à l'app (employé). `Client` = qui
> possède des **comptes** à la banque. Les confondre est l'erreur n°1.

### L'ORM : parler à la base en Python
**ORM** = *Object-Relational Mapping* (*correspondance objet-relationnel*). C'est un **traducteur**
entre le monde des objets (Python) et le monde des tables (SQL). Au lieu d'écrire du SQL, on écrit :
```python
client = Client(first_name="Amina", cin="AB123456")   # un objet Python
db.add(client)                                          # l'ORM génère l'INSERT SQL
```
Ici l'ORM est **SQLAlchemy**. Avantages :
1. On écrit du **Python** (plus lisible, moins d'erreurs).
2. **Protection contre l'injection SQL** (une attaque où un pirate glisse du SQL malveillant
   dans un champ) : l'ORM échappe automatiquement les valeurs.
3. Le code est **portable** (on pourrait changer de base sans tout réécrire).

**Décision NovaBank** : les **modèles SQLAlchemy sont la source de vérité** du schéma (pas un
fichier SQL séparé). Et **Alembic** (voir plus bas) versionne les évolutions.

### Types de données : pourquoi `Numeric` et pas `float` pour l'argent
Un **float** (nombre à virgule flottante) est stocké en binaire et **ne représente pas 0,10
exactement** — de minuscules erreurs d'arrondi s'accumulent. En banque, **inacceptable**. On
utilise **`Numeric`** (décimal **exact**). Règle d'or : **jamais de float pour de l'argent.**

### Horodatage : par la base, pas par Python
On met la date via `server_default=func.now()` → c'est **PostgreSQL** qui pose l'heure, pas le
code Python. Pourquoi ? Deux serveurs API auraient deux horloges légèrement différentes ; la base
donne **une seule horloge de référence**.

### ACID : la garantie des transactions
Une **transaction** (au sens base de données) = un **groupe d'opérations tout-ou-rien**. Un
virement = débiter A **ET** créditer B ; si l'un échoue, on **annule tout**. **ACID** résume les
4 garanties :
- **A**tomicité : tout ou rien.
- **C**ohérence : les règles restent respectées.
- **I**solation : deux transactions simultanées ne se corrompent pas.
- **D**urabilité : une fois validé, c'est gravé (même en cas de coupure).

**Le problème concret (lost update)** : deux virements simultanés sur le même compte lisent le
même solde (1000), calculent chacun, et écrivent → l'une écrase l'autre → **solde faux**.

**La solution NovaBank** : le **verrou** `SELECT ... FOR UPDATE` verrouille la ligne du compte
jusqu'à la fin ; le 2ᵉ virement **attend**. Ils s'exécutent **en série**. Et pour éviter le
**deadlock** (interblocage : chacun attend l'autre indéfiniment), on verrouille les comptes
**par ordre d'id croissant** — un ordre global unique brise le cycle. *(C'est un argument très
fort pour le jury.)*

### Migration (Alembic)
Une **migration** = une **modification versionnée** du schéma (ajouter une colonne, une table…).
**Alembic** garde l'**historique** de ces changements, comme des « sauvegardes » du schéma :
`baseline → +resolution → +shap_values → +contacts → +app_settings → +profil_risque → …`. Ça
permet de faire évoluer une base **existante** sans la casser, et de rejouer l'historique sur
n'importe quelle machine.

---

<a name="p5"></a>
## Partie 5 — Le backend : API, REST, FastAPI

### API : le contrat
**API** = *Application Programming Interface* (*interface de programmation*). C'est le **menu du
restaurant** : la liste des choses que le serveur sait faire, et comment les demander. Le
frontend ne connaît QUE l'API ; il ignore *comment* c'est fait derrière. Ça permet de changer
l'intérieur sans casser l'extérieur.

### REST : le style d'API
**REST** est un **style** d'API basé sur HTTP :
- chaque **ressource** a une URL (`/clients`, `/clients/42`) ;
- on agit dessus avec les **méthodes HTTP** (`GET` lire, `POST` créer, `PATCH` modifier,
  `DELETE` supprimer) ;
- le serveur ne **retient pas** l'état entre deux requêtes (*stateless*) : chaque requête porte
  tout ce qu'il faut (dont le jeton d'authentification).

Un **endpoint** = un point d'entrée précis de l'API : `POST /transactions`, `GET /alerts`…

### FastAPI (le framework)
Un **framework** = une boîte à outils qui structure ton code et t'évite de tout réécrire.
**FastAPI** (Python) fournit : le routage des URL, la **validation** automatique des données
(via Pydantic), la génération d'une **documentation interactive** (Swagger, sur `/docs`), et
l'**injection de dépendances**.

### Injection de dépendances (`Depends`)
**Idée** : au lieu que chaque endpoint aille chercher lui-même ce dont il a besoin (une session
de base, l'utilisateur connecté), **FastAPI le lui fournit** automatiquement. Tu déclares :
```python
def create_client(db: Session = Depends(get_db), staff = Depends(require_role("advisor"))):
```
et FastAPI **injecte** une session `db` et vérifie le rôle avant même d'entrer dans la fonction.
Avantage : le code est **découplé** et **testable** (en test, on injecte une fausse base).

### Pydantic : valider à la frontière
**Pydantic** décrit la **forme attendue** des données entrantes/sortantes (les **schémas**). Si
un client envoie un CIN mal formé ou un montant négatif, Pydantic **rejette** avec un `422`
clair, **avant** que la donnée atteigne la logique ou la base.

> **Question classique de jury : « Pourquoi ne pas renvoyer directement les objets de la base ? »**
> 3 raisons :
> 1. **Sécurité** : le modèle `User` contient `password_hash`. Le renvoyer serait une fuite. Le
>    schéma de sortie **garantit** qu'il ne sort jamais.
> 2. **Découplage** : renommer une colonne ne casse pas le frontend.
> 3. **Validation** : on rejette les données invalides à la porte.
> Séparer **le modèle (la base)** du **schéma (le contrat de l'API)** = protection en profondeur.

### L'architecture en couches (la règle d'or)
```
router  →  service  →  modèle
(HTTP)     (métier)    (base)
```
- **Router** : reçoit la requête HTTP, valide, **délègue**, traduit en réponse HTTP. *Ne touche
  jamais la base directement.*
- **Service** : la **logique métier** (verrou de virement, calcul du score, création d'alerte).
  *Ne connaît jamais HTTP.*
- **Modèle** : la table (SQLAlchemy).

**Pourquoi ?** On peut tester la logique sans serveur web, réutiliser un service ailleurs, et
comprendre où chaque chose vit. **Un router qui parle SQL, ou un service qui renvoie du HTTP, est
un signe de mauvaise architecture.**

---

<a name="p6"></a>
## Partie 6 — La sécurité expliquée

La sécurité suit l'**OWASP API Security Top 10** (la liste de référence des failles d'API).

### Hachage des mots de passe (bcrypt)
On ne stocke **jamais** un mot de passe en clair. On stocke son **hash** : le résultat d'une
fonction à **sens unique** (facile à calculer, impossible à inverser). À la connexion, on hache
le mot de passe saisi et on compare les deux hash.
- **bcrypt** est conçu pour être **lent exprès** (résiste aux attaques par force brute) et ajoute
  un **sel** (*salt*) aléatoire → deux utilisateurs avec le même mot de passe ont des hash
  différents.

### JWT : le badge de connexion
**JWT** (*JSON Web Token*) = un « badge » **signé** remis à la connexion. À chaque requête, le
client le présente ; le serveur **vérifie la signature** (sans base de données) et sait qui tu es
et ton rôle. Il est **stateless** (le serveur ne garde pas de session).
- Un JWT contient l'identité + le rôle, mais **jamais** de secret (il est lisible).
- NovaBank utilise **deux jetons** : un **access token** (courte durée, pour agir) et un
  **refresh token** (plus long, pour obtenir un nouveau access sans re-taper le mot de passe). On
  **vérifie le type** du jeton (un refresh ne peut pas servir d'access).
- On rejette explicitement l'algorithme `none` (une attaque JWT classique).

### RBAC : le contrôle d'accès par rôle
**RBAC** (*Role-Based Access Control*) : chaque **rôle** (admin / directeur / conseiller) a des
droits. La vérification se fait **côté serveur, à chaque requête** (`require_role`). Cacher un
bouton dans l'interface ne suffit PAS : un attaquant peut appeler l'API directement. **La vraie
sécurité est serveur.**

### Autres protections
- **Verrouillage** du compte après 5 échecs de connexion (anti force-brute).
- **Message d'erreur identique** pour « email inconnu » et « mauvais mot de passe » → on ne
  révèle pas quels emails existent (parade à l'**énumération**).
- **Journal d'audit** *append-only* (on **insère**, on ne **modifie** jamais) : qui a fait quoi,
  quand, depuis quelle IP.
- **Secrets hors du code** : mots de passe, jetons Telegram… vivent dans un fichier `.env`
  **jamais versionné** (principe *12-factor* : séparer code et configuration).

---

<a name="p7"></a>
## Partie 7 — Le frontend : React, TypeScript, composants

### Le trio HTML / CSS / JavaScript
- **HTML** = la **structure** (titres, boutons, champs).
- **CSS** = l'**apparence** (couleurs, tailles, disposition). Ici via **Tailwind** (des petites
  classes utilitaires : `flex`, `gap-2`, `text-primary`).
- **JavaScript/TypeScript** = le **comportement** (que se passe-t-il au clic ?).

### React : construire l'interface avec des composants
**React** est une **bibliothèque** pour construire des interfaces. Idée centrale : le
**composant** — un morceau d'interface **réutilisable** (un bouton, une carte, un tableau). On
assemble des composants comme des Lego.
- Un composant a un **état** (*state*) : des données qui, quand elles changent, **redessinent**
  automatiquement l'affichage. Ex. `const [clients, setClients] = useState([])`.
- Une **prop** = un paramètre passé à un composant (`<ScoreBadge score={80} />`).
- Un **hook** (`useState`, `useEffect`) = une fonction spéciale de React. `useEffect` sert à
  déclencher une action (ex. charger des données) quand le composant apparaît.

**Pourquoi des composants ?** Réutilisabilité et **cohérence** : le score s'affiche partout via
UN seul `ScoreBadge` → sa couleur EST l'information, uniforme dans toute l'app.

### Vite, le build, le bundle
Le navigateur ne comprend pas directement React/TypeScript. Un outil de **build** (**Vite**)
**compile** tout en HTML/CSS/JavaScript classiques, regroupés dans un **bundle** (un paquet de
fichiers optimisés). Les fichiers portent un **hash** dans leur nom (`index-a6X4.js`) → on peut
les mettre en cache « pour toujours » sans risque de version périmée.

### Le client API (axios) et les types miroirs
Le frontend appelle le backend via **axios** (un outil de requêtes HTTP). Il ajoute
automatiquement le **jeton JWT** à chaque appel et **renouvelle** le jeton expiré de façon
transparente. Les **types TypeScript** (`interface Client { … }`) sont le **miroir** des schémas
Pydantic du backend : si les deux divergent, TypeScript le signale.

### PWA : rendre l'app installable
**PWA** (*Progressive Web App*) = une app web qui s'**installe** sur le téléphone (icône, plein
écran) comme une app native, grâce à deux ingrédients :
- un **manifest** (nom, icônes, couleurs) ;
- un **service worker** : un petit script qui s'exécute en arrière-plan. ⚠️ Dans NovaBank, il ne
  met **rien** en cache (les données bancaires doivent toujours être fraîches) et efface les
  anciens caches — pour ne jamais afficher une version périmée.

---

<a name="p8"></a>
## Partie 8 — L'intelligence artificielle, sans magie

### Ce qu'est (et n'est pas) le Machine Learning
**Machine Learning** (*apprentissage automatique*) = apprendre des **règles à partir d'exemples**,
au lieu de les écrire à la main. On montre au modèle des milliers d'opérations étiquetées
(« fraude » / « normal »), et il **apprend** à distinguer les deux. Ce n'est **pas** magique :
c'est des mathématiques et des statistiques.

### Feature : transformer une opération en nombres
Un modèle ne comprend que des **nombres**. Une **feature** (caractéristique) = un signal numérique
extrait d'une donnée. NovaBank transforme chaque opération en **7 features** :
`montant/revenu`, `montant/moyenne du compte`, `opération nocturne`, `changement de ville`,
`nombre d'opérations sur 24h`, `cumul 72h/revenu` (anti-fractionnement), `jours d'inactivité`
(comptes dormants).

> **Point crucial** : le code qui calcule les features est **partagé** entre l'entraînement et
> l'inférence (`app/ml/features.py`). Sinon, le modèle apprend sur des features calculées d'une
> façon et prédit sur des features calculées autrement → **training/serving skew**, le bug
> classique du ML en production.

### Le modèle : Random Forest
Un **Random Forest** (*forêt aléatoire*) = un ensemble d'**arbres de décision** qui votent. Un
arbre pose des questions (« montant/revenu > 2 ? » → oui/non → question suivante…). Une **forêt**
combine des centaines d'arbres → robuste, peu sensible au **sur-apprentissage** (*overfitting* :
quand un modèle « apprend par cœur » les exemples au lieu de généraliser).

### Entraîner et évaluer HONNÊTEMENT
- On **entraîne** sur un jeu de données, on **évalue** sur un autre (jamais vu) → pour mesurer la
  vraie capacité à généraliser.
- Le problème est **déséquilibré** : la fraude est rare (~1,5 %). Donc l'**exactitude**
  (*accuracy*) est **trompeuse** : un modèle qui ne détecte rien atteint 98,5 % d'exactitude !
- On mesure avec les **bonnes métriques** :
  - **Précision** : parmi les alertes levées, combien sont vraies ? (peu de fausses alertes)
  - **Rappel** (*recall*) : parmi les fraudes réelles, combien attrapées ? (peu de fraudes ratées)
  - **F1** : l'équilibre entre précision et rappel.
  - **AUC-PR** : la métrique de référence des problèmes déséquilibrés.
- **Ne jamais gonfler** : on a introduit un **chevauchement volontaire** entre classes → des
  métriques **réalistes, pas parfaites** (RF F1 0,58 vs baseline 0,31).

### Le double moteur (robustesse)
Le scoring a **deux moteurs derrière une interface unique** : le **Random Forest** si l'artefact
entraîné existe, sinon un **moteur de règles** en repli. L'application n'est **jamais** en panne
de scoring, et chaque score garde la **trace du moteur** (`model_version`) — principe de
traçabilité **MLOps**.

### La boucle de feedback (human-in-the-loop) ⭐
Quand le directeur qualifie une alerte (fraude confirmée / faux positif), cette décision devient
une **étiquette d'entraînement** pour le prochain modèle. **Le système apprend des décisions de
l'agence.** C'est le différenciateur face aux solutions commerciales.

### MLOps : garder le modèle fiable dans le temps
Les fraudeurs s'adaptent → le modèle se **dégrade** (*dérive conceptuelle*). Le **MLOps** répond
par la **surveillance en production** : la page « Santé du modèle » calcule la **précision réelle**
sur les qualifications du directeur, le taux de faux positifs, etc. → pour savoir **quand
réentraîner**.

---

<a name="p9"></a>
## Partie 9 — L'explicabilité (SHAP) et la conformité

### Pourquoi expliquer une décision IA ?
Une décision algorithmique **inexpliquée** est inutilisable en banque : le directeur engage sa
responsabilité, le client a droit à une justification, et la loi (**RGPD**, **EU AI Act**) exige
la transparence des systèmes à haut risque.

### SHAP (*XAI* = eXplainable AI)
**SHAP** répartit le score entre les variables selon les **valeurs de Shapley** (une base
mathématique issue de la **théorie des jeux**) : chaque variable reçoit une **contribution**
positive (pousse vers la fraude) ou négative (vers le normal). Dans NovaBank, ces contributions
sont **stockées** avec le score et **affichées** en barres bidirectionnelles → le directeur voit
non seulement *que* c'est risqué, mais *pourquoi*, variable par variable.

### La conformité LBC-FT (Maroc)
**LBC-FT** = Lutte contre le Blanchiment de Capitaux et le Financement du Terrorisme. La **loi
43-05** impose de **déclarer** les opérations suspectes à l'**ANRF**. NovaBank génère ce dossier
en un clic (PDF). **Règle de gouvernance** : c'est la **décision humaine** (fraude confirmée) qui
ouvre le droit de déclarer, jamais le score seul — et chaque génération est **auditée**.

### Le profil de risque et le maker-checker
Pour éviter les faux positifs sur les clients atypiques (voyageur, grande fortune), le directeur
**calibre** le scoring par client (neutralise un signal précis, jamais toute la détection). Et
comme **assouplir un contrôle est le mécanisme même de la fraude interne**, on applique le
principe **maker-checker** (« quatre yeux ») : le conseiller **propose**, le directeur
**approuve** — jamais la même personne. Tout est tracé.

---

<a name="p10"></a>
## Partie 10 — Docker et le déploiement

### Le problème : « ça marche sur ma machine »
Un logiciel dépend de son **environnement** (version de Python, de PostgreSQL, variables…). Sur
une autre machine, ça casse. **Docker** résout ça.

### Conteneur et image
- Une **image** = un « gabarit » figé qui contient l'app **ET** son environnement (le bon Python,
  les dépendances…). C'est une **recette** (le `Dockerfile`).
- Un **conteneur** = une **instance** qui tourne, créée à partir d'une image. Léger, isolé,
  identique partout.

**Analogie** : l'image est un moule à gâteau + la recette ; le conteneur est le gâteau cuit.

### Docker Compose : orchestrer plusieurs conteneurs
NovaBank a **3 conteneurs** : `postgres` (base), `api` (backend), `frontend` (nginx). **Docker
Compose** (`docker-compose.yml`) les décrit et les fait tourner ensemble d'**une seule commande**.
Ils se parlent par leur **nom de service** sur un réseau privé (l'api joint la base via
`postgres:5432`).

### Volume et nginx
- Un **volume** = un espace de stockage **persistant** hors du conteneur → les données de la base
  survivent au redémarrage. `docker compose down -v` supprime le volume (remise à zéro).
- **nginx** = un serveur web qui, en production, **sert** les fichiers du frontend ET **relaie**
  `/api` vers le backend (une seule origine → pas de souci CORS).

**Détail malin NovaBank** : le modèle ML est **entraîné pendant la construction de l'image** →
l'image livrée contient déjà un modèle prêt.

### Ports
Le navigateur parle au **port** 8090 (frontend) ; l'api est sur 8000 ; postgres sur 5433 côté
hôte (5432 étant souvent déjà pris par un PostgreSQL local). Un **port** = une « porte numérotée »
d'une machine pour un service donné.

---

<a name="p11"></a>
## Partie 11 — Tests, qualité, intégration continue

### Pourquoi tester ?
Un **test** = un bout de code qui **vérifie automatiquement** qu'une partie du programme fait ce
qu'elle doit. Sans tests, chaque modification risque de **casser** silencieusement autre chose.

- **Test unitaire** : vérifie une petite fonction isolée.
- **Test d'intégration** : vérifie que plusieurs parties marchent **ensemble** (ex. « créer un
  client via l'API l'enregistre bien en base »).

NovaBank a **92 tests** (pytest). Fait notable : **un tiers testent les ÉCHECS** (solde
insuffisant refusé, conseiller bloqué en 403…). *Savoir qu'un système refuse correctement une
mauvaise opération est aussi important que de savoir qu'il accepte une bonne.*

**Isolation** : chaque test tourne dans une base dédiée, dans une **transaction annulée à la fin**
→ les tests sont **indépendants** (l'un ne pollue pas l'autre).

### Lint : la propreté automatique
Un **linter** (**ruff** ici) analyse le code et signale les erreurs de style, imports inutilisés,
etc. → un code **uniforme** et sans scories.

### CI : l'intégration continue
**CI** (*Continuous Integration*) = à **chaque** envoi de code sur GitHub, un robot (**GitHub
Actions**) **relance automatiquement** le lint + les 92 tests sur une machine neuve avec un vrai
PostgreSQL. Le **badge vert** prouve que tout marche, à chaque modification. On attrape les
régressions **tôt**.

---

<a name="p12"></a>
## Partie 12 — Git et le travail en équipe

**Git** = un système de **contrôle de version** : il garde l'**historique complet** du code
(chaque changement, qui, quand, pourquoi) et permet de travailler à plusieurs sans s'écraser.

- Un **commit** = une **photo** de l'état du code à un instant, avec un message qui explique le
  « pourquoi ». On écrit des messages clairs (*conventional commits* : `feat:`, `fix:`, `docs:`).
- Une **branche** = une ligne de travail parallèle (on développe une fonctionnalité sans toucher
  au code stable).
- Un **dépôt** (*repository*, *repo*) = le projet versionné (ici sur **GitHub**).
- **push** = envoyer ses commits vers GitHub ; **pull** = récupérer ceux des autres ; **merge** =
  fusionner deux lignes de travail.

**Pourquoi ?** Historique = on peut revenir en arrière ; collaboration = trois personnes sur le
même projet ; traçabilité = chaque décision est datée et signée.

---

<a name="p13"></a>
## Partie 13 — Les grandes décisions du projet, justifiées

Un bon ingénieur ne fait pas des choix au hasard : il les **justifie**. Voici les décisions clés
de NovaBank et leur raison :

| Décision | Pourquoi |
|---|---|
| **FastAPI** (pas Django/Flask) | Validation forte (Pydantic), Swagger auto, Python (pour l'IA) |
| **PostgreSQL** | Données très relationnelles, verrous transactionnels, standard |
| **Architecture en couches** | Séparation des responsabilités → testable, maintenable |
| **`Numeric` pour l'argent** | Décimal exact ; un float accumulerait des erreurs d'arrondi |
| **Verrou `FOR UPDATE` + ordre par id** | Virements atomiques et sans deadlock (ACID) |
| **Schémas Pydantic ≠ modèles ORM** | Le `password_hash` ne fuit jamais ; découplage ; validation |
| **Double moteur ML + règles** | Jamais de panne de scoring ; comparaison chiffrée |
| **Métriques honnêtes (pas l'accuracy)** | La fraude est rare : l'accuracy ment ; on refuse de gonfler |
| **SHAP** | Explicabilité exigée (RGPD/AI Act) et confiance du directeur |
| **Boucle de feedback** | Le système apprend de l'agence (vs bases externes des concurrents) |
| **Décision humaine avant la déclaration** | L'IA assiste, l'humain décide (et engage sa responsabilité) |
| **Maker-checker sur le profil de risque** | Assouplir un contrôle est un risque → séparation des tâches |
| **Docker + modèle entraîné au build** | Reproductible partout, image livrée prête |
| **Données simulées, périmètre assumé** | Pas d'accès au SI réel (confidentialité) — méthodologie transférable |

**La leçon d'ingénierie n°1 du projet** : *la qualité des données prime sur la sophistication du
modèle*. On l'a vécue deux fois (cohérence physique des données simulées ; rejeu point-in-time des
features). Ces deux bugs de *training/serving skew* nous ont plus appris que n'importe quelle
fonctionnalité.

---

<a name="p14"></a>
## Partie 14 — Comment refaire le projet toi-même

L'ordre **compte** : on construit un « squelette qui marche » d'abord, puis on muscle chaque
étage. (Détail commande par commande dans [GUIDE_CONSTRUCTION.md](GUIDE_CONSTRUCTION.md).)

```
0.  Installer les outils (Python, Node, Docker, Git, VSCode)
1.  Concevoir la base sur PAPIER (les 8 entités et leurs relations)
2.  Fondations backend (venv, config, connexion à la base)
3.  PostgreSQL avec Docker
4.  Les modèles SQLAlchemy → créer les tables
5.  Les schémas Pydantic (contrats de l'API)
6.  La sécurité (bcrypt, JWT, RBAC)
7.  Les services (logique métier, dont le virement verrouillé)
8.  Les routers (l'API REST) → tester dans Swagger
9.  Les tests + l'intégration continue (badge vert)
──────────── à ce stade : socle fonctionnel ────────────
10. Le module IA (features → entraînement → SHAP → feedback)
11. Les rapports serveur (PDF/Excel)
12. Le frontend React (pages, composants, appels API)
13. La dockerisation complète (démarrage 1 clic)
14. Les migrations Alembic
15. Les améliorations métier (fractionnement, dormants, déclaration, santé,
    seuil, fraude interne, profil de risque + workflow d'approbation)
16. La version mobile (PWA)
──────────── à ce stade : plateforme complète ────────────
```

> **Conseil d'ingénieur** : ne passe à l'étape suivante que quand la **vérification** de l'étape
> actuelle passe. Écris un test **avant** ou **juste après** chaque brique. Committe souvent avec
> des messages clairs. Et à chaque décision, demande-toi **« pourquoi ce choix, et quelle est
> l'alternative ? »** — c'est cette question qui fait l'ingénieur.

---

<a name="glossaire"></a>
## Glossaire A → Z

- **ACID** — les 4 garanties d'une transaction base de données : Atomicité, Cohérence, Isolation, Durabilité.
- **API** — interface de programmation : le « menu » de ce que le serveur sait faire.
- **Accuracy (exactitude)** — % de bonnes prédictions ; trompeuse sur données déséquilibrées.
- **Audit (journal d')** — enregistrement inviolable (append-only) des actions sensibles.
- **AUC-PR** — aire sous la courbe précision-rappel ; métrique reine des problèmes déséquilibrés.
- **Backend** — la partie serveur (logique, données), invisible pour l'utilisateur.
- **bcrypt** — algorithme de hachage lent et salé pour les mots de passe.
- **Bundle** — paquet de fichiers frontend compilés et optimisés.
- **CI/CD** — intégration/déploiement continus : automatiser tests et livraison.
- **Clé étrangère** — colonne qui relie une table à une autre (ex. `client_id`).
- **Commit** — une « photo » versionnée du code avec un message.
- **Composant** — brique d'interface réutilisable (React).
- **Conteneur** — instance isolée d'une image Docker qui tourne.
- **CORS** — sécurité navigateur contrôlant quels sites peuvent appeler une API.
- **Deadlock (interblocage)** — deux processus qui s'attendent mutuellement à l'infini.
- **Dérive conceptuelle** — dégradation d'un modèle quand le monde change.
- **Docker** — outil qui empaquette une app + son environnement (conteneurs).
- **Endpoint** — un point d'entrée précis de l'API (ex. `POST /transactions`).
- **Feature** — signal numérique extrait d'une donnée pour le modèle.
- **Framework** — boîte à outils qui structure le code (FastAPI, React).
- **Frontend** — la partie visible (interface) dans le navigateur.
- **Git** — système de contrôle de version (historique + collaboration).
- **Hash (hachage)** — empreinte à sens unique d'une donnée.
- **HTTP** — protocole de communication du web (requête/réponse).
- **Injection SQL** — attaque glissant du SQL malveillant ; l'ORM protège.
- **JSON** — format texte d'échange de données.
- **JWT** — jeton signé prouvant l'identité et le rôle, sans session serveur.
- **Lint** — analyse automatique de la propreté du code.
- **Maker-checker** — séparation des tâches : celui qui propose ≠ celui qui approuve.
- **Migration** — modification versionnée du schéma de la base (Alembic).
- **MLOps** — pratiques pour surveiller et maintenir un modèle en production.
- **Modèle (ML)** — le « cerveau » entraîné qui prédit (Random Forest ici).
- **Modèle (ORM)** — la classe Python représentant une table.
- **ORM** — traducteur objets Python ↔ tables SQL (SQLAlchemy).
- **OWASP** — référentiel des grandes failles de sécurité web/API.
- **Port** — « porte numérotée » d'une machine pour un service (8090, 8000, 5433).
- **Précision** — parmi les alertes, combien sont justes.
- **Prop** — paramètre passé à un composant React.
- **PWA** — app web installable sur mobile (manifest + service worker).
- **Pydantic** — validation des données à la frontière de l'API.
- **Rappel (recall)** — parmi les fraudes réelles, combien attrapées.
- **Random Forest** — modèle ML : une forêt d'arbres de décision qui votent.
- **RBAC** — contrôle d'accès par rôle, vérifié côté serveur.
- **REST** — style d'API basé sur HTTP et les ressources.
- **Router** — couche qui reçoit les requêtes HTTP et délègue au service.
- **Service** — couche de logique métier (ne connaît pas HTTP).
- **Service worker** — script d'arrière-plan d'une PWA.
- **SGBD** — système de gestion de base de données (PostgreSQL).
- **SHAP** — méthode d'explicabilité : contribution de chaque variable au score.
- **SQL** — langage d'interrogation des bases relationnelles.
- **State (état)** — données d'un composant qui, changées, redessinent l'affichage.
- **Stateless** — sans mémoire d'état entre deux requêtes (REST, JWT).
- **Sur-apprentissage (overfitting)** — modèle qui « apprend par cœur » et ne généralise pas.
- **Test unitaire / d'intégration** — vérification auto d'une fonction / d'un ensemble.
- **Training/serving skew** — écart entre entraînement et production (bug ML classique).
- **Transaction (base)** — groupe d'opérations tout-ou-rien.
- **Verrou (lock)** — mécanisme empêchant deux accès concurrents de se corrompre.
- **Volume** — stockage persistant d'un conteneur Docker.

---

> ✅ **Si tu comprends ce document, tu ne « connais » pas seulement NovaBank — tu comprends
> comment on construit une application professionnelle, et pourquoi.** Relis-le, ouvre le code en
> parallèle, refais une brique toi-même, et pose-toi toujours la question de l'ingénieur :
> **« pourquoi ce choix, et quelle serait l'alternative ? »** C'est comme ça qu'on devient
> excellent. Bon courage, El Mehdi. 🚀
