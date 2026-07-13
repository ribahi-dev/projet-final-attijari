// Menu de navigation par rôle — source de vérité UNIQUE, partagée entre la
// sidebar (desktop) et la barre basse (mobile). Sur mobile, seules les 4
// premières entrées de chaque rôle deviennent des raccourcis directs, donc
// l'ORDRE compte : on place en tête ce qui sert le plus au quotidien.
import {
  ArrowLeftRight, Banknote, Bot, FileBarChart2, HeartPulse, LayoutDashboard,
  ScrollText, ShieldAlert, ShieldCheck, UserSearch, Users, Wallet,
} from "lucide-react";
import type { Role } from "@/api/types";

export type MenuItem = { to: string; label: string; icon: typeof Users };

export const MENU: Record<Role, MenuItem[]> = {
  advisor: [
    { to: "/operations/nouvelle", label: "Opération", icon: Banknote },
    { to: "/clients", label: "Clients", icon: Users },
    { to: "/comptes", label: "Comptes", icon: Wallet },
    { to: "/transactions", label: "Transactions", icon: ArrowLeftRight },
    { to: "/assistant", label: "Assistant IA", icon: Bot },
  ],
  director: [
    // Priorité mobile du directeur : les alertes de fraude d'abord.
    { to: "/fraude", label: "Fraude", icon: ShieldAlert },
    { to: "/dashboard", label: "Tableau de bord", icon: LayoutDashboard },
    { to: "/sante-modele", label: "Santé modèle", icon: HeartPulse },
    { to: "/fraude-interne", label: "Fraude interne", icon: UserSearch },
    { to: "/clients", label: "Clients", icon: Users },
    { to: "/comptes", label: "Comptes", icon: Wallet },
    { to: "/transactions", label: "Transactions", icon: ArrowLeftRight },
    { to: "/rapports", label: "Rapports", icon: FileBarChart2 },
    { to: "/assistant", label: "Assistant IA", icon: Bot },
  ],
  admin: [
    { to: "/users", label: "Utilisateurs", icon: ShieldCheck },
    { to: "/audit", label: "Journal d'audit", icon: ScrollText },
  ],
};
