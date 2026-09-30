import { cn } from "@/lib/utils"

/** Fréquence en anneau : lisible d'un coup d'œil sur une carte du podium ou un en-tête,
 * là où une barre fine se perd. Partagé par ThemesFrequentsPage et ThemeExercicesPage. */
export function AnneauFrequence({
  pct, dore, grand = false,
}: { pct: number; dore: boolean; grand?: boolean }) {
  const rayon = 26
  const circonference = 2 * Math.PI * rayon
  return (
    <div className={cn("relative shrink-0", grand ? "size-28" : "size-16")}>
      <svg viewBox="0 0 64 64" className="size-full -rotate-90" aria-hidden>
        <circle cx="32" cy="32" r={rayon} fill="none" strokeWidth="6" className="stroke-muted" />
        <circle
          cx="32"
          cy="32"
          r={rayon}
          fill="none"
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={circonference}
          strokeDashoffset={circonference * (1 - pct / 100)}
          className={cn("transition-[stroke-dashoffset] duration-700", dore ? "stroke-gold" : "stroke-primary")}
        />
      </svg>
      <span
        className={cn(
          "absolute inset-0 flex items-center justify-center font-display font-semibold tabular-nums",
          grand ? "text-2xl" : "text-base",
        )}
      >
        {pct}%
      </span>
    </div>
  )
}
