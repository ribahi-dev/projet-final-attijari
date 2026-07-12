// Suivi de la fraude & santé du modèle (directeur) — MLOps.
//
// Le principe : un modèle de fraude se DÉGRADE avec le temps (les fraudeurs
// s'adaptent — dérive conceptuelle). Cette page surveille sa performance
// RÉELLE en production, calculée sur les qualifications du directeur (boucle
// de feedback) — pas sur le jeu de test d'entraînement. Elle s'inspire du
// « Suivi de la fraude » publié par Bank Al-Maghrib.
import { Activity, Clock3, Cpu, Database, Target, ThumbsDown } from "lucide-react";
import { useEffect, useState } from "react";
import api from "@/api/client";
import type { ModelHealth } from "@/api/types";
import { PageHeader } from "@/components/layout/AppLayout";
import { KpiCard } from "@/components/shared/KpiCard";
import { chartLayout, Plot } from "@/components/shared/Plot";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useTheme } from "@/contexts/ThemeContext";

const pct = (v: number | null) => (v === null ? "—" : `${(v * 100).toFixed(0)} %`);

export default function SanteModele() {
  const { theme } = useTheme();
  const dark = theme === "dark";
  const [health, setHealth] = useState<ModelHealth | null>(null);

  useEffect(() => {
    api.get<ModelHealth>("/analytics/model-health").then(({ data }) => setHealth(data));
  }, []);

  return (
    <>
      <PageHeader
        title="Suivi de la fraude & santé du modèle"
        subtitle="Performance réelle du moteur IA, mesurée sur les décisions de l'agence"
        actions={
          health?.model_version ? (
            <Badge tone={health.model_version.startsWith("ml") ? "primary" : "warning"}>
              <Cpu size={13} /> moteur actif : {health.model_version}
            </Badge>
          ) : undefined
        }
      />

      {!health ? (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
          <KpiCard
            index={0}
            label="Précision en production"
            value={pct(health.precision_production)}
            sub="fraudes confirmées / alertes qualifiées"
            icon={Target}
            danger={health.precision_production !== null && health.precision_production < 0.5}
          />
          <KpiCard
            index={1}
            label="Taux de faux positifs"
            value={pct(health.false_positive_rate)}
            sub="alertes à tort (charge de travail inutile)"
            icon={ThumbsDown}
            danger={health.false_positive_rate !== null && health.false_positive_rate > 0.5}
          />
          <KpiCard
            index={2}
            label="Alertes qualifiées"
            value={health.alerts_processed}
            sub={`${health.open_alerts} encore en attente`}
            icon={Activity}
          />
          <KpiCard
            index={3}
            label="Feedback disponible"
            value={health.feedback_available}
            sub="étiquettes pour le prochain réentraînement"
            icon={Database}
          />
          <KpiCard
            index={4}
            label="Temps de traitement"
            value={health.avg_processing_hours === null ? "—" : `${health.avg_processing_hours.toFixed(1)} h`}
            sub="moyenne création → clôture"
            icon={Clock3}
          />
        </div>
      )}

      <div className="mt-6 grid gap-4 xl:grid-cols-5">
        <Card className="xl:col-span-3">
          <CardHeader>
            <CardTitle>Distribution des scores de risque</CardTitle>
          </CardHeader>
          {!health ? (
            <Skeleton className="h-72" />
          ) : health.score_distribution.length === 0 ? (
            <div className="grid h-72 place-items-center text-sm text-muted-foreground">
              Aucune transaction scorée pour l'instant.
            </div>
          ) : (
            <Plot
              data={[
                {
                  x: health.score_distribution.map((b) =>
                    b.range_start === 90 ? "90-100" : `${b.range_start}-${b.range_start + 9}`
                  ),
                  y: health.score_distribution.map((b) => b.count),
                  type: "bar",
                  // Tranches ≥ 70 en rouge : c'est la zone qui déclenche une alerte.
                  marker: {
                    color: health.score_distribution.map((b) =>
                      b.range_start >= 70 ? "#d64545" : "#f08100"
                    ),
                    opacity: 0.9,
                  },
                  hovertemplate: "%{y} transactions<extra></extra>",
                },
              ]}
              layout={chartLayout(dark, {
                height: 300,
                xaxis: { title: { text: "score de risque" } },
                yaxis: { title: { text: "transactions" } },
              })}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: "100%" }}
            />
          )}
        </Card>

        <Card glass className="xl:col-span-2 self-start">
          <CardHeader>
            <CardTitle>Pourquoi surveiller le modèle ?</CardTitle>
          </CardHeader>
          <div className="space-y-3 text-[13px] leading-relaxed text-muted-foreground">
            <p>
              Les fraudeurs <strong className="text-foreground">adaptent leurs techniques</strong> :
              un modèle performant aujourd'hui se dégrade silencieusement (dérive conceptuelle).
              Les métriques de cette page sont calculées sur les{" "}
              <strong className="text-foreground">qualifications réelles du directeur</strong>,
              pas sur le jeu de test d'origine — c'est la santé vécue par l'agence.
            </p>
            <p>
              <strong className="text-foreground">Précision en chute</strong> → le modèle crie au
              loup : chaque faux positif coûte du temps d'enquête et fragilise la confiance des
              équipes dans l'outil.
            </p>
            <p>
              <strong className="text-foreground">Quand réentraîner ?</strong> Dès que le volume de
              feedback devient significatif (≥ 50 étiquettes) ou si la précision passe sous 50 % :
              les qualifications accumulées deviennent alors des exemples d'entraînement
              (<code className="text-primary">scripts/train_model.py</code>) et le modèle apprend
              des décisions de l'agence.
            </p>
            {health && health.total_scored > 0 && (
              <p className="rounded-lg border border-border bg-card/60 p-3">
                {health.total_scored} transactions scorées au total par le moteur{" "}
                <code className="text-primary">{health.model_version}</code>.
              </p>
            )}
          </div>
        </Card>
      </div>
    </>
  );
}
