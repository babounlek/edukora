import type { ReactNode } from "react"
import { Menu } from "lucide-react"

import { Logo } from "@/components/Logo"
import { t, useI18n } from "@/lib/i18n"

/**
 * Sur un grand écran, la carte « première séance » du hero est montrée dans un téléphone : le visiteur voit une
 * application, pas un formulaire posé sur une page (audit visuel de l'accueil, 2026-11-23 : aucune image du produit).
 * Le contenu reste la vraie carte, avec ses vrais boutons ; seul le cadre est décor.
 *
 * Sous `lg`, rien de tout cela : sur un téléphone la carte est déjà dans un téléphone, et entre `md` et `lg` la colonne
 * est trop étroite pour un cadre (les examens passeraient à un par ligne).
 *
 * `lg:min-h-[27.25rem]` réserve la hauteur de la carte dans ses deux états (la question, puis la séance) : c'est aussi la
 * hauteur que posent la coquille statique de index.html et CoquilleAccueil, pour que le titre du hero ne bouge pas
 * quand la carte arrive. Changer ces classes oblige à changer les deux autres.
 */
export function CadreTelephone({ children, decor = true }: {
  children: ReactNode
  /** `false` pour la coquille affichée avant les données : le cadre seul, sans logo ni carte flottante. */
  decor?: boolean
}) {
  useI18n()
  return (
    <div className="relative lg:rounded-[2rem] lg:bg-accent lg:px-10 lg:pb-24 lg:pt-8">
      <div className="lg:mx-auto lg:max-w-[22.5rem] lg:rounded-[2.5rem] lg:border-[9px] lg:border-[hsl(150_15%_10%)] lg:bg-background lg:p-2.5 lg:shadow-2xl lg:shadow-primary/20 dark:lg:border-[hsl(155_12%_30%)]">
        <div aria-hidden="true" className="hidden h-9 items-center justify-between px-2 pb-2 lg:flex">
          {decor && (
            <>
              <Logo variante="minimal" decoratif className="h-5" />
              <Menu className="size-4 text-muted-foreground" />
            </>
          )}
        </div>
        <div className="lg:grid lg:min-h-[27.25rem]">{children}</div>
      </div>
      {decor && (
        // L'autre moitié du produit, en une ligne : un corrigé qui explique. Décor, donc muet pour un lecteur d'écran -
        // la section « Un exemple, plutôt qu'une promesse », juste dessous, montre un vrai corrigé.
        <div
          aria-hidden="true"
          className="absolute bottom-4 left-5 hidden w-[17.5rem] flex-col gap-0.5 rounded-2xl border border-border bg-card px-4 py-3 shadow-lg shadow-primary/10 lg:flex"
        >
          <span className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">{t("accueil.corrige_pas_a_pas")}</span>
          {/* Neutre exprès : une formule de maths à côté d'une séance de littérature se contredisait (relevé du
              2026-11-23). Les trois temps d'un corrigé valent pour toutes les matières. */}
          <span className="flex items-center gap-1.5 text-sm font-semibold">
            {[t("accueil.cadre_methode_1"), t("accueil.cadre_methode_2"), t("accueil.cadre_methode_3")].map((etape, i) => (
              <span key={etape} className="flex items-center gap-1.5">
                {i > 0 && <span className="text-muted-foreground">→</span>}
                {etape}
              </span>
            ))}
          </span>
          <span className="text-xs text-muted-foreground">{t("accueil.cadre_methode")}</span>
        </div>
      )}
    </div>
  )
}
