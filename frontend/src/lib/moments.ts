import { Flame, Sparkles, Trophy } from "lucide-react"

import type { Accueil } from "@/api/types"
import { jalonsAtteints } from "@/lib/jalons"
import { langueCourante, t, tn } from "@/lib/i18n"

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
        surtitre: t("moments.palier"),
        texte: jalon.libelle,
      })
    }
  }
  const serie = accueil.plan.serie
  if (serie && serie.actif_aujourdhui && SERIES_MARQUANTES.includes(serie.jours)) {
    moments.push({
      cle: `serie-${serie.jours}`,
      icone: Flame,
      surtitre: t("serie.jours_de_suite", { n: serie.jours }),
      texte: serie.jours >= 30 ? t("moments.serie_methode") : t("moments.serie_habitude"),
    })
  }
  const depuis = accueil.depuis
  if (depuis && depuis.themes_consolides.length > 0) {
    const premier = depuis.themes_consolides[0]
    moments.push({
      cle: `solide-${depuis.depuis}-${premier.theme}`,
      icone: Sparkles,
      surtitre: tn("moments.solide", depuis.themes_consolides_total > 1 ? 2 : 1),
      texte:
        depuis.themes_consolides_total > 1
          ? tn("moments.et_autres", depuis.themes_consolides_total - 1, { theme: majuscule(premier.theme) })
          : t("moments.theme_matiere", { theme: majuscule(premier.theme), matiere: premier.subject_label }),
    })
  }
  return moments
}


function majuscule(texte: string): string {
  return texte.charAt(0).toLocaleUpperCase(langueCourante()) + texte.slice(1)
}
