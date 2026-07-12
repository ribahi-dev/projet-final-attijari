// Surveillance de la fraude INTERNE (directeur) — l'angle mort classique.
//
// On surveille les clients, rarement les employés. Or les détournements en
// agence passent par un poste conseiller : saisies nocturnes, concentration
// sur un compte complice, volumes anormaux. Les indicateurs viennent des
// transactions ET du journal d'audit (append-only : l'employé ne peut pas
// effacer ses traces). Un drapeau désigne un comportement À EXAMINER —
// jamais une culpabilité : la décision reste humaine, comme pour le scoring.
import { motion } from "framer-motion";
import { ShieldQuestion, UserSearch } from "lucide-react";
import { useEffect, useState } from "react";
import api from "@/api/client";
import type { InternalMonitoring } from "@/api/types";
import { PageHeader } from "@/components/layout/AppLayout";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState, Table, Td, Th, Tr } from "@/components/ui/table";
import { TableSkeleton } from "@/components/ui/skeleton";
import { fmtMAD } from "@/lib/format";

export default function FraudeInterne() {
  const [data, setData] = useState<InternalMonitoring | null>(null);

  useEffect(() => {
    api.get<InternalMonitoring>("/analytics/internal-monitoring").then(({ data }) => setData(data));
  }, []);

  const anomalous = data?.advisors.filter((a) => a.is_anomalous).length ?? 0;

  return (
    <>
      <PageHeader
        title="Fraude interne"
        subtitle="Profils d'activité des conseillers — calculés depuis les opérations et le journal d'audit"
        actions={
          data ? (
            <Badge tone={anomalous > 0 ? "danger" : "success"}>
              {anomalous > 0 ? `${anomalous} profil(s) à examiner` : "aucune anomalie détectée"}
            </Badge>
          ) : undefined
        }
      />

      <div className="grid gap-4 xl:grid-cols-5">
        <Card className="xl:col-span-3">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <UserSearch size={17} className="text-primary" /> Activité par conseiller
            </CardTitle>
          </CardHeader>
          {!data ? (
            <TableSkeleton rows={4} />
          ) : data.advisors.length === 0 ? (
            <EmptyState>Aucun conseiller actif.</EmptyState>
          ) : (
            <Table>
              <thead>
                <tr>
                  <Th>Conseiller</Th><Th>Opérations</Th><Th>Volume</Th>
                  <Th>Nuit</Th><Th>Risque ≥ 70</Th><Th>Statut</Th>
                </tr>
              </thead>
              <tbody>
                {data.advisors.map((a) => (
                  <Tr key={a.user_id} className={a.is_anomalous ? "bg-danger/5" : ""}>
                    <Td className="font-semibold">{a.name}</Td>
                    <Td>{a.tx_count}</Td>
                    <Td>{fmtMAD(a.total_amount)}</Td>
                    <Td className={a.night_count >= 3 ? "font-bold text-danger" : ""}>{a.night_count}</Td>
                    <Td className={a.high_risk_count > 0 ? "text-warning" : ""}>{a.high_risk_count}</Td>
                    <Td>
                      <Badge tone={a.is_anomalous ? "danger" : "success"}>
                        {a.is_anomalous ? "à examiner" : "normal"}
                      </Badge>
                    </Td>
                  </Tr>
                ))}
              </tbody>
            </Table>
          )}
          {data && (
            <p className="mt-3 text-xs text-muted-foreground">
              Volume moyen des pairs : {fmtMAD(data.peer_avg_amount)} — chaque conseiller est
              comparé à cette référence.
            </p>
          )}
        </Card>

        <div className="space-y-4 xl:col-span-2">
          {data?.advisors.filter((a) => a.is_anomalous).map((a) => (
            <motion.div key={a.user_id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
              <Card glass>
                <CardHeader>
                  <CardTitle className="text-danger">{a.name}</CardTitle>
                </CardHeader>
                <ul className="space-y-1.5 text-sm">
                  {a.flags.map((f) => (
                    <li key={f} className="rounded-r-lg border-l-4 border-danger bg-danger/8 p-2.5">
                      {f}
                    </li>
                  ))}
                </ul>
              </Card>
            </motion.div>
          ))}

          <Card glass className="self-start">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShieldQuestion size={16} className="text-primary" /> Comment lire cette page ?
              </CardTitle>
            </CardHeader>
            <div className="space-y-2.5 text-[13px] leading-relaxed text-muted-foreground">
              <p>
                Les indicateurs sont calculés depuis les opérations saisies et le
                <strong className="text-foreground"> journal d'audit</strong>, que personne ne peut
                modifier (append-only). Un drapeau se lève pour : saisies nocturnes répétées,
                volume très supérieur aux pairs, concentration d'opérations sur un même compte,
                part élevée d'opérations à haut risque, échecs de connexion répétés.
              </p>
              <p>
                Un drapeau signale un comportement <strong className="text-foreground">à examiner
                avec l'intéressé</strong> — il peut avoir une explication parfaitement légitime
                (permanence, gros client). Comme pour le scoring des transactions :
                l'outil détecte, <strong className="text-foreground">l'humain décide</strong>.
              </p>
            </div>
          </Card>
        </div>
      </div>
    </>
  );
}
