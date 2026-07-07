"""Module Intelligence Artificielle (CdC Module 7).

Organisation :
    features.py : extraction des caractéristiques d'une transaction —
                  code UNIQUE partagé par l'entraînement ET l'inférence
                  (toute divergence entre les deux fausse le modèle :
                  c'est le "training/serving skew", bug ML classique n°1).
    model.py    : chargement de l'artefact entraîné + prédiction, avec
                  repli transparent sur le moteur de règles si aucun
                  modèle n'est disponible.

L'entraînement vit dans scripts/train_model.py (hors du package app :
il ne doit jamais s'exécuter dans le processus de l'API).
"""
