import { Flame, Sparkles, Trophy } from "lucide-react"

import type { Accueil } from "@/api/types"
import { jalonsAtteints } from "@/lib/jalons"

/**
 * Les moments candidats de l'accueil (voir components/Moments) : un palier de travail
 * franchi cette semaine, une série marquante, un thème passé en solide depuis la
 * dernière visite - dans cet ordre de rareté.
 */
export interface Moment {
  cle: string
  icone: typeof Trophy
  surtitre: string
  texte: string
}

const SERIES_MARQUANTES = [7, 30, 100]

export function momentsCandidats(accueil: Accueil): Moment[] {
  const moments: Moment[] = []
  const bilan = accueil.bilan_semaine
  if (bilan) {
    for (const jalon of jalonsAtteints(bilan)) {
      moments.push({
        cle: `jalon-${jalon.genre}-${jalon.palier}`,
        icone: Trophy,
        surtitre: "Palier franchi",
        texte: jalon.libelle,
      })
    }
  }
  const serie = accueil.plan.serie
  if (serie && serie.actif_aujourdhui && SERIES_MARQUANTES.includes(serie.jours)) {
    moments.push({
      cle: `serie-${serie.jours}`,
      icone: Flame,
      surtitre: `${serie.jours} jours de suite`,
      texte: serie.jours >= 30 ? "Ce n'est plus une habitude, c'est une méthode." : "Ça devient une habitude.",
    })
  }
  const depuis = accueil.depuis
  if (depuis && depuis.themes_consolides.length > 0) {
    const premier = depuis.themes_consolides[0]
    moments.push({
      cle: `solide-${depuis.depuis}-${premier.theme}`,
      icone: Sparkles,
      surtitre: depuis.themes_consolides_total > 1 ? "Nouveaux thèmes solides" : "Nouveau thème solide",
      texte:
        depuis.themes_consolides_total > 1
          ? `${majuscule(premier.theme)} et ${depuis.themes_consolides_total - 1} autre${depuis.themes_consolides_total > 2 ? "s" : ""}`
          : `${majuscule(premier.theme)} (${premier.subject_label})`,
    })
  }
  return moments
}


function majuscule(texte: string): string {
  return texte.charAt(0).toLocaleUpperCase("fr") + texte.slice(1)
}
