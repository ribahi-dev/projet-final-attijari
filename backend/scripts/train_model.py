"""Entraînement et évaluation du modèle de détection d'anomalies (Module 7).

Démarche (documentée pour le rapport, §9.1 du cahier des charges) :

1. DONNÉES : génération d'un jeu étiqueté simulé mais statistiquement
   réaliste (~20 000 transactions, ~1,5 % de fraudes — la fraude est RARE,
   on n'équilibre pas artificiellement le jeu de TEST, conformément à la
   mise en garde de l'état de l'art §2.3 sur les métriques gonflées).
   S'y AJOUTENT les étiquettes réelles de la boucle de feedback : chaque
   alerte qualifiée par le directeur (confirmed_fraud / false_positive)
   devient un exemple d'entraînement — le système apprend de l'agence.

2. MODÈLES : RandomForest (supervisé, retenu §2.4) comparé à
   IsolationForest (non supervisé, alternative si pas d'étiquettes) et à
   la BASELINE de règles (mvp-rules-v1) déjà en production.

3. MÉTRIQUES : précision, rappel, F1 et AUC-PR — jamais l'accuracy seule,
   trompeuse à 98,5 % de classe majoritaire (état de l'art §2.3).

4. ARTEFACT : ml_artifacts/model.joblib + metrics.json (versionnés,
   auditables). L'API le charge au prochain démarrage — zéro changement
   de code côté scoring.

Usage :  python -m scripts.train_model
"""

import json
import random
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import average_precision_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split

from app.ml.features import FEATURE_NAMES, TransactionFeatures

MODEL_VERSION = "ml-rf-v2.1"  # v2.1 : +fractionnement (cumul 72h) +comptes dormants
ARTIFACTS_DIR = Path("ml_artifacts")
SEED = 42

rng = random.Random(SEED)
np_rng = np.random.default_rng(SEED)


def generate_labeled_dataset(n: int = 20_000, fraud_rate: float = 0.015):
    """Simule des vecteurs de features selon deux régimes de comportement.

    Légitime : montants faibles vs revenu, heures de bureau, ville stable.
    Frauduleux : combinaisons de signaux (gros montant ET/OU nuit ET/OU
    changement de ville ET/OU rafale d'opérations) — avec chevauchement
    volontaire entre les deux classes : un jeu parfaitement séparable
    donnerait des métriques irréalistes (rappel de l'état de l'art §2.3).
    """
    X, y = [], []
    for _ in range(n):
        is_fraud = rng.random() < fraud_rate
        if not is_fraud:
            # Comportement légitime AVEC exceptions réalistes : ~7 % des
            # opérations honnêtes sont "atypiques" (salaire, loyer, achat
            # exceptionnel, déplacement) — c'est ce chevauchement qui rend
            # le problème difficile et les métriques crédibles.
            atypical = rng.random() < 0.07
            features = TransactionFeatures(
                amount_over_income=abs(np_rng.normal(1.4, 0.9)) if atypical else abs(np_rng.normal(0.15, 0.35)),
                amount_over_avg=abs(np_rng.normal(3.0, 2.0)) if atypical else abs(np_rng.normal(1.0, 0.9)),
                is_night=1 if rng.random() < (0.20 if atypical else 0.04) else 0,
                city_changed=1 if rng.random() < (0.35 if atypical else 0.08) else 0,
                tx_last_24h=int(abs(np_rng.normal(1.8, 1.5))),
                cumul_72h_over_income=abs(np_rng.normal(1.5, 1.0)) if atypical else abs(np_rng.normal(0.4, 0.3)),
                days_since_last_tx=int(abs(np_rng.normal(20, 25))) if atypical else int(abs(np_rng.normal(3, 5))),
            )
        else:
            # Une fraude n'allume pas TOUS les signaux : tirage d'un profil,
            # dont un profil "discret" volontairement proche du légitime.
            profile = rng.choice(
                ["big_amount", "night_away", "burst", "mixed", "subtle", "structuring", "dormant"]
            )
            if profile == "subtle":
                features = TransactionFeatures(
                    amount_over_income=abs(np_rng.normal(0.6, 0.4)),
                    amount_over_avg=abs(np_rng.normal(2.0, 1.2)),
                    is_night=1 if rng.random() < 0.25 else 0,
                    city_changed=1 if rng.random() < 0.35 else 0,
                    tx_last_24h=int(abs(np_rng.normal(3, 2))),
                    cumul_72h_over_income=abs(np_rng.normal(1.2, 0.8)),
                    days_since_last_tx=int(abs(np_rng.normal(10, 15))),
                )
            elif profile == "structuring":
                # FRACTIONNEMENT : chaque montant reste MODÉRÉ (passe sous les
                # seuils unitaires), mais le cumul 72h explose — seule la
                # nouvelle feature cumul_72h_over_income voit ce schéma.
                features = TransactionFeatures(
                    amount_over_income=abs(np_rng.normal(0.4, 0.2)),
                    amount_over_avg=abs(np_rng.normal(1.5, 0.8)),
                    is_night=1 if rng.random() < 0.15 else 0,
                    city_changed=1 if rng.random() < 0.2 else 0,
                    tx_last_24h=int(abs(np_rng.normal(4, 2))),
                    cumul_72h_over_income=abs(np_rng.normal(4.0, 1.5)),
                    days_since_last_tx=int(abs(np_rng.normal(3, 4))),
                )
            elif profile == "dormant":
                # COMPTE DORMANT réactivé par un gros retrait : signature
                # classique d'usurpation / compte compromis.
                features = TransactionFeatures(
                    amount_over_income=abs(np_rng.normal(1.8, 1.0)),
                    amount_over_avg=abs(np_rng.normal(3.5, 2.0)),
                    is_night=1 if rng.random() < 0.3 else 0,
                    city_changed=1 if rng.random() < 0.5 else 0,
                    tx_last_24h=int(abs(np_rng.normal(1, 1))),
                    cumul_72h_over_income=abs(np_rng.normal(2.0, 1.2)),
                    days_since_last_tx=min(365, int(abs(np_rng.normal(150, 60)))),
                )
            else:
                features = TransactionFeatures(
                    amount_over_income=(
                        abs(np_rng.normal(2.6, 1.6)) if profile in ("big_amount", "mixed")
                        else abs(np_rng.normal(0.8, 0.6))
                    ),
                    amount_over_avg=abs(np_rng.normal(4.0, 2.5)),
                    is_night=1 if profile in ("night_away", "mixed") or rng.random() < 0.3 else 0,
                    city_changed=1 if profile in ("night_away", "mixed") or rng.random() < 0.4 else 0,
                    tx_last_24h=int(abs(np_rng.normal(6, 3))) if profile in ("burst", "mixed") else int(abs(np_rng.normal(2, 1.5))),
                    cumul_72h_over_income=abs(np_rng.normal(1.5, 1.0)),
                    days_since_last_tx=int(abs(np_rng.normal(8, 10))),
                )
        X.append(features.as_vector())
        y.append(1 if is_fraud else 0)
    return np.array(X), np.array(y)


def load_feedback_labels():
    """Boucle de feedback : les qualifications du directeur deviennent des
    étiquettes d'entraînement (human-in-the-loop). Retourne ([], []) si la
    base est inaccessible — l'entraînement reste possible hors connexion."""
    try:
        from sqlalchemy import select
        from app.db.session import SessionLocal
        from app.ml.features import extract_features
        from app.models import Account, Alert

        X, y = [], []
        with SessionLocal() as db:
            alerts = db.scalars(
                select(Alert).where(Alert.resolution.is_not(None), Alert.transaction_id.is_not(None))
            ).all()
            for alert in alerts:
                tx = alert.transaction
                if tx is None:
                    continue
                account = db.get(Account, tx.account_id)
                f = extract_features(db, account, tx.amount, tx.city, tx.created_at)
                X.append(f.as_vector())
                y.append(1 if alert.resolution == "confirmed_fraud" else 0)
        return X, y
    except Exception as exc:  # pragma: no cover
        print(f"(feedback ignoré : {exc})")
        return [], []


def rules_score_vector(x: np.ndarray) -> int:
    """Réplique de la baseline mvp-rules-v1 pour comparaison équitable."""
    amount_over_income, amount_over_avg, is_night, city_changed, tx_24h, cumul_72h, days_since = x
    score = 0
    if amount_over_income >= 2:
        score += 45
    elif amount_over_income >= 1:
        score += 30
    elif amount_over_income >= 0.5:
        score += 12
    elif amount_over_avg >= 5:
        score += 40
    elif amount_over_avg >= 3:
        score += 25
    if is_night:
        score += 25
    if city_changed:
        score += 20
    if tx_24h >= 5:
        score += 15
    if cumul_72h >= 3:
        score += 30
    elif cumul_72h >= 1.5:
        score += 15
    if days_since >= 90:
        score += 20
    elif days_since >= 30:
        score += 8
    return min(100, score)


def evaluate(name: str, y_true, scores_0_100, threshold: int = 70) -> dict:
    y_pred = (np.array(scores_0_100) >= threshold).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", zero_division=0
    )
    auc_pr = average_precision_score(y_true, np.array(scores_0_100) / 100)
    metrics = {
        "precision": round(float(precision), 3),
        "recall": round(float(recall), 3),
        "f1": round(float(f1), 3),
        "auc_pr": round(float(auc_pr), 3),
        "alertes_generees": int(y_pred.sum()),
    }
    print(f"  {name:<22} précision={metrics['precision']:.3f}  rappel={metrics['recall']:.3f}  "
          f"F1={metrics['f1']:.3f}  AUC-PR={metrics['auc_pr']:.3f}  alertes={metrics['alertes_generees']}")
    return metrics


def main() -> None:
    print("1/4 Génération du jeu de données simulé…")
    X, y = generate_labeled_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, stratify=y, random_state=SEED
    )

    fx, fy = load_feedback_labels()
    if fx:
        # Les étiquettes humaines rejoignent l'ENTRAÎNEMENT uniquement —
        # le jeu de test reste inchangé pour une comparaison stable.
        X_train = np.vstack([X_train, np.array(fx)])
        y_train = np.concatenate([y_train, np.array(fy)])
        print(f"   + {len(fx)} étiquette(s) issue(s) de la boucle de feedback du directeur")

    print(f"   train={len(X_train)}  test={len(X_test)}  fraudes test={int(y_test.sum())} "
          f"({y_test.mean():.1%} — déséquilibre réaliste conservé)")

    print("2/4 Entraînement des modèles…")
    # class_weight='balanced' : compense le déséquilibre SANS rééchantillonner
    # (évite l'effet SMOTE sur la fidélité des explications — CdC §2.3).
    # max_depth=10 : 7 features (dont 2 signaux temporels) demandent des
    # arbres un peu plus profonds pour croiser les dimensions.
    rf = RandomForestClassifier(
        n_estimators=300, max_depth=10, class_weight="balanced", random_state=SEED, n_jobs=-1
    )
    rf.fit(X_train, y_train)

    iso = IsolationForest(contamination=0.015, random_state=SEED)
    iso.fit(X_train[y_train == 0])  # non supervisé : n'apprend que le "normal"

    print("3/4 Évaluation sur le jeu de test (seuil d'alerte = 70) :")
    results = {
        "baseline_regles": evaluate(
            "Règles (baseline)", y_test, [rules_score_vector(x) for x in X_test]
        ),
        "isolation_forest": evaluate(
            "IsolationForest",
            y_test,
            # score_samples : plus négatif = plus anormal -> normalisation 0-100
            (lambda s: ((s.max() - s) / (s.max() - s.min()) * 100))(iso.score_samples(X_test)),
        ),
        "random_forest": evaluate(
            "RandomForest (retenu)", y_test, rf.predict_proba(X_test)[:, 1] * 100
        ),
    }

    print("4/4 Sauvegarde de l'artefact…")
    ARTIFACTS_DIR.mkdir(exist_ok=True)
    payload = {
        "model": rf,
        "feature_names": FEATURE_NAMES,
        "version": MODEL_VERSION,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "feedback_labels_used": len(fx),
        "metrics": results,
    }
    joblib.dump(payload, ARTIFACTS_DIR / "model.joblib")
    report = {k: v for k, v in payload.items() if k != "model"}
    report["feature_importances"] = dict(
        zip(FEATURE_NAMES, [round(float(v), 3) for v in rf.feature_importances_])
    )
    (ARTIFACTS_DIR / "metrics.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"   -> {ARTIFACTS_DIR / 'model.joblib'} (version {MODEL_VERSION})")
    print(f"   -> {ARTIFACTS_DIR / 'metrics.json'}")
    print("Redémarrer l'API pour charger le nouveau modèle.")


if __name__ == "__main__":
    main()
