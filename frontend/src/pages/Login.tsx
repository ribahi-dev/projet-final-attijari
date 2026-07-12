// Connexion — vitrine 3D du projet.
//
// La carte est un VRAI objet 3D : un conteneur en perspective, une carte
// qui s'incline en suivant la souris (springs Framer Motion), et des
// éléments internes étagés en profondeur (translateZ + preserve-3d) — le
// logo, le titre et les champs "flottent" à des altitudes différentes.
// Un reflet (glare) suit le curseur comme sur une carte bancaire réelle.
// Le fond est une aurora animée (orbes + particules) en pur Framer Motion.
import {
  motion, useMotionTemplate, useMotionValue, useSpring, useTransform,
} from "framer-motion";
import { Landmark, Lock, Mail, ShieldCheck, Sparkles, TrendingUp } from "lucide-react";
import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiError } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Field, Input } from "@/components/ui/input";
import { ROLE_HOME, useAuth } from "@/contexts/AuthContext";

const FEATURES = [
  { icon: TrendingUp, text: "Pilotage temps réel de l'activité de l'agence" },
  { icon: Sparkles, text: "Score de risque IA expliqué pour chaque opération" },
  { icon: ShieldCheck, text: "Sécurité bancaire : JWT, RBAC, journal d'audit" },
];

// Particules déterministes (pas de Math.random au rendu : positions stables).
const PARTICLES = Array.from({ length: 16 }, (_, i) => ({
  left: (i * 61) % 100,
  size: 2 + (i % 3) * 2,
  duration: 9 + (i % 5) * 3,
  delay: (i * 0.9) % 7,
  opacity: 0.15 + (i % 4) * 0.08,
}));

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  // ----- Moteur 3D de la carte -------------------------------------------
  // Position de la souris normalisée [-0.5, 0.5], lissée par des ressorts :
  // la carte "rattrape" le curseur avec une inertie naturelle.
  const cardRef = useRef<HTMLDivElement>(null);
  const mx = useMotionValue(0);
  const my = useMotionValue(0);
  const smx = useSpring(mx, { stiffness: 140, damping: 18 });
  const smy = useSpring(my, { stiffness: 140, damping: 18 });
  const rotateX = useTransform(smy, [-0.5, 0.5], ["10deg", "-10deg"]);
  const rotateY = useTransform(smx, [-0.5, 0.5], ["-12deg", "12deg"]);
  // Reflet : un halo lumineux qui suit le curseur sur la surface.
  const glareX = useTransform(smx, [-0.5, 0.5], ["20%", "80%"]);
  const glareY = useTransform(smy, [-0.5, 0.5], ["15%", "85%"]);
  const glare = useMotionTemplate`radial-gradient(320px circle at ${glareX} ${glareY}, rgba(255,255,255,0.55), transparent 65%)`;

  function onMouseMove(e: React.MouseEvent<HTMLDivElement>) {
    const rect = cardRef.current?.getBoundingClientRect();
    if (!rect) return;
    mx.set((e.clientX - rect.left) / rect.width - 0.5);
    my.set((e.clientY - rect.top) / rect.height - 0.5);
  }

  function onMouseLeave() {
    mx.set(0);
    my.set(0);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const user = await login(email, password);
      navigate(ROLE_HOME[user.role]);
    } catch (err) {
      setError(apiError(err, "Connexion impossible — vérifiez le serveur."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="relative grid min-h-screen place-items-center overflow-hidden bg-[#12100d] p-4">
      {/* ----- Fond : aurora de marque animée ----- */}
      <div className="absolute inset-0 bg-brand-gradient opacity-80" />
      <motion.div
        className="absolute -left-40 -top-40 h-[30rem] w-[30rem] rounded-full bg-[#ffb347]/40 blur-3xl"
        animate={{ x: [0, 60, 0], y: [0, 40, 0], scale: [1, 1.15, 1] }}
        transition={{ duration: 16, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute -bottom-48 -right-32 h-[34rem] w-[34rem] rounded-full bg-[#3a2a12]/60 blur-3xl"
        animate={{ x: [0, -50, 0], y: [0, -35, 0], scale: [1, 1.1, 1] }}
        transition={{ duration: 19, repeat: Infinity, ease: "easeInOut", delay: 2 }}
      />
      <motion.div
        className="absolute left-1/3 top-1/2 h-72 w-72 rounded-full bg-white/12 blur-3xl"
        animate={{ x: [0, 80, -40, 0], y: [0, -60, 30, 0] }}
        transition={{ duration: 24, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Particules qui s'élèvent lentement (poussière dorée) */}
      {PARTICLES.map((p, i) => (
        <motion.span
          key={i}
          className="absolute rounded-full bg-white"
          style={{ left: `${p.left}%`, width: p.size, height: p.size, opacity: p.opacity }}
          initial={{ y: "105vh" }}
          animate={{ y: "-5vh" }}
          transition={{ duration: p.duration, delay: p.delay, repeat: Infinity, ease: "linear" }}
        />
      ))}

      <div className="relative z-10 grid w-full max-w-5xl gap-10 lg:grid-cols-2 lg:items-center">
        {/* ----- Présentation (parallaxe légère inversée) ----- */}
        <motion.div
          initial={{ opacity: 0, x: -24 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          style={{
            x: useTransform(smx, [-0.5, 0.5], [8, -8]),
            y: useTransform(smy, [-0.5, 0.5], [5, -5]),
          }}
          className="hidden text-white lg:block"
        >
          <div className="mb-6 flex items-center gap-3">
            {/* Le médaillon entre en pièce de monnaie (flip 3D) puis lévite */}
            <motion.div
              initial={{ rotateY: 180, opacity: 0 }}
              animate={{ rotateY: 0, opacity: 1 }}
              transition={{ type: "spring", stiffness: 60, damping: 12, delay: 0.15 }}
              className="grid h-12 w-12 place-items-center rounded-2xl bg-white/15 backdrop-blur"
            >
              <motion.span
                animate={{ y: [0, -4, 0] }}
                transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut" }}
              >
                <Landmark size={24} />
              </motion.span>
            </motion.div>
            <div className="text-3xl font-bold">
              Nova<span className="text-[#2b2117]">Bank</span>
            </div>
          </div>
          <h1 className="mb-3 text-4xl font-bold leading-tight">
            La décision bancaire,
            <br />
            éclairée par l'IA.
          </h1>
          <p className="mb-8 max-w-md text-white/85">
            Plateforme intelligente d'aide à la décision pour l'agence :
            gestion, analyse, détection d'anomalies et cybersécurité.
          </p>
          <div className="space-y-3.5">
            {FEATURES.map(({ icon: Icon, text }, i) => (
              <motion.div
                key={text}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.25 + i * 0.12 }}
                className="flex items-center gap-3 text-[15px]"
              >
                <span className="grid h-8 w-8 place-items-center rounded-lg bg-white/15">
                  <Icon size={16} />
                </span>
                {text}
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* ----- Carte 3D (perspective + inclinaison + profondeur) ----- */}
        <div style={{ perspective: 1400 }} className="mx-auto w-full max-w-md">
          <motion.div
            ref={cardRef}
            onMouseMove={onMouseMove}
            onMouseLeave={onMouseLeave}
            initial={{ opacity: 0, y: 40, rotateX: 18 }}
            animate={{ opacity: 1, y: 0, rotateX: 0 }}
            transition={{ type: "spring", stiffness: 70, damping: 14, delay: 0.1 }}
            style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
            className="glass relative rounded-2xl p-8 !bg-white/92 shadow-[0_35px_70px_-15px_rgba(0,0,0,0.45)] dark:!bg-white/92"
          >
            {/* Reflet qui suit le curseur (comme une carte bancaire) */}
            <motion.div
              aria-hidden
              className="pointer-events-none absolute inset-0 rounded-2xl mix-blend-soft-light"
              style={{ background: glare }}
            />
            {/* Liseré lumineux */}
            <div aria-hidden className="pointer-events-none absolute inset-0 rounded-2xl ring-1 ring-white/60" />

            {/* Chaque étage a sa profondeur : le contenu "flotte" dans la carte */}
            <div style={{ transform: "translateZ(45px)", transformStyle: "preserve-3d" }}>
              <h2 className="text-2xl font-bold text-[#1c2024]">Connexion</h2>
              <p className="mb-6 mt-1 text-sm text-[#64707d]">
                Accédez à votre espace de travail sécurisé
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div style={{ transform: "translateZ(30px)" }}>
                <Field label="Email professionnel">
                  <div className="relative">
                    <Mail size={16} className="absolute left-3 top-1/2 z-10 -translate-y-1/2 text-[#98a2ae]" />
                    <Input
                      type="email"
                      required
                      placeholder="prenom@novabank.ma"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="!bg-white pl-9 !text-[#1c2024] transition-shadow focus:shadow-[0_0_0_4px_rgba(240,129,0,0.15),0_8px_20px_-6px_rgba(240,129,0,0.35)]"
                    />
                  </div>
                </Field>
              </div>
              <div style={{ transform: "translateZ(30px)" }}>
                <Field label="Mot de passe">
                  <div className="relative">
                    <Lock size={16} className="absolute left-3 top-1/2 z-10 -translate-y-1/2 text-[#98a2ae]" />
                    <Input
                      type="password"
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="!bg-white pl-9 !text-[#1c2024] transition-shadow focus:shadow-[0_0_0_4px_rgba(240,129,0,0.15),0_8px_20px_-6px_rgba(240,129,0,0.35)]"
                    />
                  </div>
                </Field>
              </div>
              {error && (
                <motion.div
                  initial={{ opacity: 0, x: 0 }}
                  animate={{ opacity: 1, x: [0, -8, 8, -5, 5, 0] }}
                  transition={{ duration: 0.45 }}
                  style={{ transform: "translateZ(25px)" }}
                  className="rounded-lg border border-danger/30 bg-danger/10 px-3.5 py-2.5 text-sm text-danger"
                >
                  {error}
                </motion.div>
              )}
              <motion.div
                style={{ transform: "translateZ(40px)" }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.97 }}
              >
                <Button className="group relative w-full overflow-hidden" size="lg" disabled={busy}>
                  {/* Balayage lumineux au survol */}
                  <span
                    aria-hidden
                    className="absolute inset-y-0 -left-1/2 w-1/3 -skew-x-12 bg-white/30 opacity-0 blur-sm transition-all duration-700 group-hover:left-[120%] group-hover:opacity-100"
                  />
                  {busy ? "Connexion…" : "Se connecter"}
                </Button>
              </motion.div>
            </form>

            <p
              style={{ transform: "translateZ(20px)" }}
              className="mt-5 text-center text-[11px] tracking-wide text-[#98a2ae]"
            >
              🔒 Connexion chiffrée · comptes verrouillés après 5 échecs
            </p>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
