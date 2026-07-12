"""Dossier de déclaration de soupçon — PDF réglementaire LBC-FT (version PFE).

Contexte métier (l'argument conformité du projet) :
    Au Maroc, la loi 43-05 relative à la lutte contre le blanchiment de
    capitaux (LBC-FT) impose aux banques de DÉCLARER les opérations
    suspectes à l'ANRF (Autorité Nationale du Renseignement Financier,
    ex-UTRF). En agence, monter ce dossier est un travail manuel et lent :
    rassembler l'identité KYC du client, l'opération, l'historique...

    NovaBank l'automatise : quand le directeur a QUALIFIÉ une alerte en
    fraude confirmée, un clic produit un dossier PDF complet — identité
    KYC, compte, opération incriminée, analyse du modèle IA (score +
    contributions SHAP), chronologie du compte et cadre légal.

    ⚠ Le document généré est un MODÈLE INDICATIF à usage pédagogique
    (données simulées) — pas un formulaire officiel de l'ANRF.

Règle de la couche service : reçoit une Session et une Alert, renvoie des
`bytes` — aucune logique HTTP ici (le router gère codes et en-têtes).
"""

import io
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Alert, Transaction

BRAND_ORANGE = "#F08100"
DARK = "#1F2427"
GREY_LINE = "#E4E7EC"
ROW_ALT = "#F7F8FA"

# Traduction des features techniques en libellés lisibles par un juriste
# ou un enquêteur (le PDF sort du cercle des développeurs).
FEATURE_LABELS = {
    "amount_over_income": "Montant rapporté au revenu mensuel",
    "amount_over_avg": "Montant rapporté à la moyenne du compte",
    "is_night": "Opération nocturne (00h-06h)",
    "city_changed": "Changement de ville",
    "tx_last_24h": "Nombre d'opérations sur 24h",
    "cumul_72h_over_income": "Cumul des opérations sur 72h / revenu (fractionnement)",
    "days_since_last_tx": "Jours d'inactivité du compte avant l'opération",
}

TYPE_LABELS = {"deposit": "Dépôt", "withdrawal": "Retrait", "transfer": "Virement"}


def generate_suspicion_report_pdf(db: Session, alert: Alert) -> bytes:
    """Construit le dossier PDF d'une alerte qualifiée en fraude confirmée.

    Le router garantit les préconditions (alerte existante, transaction
    liée, resolution == confirmed_fraud) — ici on ne fait que composer le
    document, section par section, comme un dossier papier.
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
    )

    tx = alert.transaction
    account = tx.account
    client = account.client
    risk = tx.risk_score

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.8 * cm, bottomMargin=1.8 * cm)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("t", parent=styles["Title"], textColor=colors.HexColor(DARK), fontSize=17)
    subtitle = ParagraphStyle("st", parent=styles["Normal"], textColor=colors.HexColor(BRAND_ORANGE),
                              fontSize=11, spaceAfter=2)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=colors.HexColor(DARK), fontSize=12)
    normal = styles["Normal"]
    small_grey = ParagraphStyle("f", parent=normal, fontSize=7, textColor=colors.grey)

    def info_table(rows: list[list[str]], widths=(6.5, 9)) -> Table:
        """Tableau clé/valeur au style uniforme du dossier."""
        t = Table(rows, colWidths=[widths[0] * cm, widths[1] * cm])
        t.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor(GREY_LINE)),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor(ROW_ALT)]),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        return t

    generated = datetime.now(timezone.utc).strftime("%d/%m/%Y à %H:%M UTC")

    story = [
        Paragraph("DÉCLARATION DE SOUPÇON", title),
        Paragraph("Dossier LBC-FT — Lutte contre le blanchiment de capitaux et le financement du terrorisme", subtitle),
        Paragraph(f"NovaBank — Agence (données simulées) · Généré le {generated}", small_grey),
        Spacer(1, 0.5 * cm),

        Paragraph("1. Référence du dossier", h2),
        info_table([
            ["N° d'alerte interne", f"ALT-{alert.id:06d}"],
            ["Niveau d'alerte", alert.level],
            ["Date de l'alerte", alert.created_at.strftime("%d/%m/%Y %H:%M")],
            ["Qualification du directeur", "FRAUDE CONFIRMÉE (confirmed_fraud)"],
            ["Date de qualification", alert.closed_at.strftime("%d/%m/%Y %H:%M") if alert.closed_at else "—"],
        ]),
        Spacer(1, 0.4 * cm),

        Paragraph("2. Identité du client concerné (KYC)", h2),
        info_table([
            ["Nom complet", f"{client.first_name} {client.last_name}"],
            ["CIN", client.cin],
            ["Profession déclarée", client.profession or "Non renseignée"],
            ["Revenu mensuel déclaré", f"{client.monthly_income:,.2f} MAD" if client.monthly_income else "Non renseigné"],
            ["Téléphone", client.phone or "Non renseigné"],
            ["Adresse", client.address or "Non renseignée"],
        ]),
        Spacer(1, 0.4 * cm),

        Paragraph("3. Compte concerné", h2),
        info_table([
            ["Numéro de compte", account.account_number],
            ["Type de compte", "Compte courant" if account.account_type == "current" else "Compte épargne"],
            ["Statut du compte", account.status],
            ["Solde au moment de l'édition", f"{account.balance:,.2f} MAD"],
        ]),
        Spacer(1, 0.4 * cm),

        Paragraph("4. Opération à l'origine du soupçon", h2),
        info_table([
            ["Référence", f"TRX-{tx.id:06d}"],
            ["Type d'opération", TYPE_LABELS.get(tx.transaction_type, tx.transaction_type)],
            ["Montant", f"{tx.amount:,.2f} MAD"],
            ["Ville", tx.city or "Non renseignée"],
            ["Date et heure", tx.created_at.strftime("%d/%m/%Y %H:%M")],
            ["Saisie par", f"{tx.created_by.first_name} {tx.created_by.last_name}" if tx.created_by else "—"],
        ]),
        Spacer(1, 0.4 * cm),
    ]

    # ----- 5. Analyse du système de détection (le cœur "IA" du dossier) --
    story.append(Paragraph("5. Analyse du système de détection", h2))
    if risk:
        story.append(info_table([
            ["Score de risque", f"{risk.score}/100"],
            ["Niveau de confiance", risk.confidence_level],
            ["Moteur ayant produit le score", risk.model_version],
            ["Explication", risk.explanation],
        ]))
        # Contributions SHAP : la justification variable par variable de la
        # décision du modèle — l'exigence d'explicabilité appliquée à un
        # document réglementaire (un enquêteur doit comprendre POURQUOI).
        if risk.shap_values:
            story.append(Spacer(1, 0.25 * cm))
            story.append(Paragraph(
                "Contributions des variables à la décision (méthode SHAP) — une valeur positive "
                "pousse le score vers la fraude, une valeur négative vers le comportement normal :",
                normal,
            ))
            story.append(Spacer(1, 0.15 * cm))
            shap_rows = [["Variable analysée", "Contribution", "Effet"]]
            ordered = sorted(risk.shap_values.items(), key=lambda kv: abs(kv[1]), reverse=True)
            for name, value in ordered:
                shap_rows.append([
                    FEATURE_LABELS.get(name, name),
                    f"{value:+.3f}",
                    "vers la fraude" if value > 0 else "vers le normal",
                ])
            shap_table = Table(shap_rows, colWidths=[9 * cm, 3 * cm, 3.5 * cm])
            shap_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(DARK)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor(GREY_LINE)),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor(ROW_ALT)]),
                ("PADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(shap_table)
    else:
        story.append(Paragraph("Aucun score de risque enregistré pour cette opération.", normal))
    story.append(Spacer(1, 0.4 * cm))

    # ----- 6. Chronologie du compte (contexte de l'opération) ------------
    story.append(Paragraph("6. Chronologie des opérations récentes du compte", h2))
    history = db.scalars(
        select(Transaction)
        .where(Transaction.account_id == account.id)
        .order_by(Transaction.created_at.desc())
        .limit(15)
    ).all()
    hist_rows = [["Date", "Type", "Montant (MAD)", "Ville", "Score"]]
    for h in history:
        marker = " ◀ opération déclarée" if h.id == tx.id else ""
        hist_rows.append([
            h.created_at.strftime("%d/%m/%Y %H:%M"),
            TYPE_LABELS.get(h.transaction_type, h.transaction_type),
            f"{h.amount:,.2f}",
            (h.city or "—") + marker,
            str(h.risk_score.score) if h.risk_score else "—",
        ])
    hist_table = Table(hist_rows, colWidths=[3.2 * cm, 2.4 * cm, 3 * cm, 4.9 * cm, 2 * cm])
    hist_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(BRAND_ORANGE)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor(GREY_LINE)),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor(ROW_ALT)]),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(hist_table)
    story.append(Spacer(1, 0.4 * cm))

    # ----- 7. Cadre légal (formulation prudente, modèle indicatif) -------
    story += [
        Paragraph("7. Cadre légal de référence", h2),
        Paragraph(
            "La présente déclaration s'inscrit dans le cadre du dispositif marocain de lutte "
            "contre le blanchiment de capitaux et le financement du terrorisme, notamment la "
            "loi n° 43-05 (telle que modifiée et complétée) qui impose aux établissements "
            "assujettis une obligation de vigilance et de déclaration des opérations suspectes "
            "auprès de l'Autorité Nationale du Renseignement Financier (ANRF). "
            "Le déclarant bénéficie de la confidentialité prévue par la loi ; la déclaration "
            "ne doit en aucun cas être portée à la connaissance du client concerné.",
            normal,
        ),
        Spacer(1, 0.6 * cm),
        Paragraph(
            "Document généré automatiquement par la plateforme NovaBank à partir de données "
            "entièrement simulées — MODÈLE INDICATIF à usage pédagogique, ne constitue pas "
            "un formulaire officiel de déclaration auprès de l'ANRF.",
            small_grey,
        ),
    ]

    doc.build(story)
    return buffer.getvalue()
