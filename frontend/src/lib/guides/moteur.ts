import { GUIDES } from "./contenu"
import { estAJour } from "./store"
import type { ContexteGuide, DefinitionGuide, DonneesGuides, EtapeGuide } from "./types"

/**
 * Les règles qui décident si un guide peut se montrer SEUL. Pures (aucun DOM, aucun
 * stockage, aucun React) : tout ce qu'elles savent leur est passé, donc tout se teste.
 *
 * Une demande explicite de l'élève (bouton « ? », centre d'aide) ne passe PAS par ici :
 * elle est toujours obéie. Ces règles ne protègent que contre l'aide qu'on lui impose.
 */

/**
 * Pages où aucune aide ne s'impose jamais : un quiz ou une copie en cours, le tunnel
 * d'abonnement et de paiement, la connexion. Une carte de plus y coûterait une réponse
 * manquée, un paiement interrompu ou un code mal saisi.
 *
 * Écrit en chemins INTERNES du routeur (le préfixe /en et les segments anglais sont
 * traduits avant lui, voir lib/i18n/segments-url.json) : la liste vaut pour les deux langues.
 */
const ROUTES_SANS_AIDE_AUTO: readonly RegExp[] = [
  // La page de CHOIX du quiz (/quiz) est permise ; tout ce qui est en dessous (session, essai,
  // résultat) ne l'est pas.
  /^\/quiz\//,
  /^\/historique\/quiz(\/|$)/,
  /^\/inedit\/tentative(\/|$)/,
  /^\/simulation(\/|$)/,
  /^\/abonnement(\/|$)/,
  /^\/mes-paiements(\/|$)/,
  /^\/connexion(\/|$)/,
]

export function routeAutoPermise(pathname: string): boolean {
  return !ROUTES_SANS_AIDE_AUTO.some((motif) => motif.test(pathname))
}

export interface SituationAuto {
  memoire: DonneesGuides
  /** Un guide est déjà affiché : on ne le remplace jamais. */
  guideOuvert: boolean
  /** Une aide automatique a déjà été montrée depuis le chargement de la page. */
  autoDejaMontre: boolean
}

/**
 * Les étapes qui ont un sens maintenant : une étape dont la cible est obligatoire et
 * absente de l'écran est sautée (elle décrirait quelque chose d'invisible), les autres
 * restent - sans mise en évidence si leur cible manque.
 */
export function etapesEffectives(
  guide: DefinitionGuide,
  ciblePresente: (cible: string) => boolean,
): EtapeGuide[] {
  return guide.etapes.filter((etape) => !(etape.cible && etape.cibleObligatoire && !ciblePresente(etape.cible)))
}

function peutSeMontrer(guide: DefinitionGuide, contexte: ContexteGuide, situation: SituationAuto): boolean {
  if (guide.declencheur === "manuel") return false
  if (contexte.public === null || contexte.public !== guide.public) return false
  if (!guide.route(contexte.pathname) || !routeAutoPermise(contexte.pathname)) return false
  if (contexte.onboardingOuvert || contexte.enExamen || contexte.dialogueOuvert) return false
  if (!situation.memoire.prefs.aidesAuto) return false
  if (estAJour(situation.memoire, guide.id, guide.version)) return false
  if (guide.condition && !guide.condition(contexte)) return false
  return etapesEffectives(guide, contexte.ciblePresente).length > 0
}

/**
 * Ce guide peut-il s'afficher de lui-même, maintenant ? Chaque règle ci-dessous est une
 * promesse faite à l'élève :
 *  - jamais deux aides automatiques à la fois, ni deux dans la même visite ;
 *  - jamais par-dessus un guide déjà ouvert, l'écran d'accueil du compte, une fenêtre, la
 *    salle d'examen, ni sur une page sans aide (quiz, paiement...) ;
 *  - jamais s'il a désactivé les aides automatiques, ou s'il a déjà vu cette version ;
 *  - une aide de fonctionnalité cède la place au tutoriel de bienvenue encore à faire,
 *    qui est le premier contact.
 */
export function peutDeclencherAuto(
  guide: DefinitionGuide,
  contexte: ContexteGuide,
  situation: SituationAuto,
): boolean {
  if (situation.guideOuvert || situation.autoDejaMontre) return false
  if (!peutSeMontrer(guide, contexte, situation)) return false
  if (guide.declencheur === "premiere-fonctionnalite") {
    const bienvenueEnAttente = GUIDES.some(
      (autre) => autre.declencheur === "premiere-visite" && peutSeMontrer(autre, contexte, situation),
    )
    if (bienvenueEnAttente) return false
  }
  return true
}

/** Le premier guide de type « parcours » qui peut se lancer seul, s'il y en a un. */
export function guideAutomatique(contexte: ContexteGuide, situation: SituationAuto): DefinitionGuide | null {
  return (
    GUIDES.find(
      (guide) => guide.type === "parcours" && guide.declencheur === "premiere-visite"
        && peutDeclencherAuto(guide, contexte, situation),
    ) ?? null
  )
}
