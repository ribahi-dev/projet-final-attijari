// Paramètres : profil, thème, notifications Telegram, seuil d'alerte, à propos.
import { Gauge, Link2, Moon, Send, Sun } from "lucide-react";
import { useEffect, useState } from "react";
import api, { apiError } from "@/api/client";
import { PageHeader } from "@/components/layout/AppLayout";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { ROLE_LABEL, useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";
import { useToast } from "@/contexts/ToastContext";
import { fmtDate } from "@/lib/format";

export default function Settings() {
  const { user } = useAuth();
  const { theme, toggle } = useTheme();
  const { toast } = useToast();
  const [linked, setLinked] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  // Seuil d'alerte (directeur) : la molette de gouvernance de la détection.
  const [threshold, setThreshold] = useState<number | null>(null);
  const [overridden, setOverridden] = useState(false);
  const isDirector = user?.role === "director";

  useEffect(() => {
    if (!isDirector) return;
    api.get<{ threshold: number; overridden: boolean }>("/agency-settings/alert-threshold")
      .then(({ data }) => {
        setThreshold(data.threshold);
        setOverridden(data.overridden);
      });
  }, [isDirector]);

  if (!user) return null;

  async function saveThreshold() {
    if (threshold === null) return;
    setBusy(true);
    try {
      const { data } = await api.patch("/agency-settings/alert-threshold", { threshold });
      setOverridden(data.overridden);
      toast("success", `Seuil d'alerte fixé à ${data.threshold}/100 — décision tracée dans l'audit.`);
    } catch (err) {
      toast("error", apiError(err));
    } finally {
      setBusy(false);
    }
  }

  async function linkTelegram() {
    setBusy(true);
    try {
      const { data } = await api.post("/notifications/telegram/link-me");
      setLinked(data.name);
      toast("success", `Telegram lié au chat de ${data.name} ✅`);
    } catch (err) {
      toast("error", apiError(err, "Envoyez d'abord /start à votre bot, puis réessayez."));
    } finally {
      setBusy(false);
    }
  }

  async function sendTest() {
    setBusy(true);
    try {
      await api.post("/notifications/test");
      toast("success", "Notification de test envoyée — vérifiez Telegram 📱");
    } catch (err) {
      toast("error", apiError(err, "Aucun canal configuré."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <PageHeader title="Paramètres" subtitle="Profil et préférences de l'application" />
      <div className="grid max-w-4xl gap-4 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Mon profil</CardTitle></CardHeader>
          <dl className="grid grid-cols-[130px_1fr] gap-y-2.5 text-sm">
            <dt className="text-muted-foreground">Nom</dt>
            <dd className="font-semibold">{user.first_name} {user.last_name}</dd>
            <dt className="text-muted-foreground">Email</dt><dd>{user.email}</dd>
            <dt className="text-muted-foreground">Rôle</dt>
            <dd><Badge tone="primary">{ROLE_LABEL[user.role]}</Badge></dd>
            <dt className="text-muted-foreground">Membre depuis</dt><dd>{fmtDate(user.created_at)}</dd>
          </dl>
          <p className="mt-4 text-xs text-muted-foreground">
            La modification du mot de passe passe par l'administrateur (procédure sécurisée).
          </p>
        </Card>

        <Card>
          <CardHeader><CardTitle>Apparence</CardTitle></CardHeader>
          <p className="mb-4 text-sm text-muted-foreground">
            Thème actuel : <strong className="text-foreground">{theme === "dark" ? "sombre" : "clair"}</strong>
          </p>
          <Button variant="secondary" onClick={toggle}>
            {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
            Passer en mode {theme === "dark" ? "clair" : "sombre"}
          </Button>
          <p className="mt-4 text-xs text-muted-foreground">
            Préférence enregistrée sur cet appareil. Le mode sombre est appliqué à tous les écrans, graphiques compris.
          </p>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Send size={16} className="text-primary" /> Notifications Telegram
            </CardTitle>
            <Badge tone={user.telegram_chat_id || linked ? "success" : "neutral"}>
              {user.telegram_chat_id || linked ? "lié" : "non lié"}
            </Badge>
          </CardHeader>
          <p className="mb-3 text-sm text-muted-foreground">
            Recevez les alertes de fraude directement sur Telegram. Ouvrez votre bot,
            envoyez-lui <code className="rounded bg-muted px-1.5 py-0.5">/start</code>, puis
            cliquez sur « Lier mon Telegram » : votre identifiant est capté automatiquement.
          </p>
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={linkTelegram} disabled={busy}>
              <Link2 size={16} /> Lier mon Telegram
            </Button>
            <Button onClick={sendTest} disabled={busy}>
              <Send size={16} /> Envoyer une notification de test
            </Button>
          </div>
          {linked && (
            <p className="mt-3 text-sm text-success">✅ Compte Telegram de {linked} lié à ce profil.</p>
          )}
        </Card>

        {isDirector && threshold !== null && (
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Gauge size={16} className="text-primary" /> Seuil d'alerte de l'agence
              </CardTitle>
              <Badge tone={overridden ? "primary" : "neutral"}>
                {overridden ? "personnalisé" : "valeur par défaut"}
              </Badge>
            </CardHeader>
            <p className="mb-4 text-sm text-muted-foreground">
              Une transaction dont le score atteint ce seuil crée une alerte et notifie le
              directeur. <strong className="text-foreground">Seuil bas</strong> : moins de fraudes
              ratées, plus de faux positifs. <strong className="text-foreground">Seuil haut</strong> :
              moins de bruit, plus de risque. Consultez la page « Santé du modèle » pour décider —
              chaque changement est tracé dans le journal d'audit.
            </p>
            <div className="flex flex-wrap items-center gap-4">
              <input
                type="range" min={1} max={100} value={threshold}
                onChange={(e) => setThreshold(Number(e.target.value))}
                className="h-2 w-64 cursor-pointer appearance-none rounded-full bg-muted accent-[var(--primary)]"
                aria-label="Seuil d'alerte"
              />
              <span className={`w-20 text-2xl font-bold ${threshold >= 85 ? "text-success" : threshold < 50 ? "text-danger" : "text-primary"}`}>
                {threshold}<span className="text-sm text-muted-foreground">/100</span>
              </span>
              <Button onClick={saveThreshold} disabled={busy}>Appliquer le seuil</Button>
            </div>
          </Card>
        )}

        <Card className="md:col-span-2">
          <CardHeader><CardTitle>À propos de la plateforme</CardTitle></CardHeader>
          <div className="grid gap-3 text-sm sm:grid-cols-3">
            <div>
              <div className="text-muted-foreground">Version</div>
              <div className="font-semibold">NovaBank PFE 2.1</div>
            </div>
            <div>
              <div className="text-muted-foreground">Moteur de risque</div>
              <div className="font-semibold">ml-rf-v2.1 · repli règles</div>
            </div>
            <div>
              <div className="text-muted-foreground">Sécurité</div>
              <div className="font-semibold">JWT · RBAC · Audit</div>
            </div>
          </div>
        </Card>
      </div>
    </>
  );
}
