import { Check, CircleDashed, RotateCcw, Star } from "lucide-react"

import { centre, estDore, frontiere, HAUTEUR_LIGNE, LARGEUR, RAYON, trace } from "@/lib/cheminParcours"
import { cn } from "@/lib/utils"

export type BucketChemin = "maitrise" | "en_revision" | "en_cours" | "a_decouvrir" | "sans_contenu"

export interface ItemChemin {
  id: number
  titre: string
  rang: number
  bucket: BucketChemin
  /** Taux de réussite (0-100) ou null : jamais pratiqué. */
  taux: number | null
  /** Part des épreuves où le thème est tombé (mode Parcours par fréquence uniquement). */
  frequencePct?: number | null
}

const LIBELLES: Record<BucketChemin, string> = {
  maitrise: "Maîtrisé",
  en_revision: "À réviser",
  en_cours: "En cours",
  a_decouvrir: "À découvrir",
  sans_contenu: "Contenu à venir",
}

// Anneau de réussite autour d'un nœud entamé : r = 29 dans un cercle de 64 de côté.
const R_ANNEAU = 29
const CIRCONFERENCE = 2 * Math.PI * R_ANNEAU

/**
 * Les thèmes d'un module comme un chemin : un nœud par thème sur un fil qui serpente, le chemin
 * déjà parcouru en trait plein, la suite en pointillé. Le nœud rempli dit l'état (coche = maîtrisé,
 * flèche de retour = à réviser, anneau = en cours), un liseré et une étoile dorés disent « tombe
 * souvent à l'examen » - le doré ne sert qu'à ça (voir lib/statutsProgression). Le prochain pas
 * recommandé pulse doucement.
 *
 * Présentationnel : le détail d'un thème (actions, quiz, cours) s'ouvre dans la page, via
 * `onSelect`, pour que la logique de lancement d'un quiz reste à un seul endroit.
 */
export function CheminParcours({
  items, prochainId, seuilOr, onSelect,
}: {
  items: ItemChemin[]
  prochainId: number | null
  seuilOr: number | null
  onSelect: (id: number) => void
}) {
  if (items.length === 0) return null
  const limite = frontiere(items.map((item) => item.bucket === "maitrise"))
  const hauteur = items.length * HAUTEUR_LIGNE

  return (
    <div className="overflow-x-auto overflow-y-hidden pb-2 pt-4">
      <div className="relative mx-auto" style={{ width: LARGEUR, height: hauteur }}>
        <svg width={LARGEUR} height={hauteur} className="absolute inset-0" aria-hidden>
          <path d={trace(0, limite)} fill="none" strokeWidth={6} strokeLinecap="round" className="stroke-primary/40" />
          <path
            d={trace(limite, items.length - 1)}
            fill="none"
            strokeWidth={4}
            strokeLinecap="round"
            strokeDasharray="2 12"
            className="stroke-border"
          />
        </svg>

        <ol>
          {items.map((item, i) => {
            const { x } = centre(i)
            const dore = estDore(item.frequencePct, seuilOr)
            const prochain = item.id === prochainId
            return (
              <li
                key={item.id}
                className="absolute flex flex-col items-center text-center"
                style={{ left: x - 70, top: i * HAUTEUR_LIGNE, width: 140 }}
              >
                {prochain && (
                  <span className="absolute -top-7 z-10 rounded-full bg-primary px-2.5 py-0.5 text-[0.7rem] font-semibold text-primary-foreground shadow-sm">
                    Commence ici
                  </span>
                )}
                <button
                  type="button"
                  onClick={() => onSelect(item.id)}
                  aria-label={`${item.titre}, ${LIBELLES[item.bucket]}${dore ? ", tombe souvent à l'examen" : ""}`}
                  className={cn(
                    "group relative flex shrink-0 items-center justify-center rounded-full font-display text-lg font-semibold tabular-nums outline-none transition-transform duration-200 hover:scale-105 focus-visible:ring-4 focus-visible:ring-ring/50 active:scale-95",
                    item.bucket === "maitrise" && "text-primary-foreground shadow-md shadow-primary/30",
                    item.bucket === "en_revision" && "text-warning-foreground dark:text-warning",
                    item.bucket === "en_cours" && "text-info",
                    (item.bucket === "a_decouvrir" || item.bucket === "sans_contenu") && "text-muted-foreground",
                    dore && "ring-4 ring-gold/50",
                  )}
                  style={{ width: RAYON * 2, height: RAYON * 2 }}
                >
                  {/* Fond opaque sous la teinte du nœud : le fil passe DERRIÈRE un nœud, il ne
                      doit jamais se voir à travers une teinte translucide. */}
                  <span aria-hidden className="absolute inset-0 rounded-full bg-card" />
                  <span
                    aria-hidden
                    className={cn(
                      "absolute inset-0 rounded-full",
                      item.bucket === "maitrise" && "bg-primary",
                      item.bucket === "en_revision" && "bg-warning/25",
                      item.bucket === "en_cours" && "bg-info/15",
                      item.bucket === "a_decouvrir" && "border-2 border-dashed border-border",
                      item.bucket === "sans_contenu" && "bg-muted opacity-60",
                    )}
                  />
                  {prochain && (
                    <span
                      aria-hidden
                      className="absolute -inset-1.5 animate-pulse rounded-full border-2 border-primary/60 motion-reduce:animate-none"
                    />
                  )}
                  {(item.bucket === "en_cours" || item.bucket === "en_revision") && item.taux !== null && (
                    <svg viewBox="0 0 64 64" className="absolute inset-0 -rotate-90" aria-hidden>
                      <circle cx="32" cy="32" r={R_ANNEAU} fill="none" strokeWidth="4" className="stroke-black/10 dark:stroke-white/10" />
                      <circle
                        cx="32"
                        cy="32"
                        r={R_ANNEAU}
                        fill="none"
                        strokeWidth="4"
                        strokeLinecap="round"
                        strokeDasharray={`${(CIRCONFERENCE * item.taux) / 100} ${CIRCONFERENCE}`}
                        className={item.bucket === "en_revision" ? "stroke-warning" : "stroke-info"}
                      />
                    </svg>
                  )}
                  <span className="relative">
                    {item.bucket === "maitrise" ? (
                      <Check className="size-7" strokeWidth={3} aria-hidden="true" />
                    ) : item.bucket === "en_revision" ? (
                      <RotateCcw className="size-6" aria-hidden="true" />
                    ) : item.bucket === "sans_contenu" ? (
                      <CircleDashed className="size-6" aria-hidden="true" />
                    ) : (
                      item.rang
                    )}
                  </span>
                  {dore && (
                    <span
                      aria-hidden
                      className="absolute -right-1.5 -top-1.5 flex size-6 items-center justify-center rounded-full bg-gold text-gold-foreground shadow-sm ring-2 ring-card"
                    >
                      <Star className="size-3.5" fill="currentColor" />
                    </span>
                  )}
                </button>
                {/* Fond de la carte : le fil qui descend vers le nœud suivant passe derrière
                    l'étiquette, jamais à travers le texte. */}
                <span className="relative mt-2 line-clamp-2 rounded-md bg-card px-1.5 text-sm font-medium leading-tight">
                  {item.titre}
                </span>
              </li>
            )
          })}
        </ol>
      </div>
    </div>
  )
}
