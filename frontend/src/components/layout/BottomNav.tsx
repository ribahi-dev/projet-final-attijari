// Barre de navigation basse — MOBILE uniquement (lg:hidden).
//
// Sur téléphone, la sidebar latérale n'a pas sa place : on la remplace par
// une barre d'onglets en bas, atteignable au pouce. On n'y met que les
// destinations ESSENTIELLES du rôle (max 5) — le reste passe par le menu
// « Plus ». Objectif directeur : atteindre les alertes en un geste.
import { MoreHorizontal } from "lucide-react";
import { useState } from "react";
import { NavLink } from "react-router-dom";
import type { Role } from "@/api/types";
import { ROLE_LABEL, useAuth } from "@/contexts/AuthContext";
import { MENU } from "./menu";
import { cn } from "@/lib/utils";

export function BottomNav() {
  const { user, logout } = useAuth();
  const [moreOpen, setMoreOpen] = useState(false);
  if (!user) return null;

  const items = MENU[user.role as Role];
  const primary = items.slice(0, 4); // 4 raccourcis + bouton « Plus »
  const overflow = [...items.slice(4), { to: "/parametres", label: "Paramètres", icon: items[0].icon }];

  return (
    <>
      {/* Feuille « Plus » */}
      {moreOpen && (
        <div className="fixed inset-0 z-40 lg:hidden" onClick={() => setMoreOpen(false)}>
          <div className="absolute inset-0 bg-black/40" />
          <div
            className="glass absolute inset-x-0 bottom-16 rounded-t-2xl border-t border-border p-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-3 px-1">
              <div className="text-sm font-semibold">{user.first_name} {user.last_name}</div>
              <div className="text-[11px] uppercase tracking-wider text-primary">{ROLE_LABEL[user.role]}</div>
            </div>
            <div className="grid grid-cols-3 gap-2">
              {overflow.map(({ to, label, icon: Icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  onClick={() => setMoreOpen(false)}
                  className="flex flex-col items-center gap-1.5 rounded-xl border border-border p-3 text-center text-[12px] active:scale-95"
                >
                  <Icon size={20} className="text-primary" />
                  <span className="leading-tight">{label}</span>
                </NavLink>
              ))}
              <button
                onClick={() => { setMoreOpen(false); logout(); }}
                className="flex flex-col items-center gap-1.5 rounded-xl border border-border p-3 text-center text-[12px] text-danger active:scale-95"
              >
                <MoreHorizontal size={20} className="rotate-90" />
                <span>Déconnexion</span>
              </button>
            </div>
          </div>
        </div>
      )}

      <nav className="glass fixed inset-x-0 bottom-0 z-30 flex h-16 items-stretch border-t border-border pb-[env(safe-area-inset-bottom)] lg:hidden">
        {primary.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                "flex flex-1 flex-col items-center justify-center gap-0.5 text-[10.5px] font-medium",
                isActive ? "text-primary" : "text-muted-foreground"
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon size={21} className={isActive ? "scale-110 transition-transform" : ""} />
                <span className="max-w-full truncate px-0.5">{label}</span>
              </>
            )}
          </NavLink>
        ))}
        <button
          onClick={() => setMoreOpen(true)}
          className="flex flex-1 flex-col items-center justify-center gap-0.5 text-[10.5px] font-medium text-muted-foreground"
        >
          <MoreHorizontal size={21} />
          <span>Plus</span>
        </button>
      </nav>
    </>
  );
}
