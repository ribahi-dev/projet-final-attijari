// Card — surface principale de l'interface (option verre : <Card glass>).
import { forwardRef, type HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  glass?: boolean;
}

// forwardRef : certaines pages ont besoin de la ref (ex. auto-scroll mobile
// vers le détail d'une alerte).
export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, glass, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "rounded-xl2 border border-border bg-card text-card-foreground p-5",
        glass ? "glass" : "shadow-[var(--shadow-soft)]",
        className
      )}
      {...props}
    />
  )
);
Card.displayName = "Card";

export function CardHeader({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("mb-4 flex items-start justify-between gap-3", className)} {...props} />;
}

export function CardTitle({ className, ...props }: HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={cn("text-[15px] font-semibold", className)} {...props} />;
}
