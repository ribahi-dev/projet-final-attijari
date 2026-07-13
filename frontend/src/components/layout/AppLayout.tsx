// Gabarit applicatif : sidebar (desktop) OU barre basse (mobile) + contenu.
import { motion } from "framer-motion";
import { Landmark } from "lucide-react";
import { useEffect, useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import { BottomNav } from "./BottomNav";
import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";

export function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);
  // La marge latérale ne s'applique QUE sur desktop (>= 1024px). Sur mobile
  // la sidebar est masquée, donc marge nulle et navigation par barre basse.
  const [isDesktop, setIsDesktop] = useState(
    typeof window !== "undefined" ? window.matchMedia("(min-width: 1024px)").matches : true
  );
  const location = useLocation();

  useEffect(() => {
    const mq = window.matchMedia("(min-width: 1024px)");
    const onChange = () => setIsDesktop(mq.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);

  return (
    <div className="min-h-screen">
      <div className="app-backdrop" />
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

      {/* En-tête de marque compact, mobile uniquement */}
      <header className="glass sticky top-0 z-30 flex h-14 items-center gap-2 border-b border-border px-4 lg:hidden">
        <div className="bg-brand-gradient grid h-8 w-8 place-items-center rounded-lg text-white">
          <Landmark size={16} />
        </div>
        <span className="text-[15px] font-bold">
          Nova<span className="text-primary">Bank</span>
        </span>
      </header>

      <div
        className="transition-[margin] duration-300"
        style={{ marginLeft: isDesktop ? (collapsed ? 76 : 248) : 0 }}
      >
        {/* La navbar de recherche/thème reste réservée au desktop */}
        <div className="hidden lg:block">
          <Navbar />
        </div>
        <motion.main
          key={location.pathname}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25, ease: "easeOut" }}
          className="mx-auto max-w-[1440px] p-4 pb-24 sm:p-6 lg:p-8 lg:pb-8"
        >
          <Outlet />
        </motion.main>
      </div>

      <BottomNav />
    </div>
  );
}

export function PageHeader({
  title,
  subtitle,
  actions,
}: {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}) {
  return (
    <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 className="text-[22px] font-bold tracking-tight">{title}</h1>
        {subtitle && <p className="mt-0.5 text-[13.5px] text-muted-foreground">{subtitle}</p>}
      </div>
      {actions}
    </div>
  );
}
