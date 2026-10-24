import type { CleI18n } from "@/lib/i18n"

/**
 * Un guide, tel que l'écrit lib/guides/contenu.ts : de la donnée, jamais de la logique.
 * Le tutoriel de bienvenue, les aides contextuelles et le centre d'aide lisent TOUS les
 * mêmes définitions - un texte n'existe qu'à un endroit.
 */

/**
 * - `parcours` : plusieurs étapes dans une carte flottante (le tutoriel de bienvenue) ;
 * - `aide` : une carte posée dans la page, à côté de ce qu'elle explique, rouvrable
 *   par un « ? » (une aide contextuelle).
 */
export type TypeGuide = "parcours" | "aide"

/**
 * Quand un guide peut se montrer TOUT SEUL. « manuel » : jamais seul, uniquement à la
 * demande de l'élève (bouton d'aide, centre d'aide).
 */
export type DeclencheurGuide = "premiere-visite" | "premiere-fonctionnalite" | "manuel"

/** Qui voit le guide : un élève connecté avec un examen déclaré, ou un visiteur. */
export type PublicGuide = "eleve" | "visiteur"

export interface ActionGuide {
  label: CleI18n
  /** Chemin interne (routeur), jamais une URL absolue. */
  to: string
}

export interface EtapeGuide {
  id: string
  titre: CleI18n
  texte: CleI18n
  /**
   * Valeur de l'attribut `data-guide` de l'élément mis en évidence. Jamais une classe
   * CSS : celles-ci sont décoratives et changent sans prévenir.
   */
  cible?: string
  /**
   * Cible absente ou masquée : `true` saute l'étape (elle parlerait de quelque chose
   * qui n'est pas à l'écran), `false` la montre sans mise en évidence.
   */
  cibleObligatoire?: boolean
  action?: ActionGuide
}

export interface DefinitionGuide {
  /** Stable pour toujours : c'est la clé de la mémoire de l'élève. */
  id: string
  /**
   * Version MAJEURE : l'augmenter repropose le guide à qui l'avait déjà vu. Une simple
   * correction de formulation ne l'augmente pas.
   */
  version: number
  type: TypeGuide
  titre: CleI18n
  description: CleI18n
  declencheur: DeclencheurGuide
  public: PublicGuide | "tous"
  /** Pages (chemins internes du routeur) où le guide a un sens. */
  route: (pathname: string) => boolean
  /**
   * Où le centre d'aide emmène l'élève pour relancer ce guide : "accueil" (l'accueil de son pays) ou un
   * chemin fixe. Absent : le guide est lié à une page qui dépend d'un contenu (un cours, un exercice) ;
   * le centre ne peut alors le relancer que depuis cette page, et le dit.
   */
  cheminRelance?: string
  /** Condition d'affichage automatique supplémentaire (en plus du public et de la route). */
  condition?: (contexte: ContexteGuide) => boolean
  etapes: EtapeGuide[]
}

/** Ce que le moteur sait de la situation au moment de décider d'afficher un guide. */
export interface ContexteGuide {
  pathname: string
  /** null tant qu'on ne sait pas encore qui regarde (session en cours de lecture). */
  public: PublicGuide | null
  /** L'écran de première visite (choix de l'examen) est ouvert : rien ne s'affiche par-dessus. */
  onboardingOuvert: boolean
  /** Salle d'examen : un chrono tourne. */
  enExamen: boolean
  /** Une fenêtre modale est déjà ouverte (saisie d'un code PIN, menu, paiement...). */
  dialogueOuvert: boolean
  /** La cible `data-guide` est-elle à l'écran ? */
  ciblePresente: (cible: string) => boolean
}

export type StatutGuide = "termine" | "ignore"

export interface MemoireGuide {
  version: number
  statut: StatutGuide
  /** Millisecondes depuis 1970, pour information ; aucune règle n'en dépend. */
  date: number
}

export interface DonneesGuides {
  /** Format du stockage : permet de migrer plus tard sans lire de travers. */
  v: 1
  guides: Record<string, MemoireGuide>
  prefs: { aidesAuto: boolean }
}
