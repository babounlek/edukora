import { cn } from "@/lib/utils"

/**
 * Nom d'un opérateur Mobile Money en version sobre (pied de page) : pastille neutre au contour fin, avec un point de la
 * couleur de marque. Les aplats pleins restent sur les pages où l'élève choisit son opérateur (voir SubscribePage) ; ici
 * ils dominaient une ligne faite pour rassurer, et le texte blanc sur l'orange n'atteignait pas le contraste requis.
 * Pas de logo : droits d'usage non établis.
 */
const COULEURS = {
  ORANGE: "bg-[#FF7900]",
  MTN: "bg-[#FFCC08]",
} as const

export function PastilleOperateur({
  operateur,
  children,
  className,
}: {
  operateur: keyof typeof COULEURS
  children: string
  className?: string
}) {
  return (
    <span
      data-operateur={operateur}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md border border-border bg-background/60 px-2 py-0.5 text-[0.7rem] font-medium text-foreground/70",
        className,
      )}
    >
      <span aria-hidden="true" className={cn("size-2 shrink-0 rounded-full ring-1 ring-black/10", COULEURS[operateur])} />
      {children}
    </span>
  )
}
