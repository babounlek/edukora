import { t } from "@/lib/i18n"
import type { ContextePage } from "./contextePage"

/**
 * Les textes de guide qui dépendent de ce que la page montre. Chacun reçoit ce que la page a publié
 * (voir contextePage.ts) et compose sa phrase à partir de clés i18n : rien n'est écrit en dur, et rien
 * n'est affirmé que l'écran ne montre pas. Sans publication (le centre d'aide, ouvert depuis une autre
 * page), chaque composeur retombe sur une formulation générale, vraie dans le cas courant.
 */

interface PageSeance {
  /** Libellé réel du bouton principal (« Commencer : faire un exercice », « Reprendre : … »). */
  bouton?: string
  /** Étapes réellement proposées, déjà traduites, dans l'ordre : « S'entraîner », « Vérifier »... */
  phases?: string[]
  quizExpress?: boolean
  quiz?: boolean
  verrouillee?: boolean
}

interface PageCours {
  /** Parties réellement présentes dans ce cours, déjà traduites. */
  sections?: string[]
  /** Le suivi « marquer comme compris » est offert à ce lecteur. */
  suivi?: boolean
}

interface PageExercice {
  /** Le lecteur a accès aux corrigés. */
  acces?: boolean
  /** Mode « Essaie d'abord » actif : les corrigés sont repliés. */
  essai?: boolean
}

function parcours(phases: string[]): string {
  return phases.join(" → ")
}

/** Le texte de l'aide « Comment marche ta séance ? ». */
export function texteAideSeance(page: ContextePage | undefined): string {
  const p = (page ?? {}) as PageSeance
  const morceaux = [
    p.bouton ? t("guide.seance.dyn.bouton", { bouton: p.bouton }) : t("guide.seance.dyn.bouton_generique"),
    p.phases?.length ? t("guide.seance.dyn.parcours", { parcours: parcours(p.phases) }) : t("guide.seance.dyn.parcours_generique"),
  ]
  if (p.quiz) morceaux.push(t("guide.seance.dyn.quiz_valide"))
  if (p.quizExpress) morceaux.push(t("guide.seance.dyn.express"))
  if (!p.verrouillee) morceaux.push(t("guide.seance.dyn.reglages"))
  return morceaux.join(" ")
}

/** Bienvenue, étape « Ta séance du jour » : le bouton tel qu'il est écrit à l'écran. */
export function texteBienvenueSeance(page: ContextePage | undefined): string {
  const { bouton } = (page ?? {}) as PageSeance
  return bouton ? t("guide.bienvenue.seance.dyn", { bouton }) : t("guide.bienvenue.seance.texte")
}

/** Bienvenue, étape « les étapes » : leur nombre et leur ordre réels. */
export function titreBienvenueEtapes(page: ContextePage | undefined): string {
  const n = ((page ?? {}) as PageSeance).phases?.length ?? 0
  if (n === 1) return t("guide.bienvenue.etapes.titre_1")
  if (n === 2) return t("guide.bienvenue.etapes.titre_2")
  if (n === 3) return t("guide.bienvenue.etapes.titre")
  return t("guide.bienvenue.etapes.titre_generique")
}

export function texteBienvenueEtapes(page: ContextePage | undefined): string {
  const p = (page ?? {}) as PageSeance
  if (!p.phases?.length) return t("guide.bienvenue.etapes.texte")
  const base = t("guide.bienvenue.etapes.dyn", { parcours: parcours(p.phases) })
  return p.quiz ? `${base} ${t("guide.seance.dyn.quiz_valide")}` : base
}

/** Découverte (séance verrouillée) : ce que l'abonnement ouvre, d'après le parcours affiché. */
export function texteDecouverteContenu(page: ContextePage | undefined): string {
  const { phases } = (page ?? {}) as PageSeance
  return phases?.length ? t("guide.decouverte.contenu.dyn", { parcours: parcours(phases) }) : t("guide.decouverte.contenu.texte")
}

export function texteAideCours(page: ContextePage | undefined): string {
  const p = (page ?? {}) as PageCours
  if (!p.sections?.length) return t("guide.cours.texte")
  const base = t("guide.cours.dyn", { sections: p.sections.join(", ") })
  return p.suivi ? `${base} ${t("guide.cours.dyn_suivi")}` : base
}

export function texteAideExercice(page: ContextePage | undefined): string {
  const p = (page ?? {}) as PageExercice
  if (p.acces === undefined) return t("guide.exercice.texte")
  if (!p.acces) return t("guide.exercice.dyn_verrouille")
  return p.essai ? t("guide.exercice.texte") : t("guide.exercice.dyn_tout")
}
