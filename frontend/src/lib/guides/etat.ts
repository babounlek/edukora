import { useSyncExternalStore } from "react"

import {
  definirAidesAuto, lireDonnees, memoriser, reporterAnonymeSur, toutOublier,
} from "./store"
import type { DonneesGuides, StatutGuide } from "./types"
import { trouverGuide } from "./contenu"

/**
 * L'état partagé des guides : quel guide est ouvert, à quelle étape, si le centre d'aide
 * est ouvert, pour QUI on mémorise (l'identité), et si une aide automatique a déjà été
 * montrée depuis le chargement de la page.
 *
 * Un petit magasin externe (useSyncExternalStore, même mécanique que lib/modeExamen.ts et
 * lib/cursusPrepare.ts) plutôt qu'un Provider : le bouton « Aide » du Header, le tutoriel,
 * l'aide dans la séance et le centre d'aide sont montés à des endroits sans rapport de
 * parenté, et l'ajout d'un Provider aurait obligé à réindenter App.tsx.
 */

export interface GuideOuvert {
  id: string
  /** Position dans `definition.etapes` (pas dans la liste filtrée par les cibles absentes). */
  etape: number
  /** Demandé par l'élève (bouton, centre d'aide) : jamais fermé de force à un changement de page. */
  explicite: boolean
}

export interface EtatGuides {
  /**
   * Qui regarde : « anonyme » ou « {compte}:{profil} ». null tant que la session n'est pas lue -
   * rien ne se montre et rien ne s'enregistre avant, sous peine d'écrire sur la mauvaise personne.
   */
  identite: string | null
  ouvert: GuideOuvert | null
  centreOuvert: boolean
  onboardingOuvert: boolean
  /** Une aide automatique a été montrée depuis le chargement : plus aucune, même après navigation. */
  autoDejaMontre: boolean
  /** Change à chaque écriture en mémoire, pour que les composants relisent. */
  revision: number
}

const INITIAL: EtatGuides = {
  identite: null,
  ouvert: null,
  centreOuvert: false,
  onboardingOuvert: false,
  autoDejaMontre: false,
  revision: 0,
}

let etat: EtatGuides = INITIAL
const abonnes = new Set<() => void>()

function changer(partiel: Partial<EtatGuides>) {
  etat = { ...etat, ...partiel }
  abonnes.forEach((rappel) => rappel())
}

function abonner(rappel: () => void) {
  abonnes.add(rappel)
  return () => {
    abonnes.delete(rappel)
  }
}

export function lireEtat(): EtatGuides {
  return etat
}

export function useEtatGuides(): EtatGuides {
  return useSyncExternalStore(abonner, lireEtat, lireEtat)
}

/**
 * Qui regarde. Au premier compte connecté, ce que le visiteur anonyme avait déjà fermé est
 * reporté sur le compte (voir reporterAnonymeSur), pour qu'il ne revoie pas ce qu'il vient
 * de voir.
 */
export function definirIdentite(identite: string | null) {
  if (identite === etat.identite) return
  if (identite && identite !== "anonyme") reporterAnonymeSur(identite)
  // Un guide ouvert pour quelqu'un d'autre n'a plus de sens : changement de profil, déconnexion.
  changer({ identite, ouvert: null, revision: etat.revision + 1 })
}

export function signalerOnboarding(ouvert: boolean) {
  if (ouvert === etat.onboardingOuvert) return
  changer({ onboardingOuvert: ouvert })
}

/**
 * Ouvre un guide.
 *  - Demandé par l'élève (`explicite`) : toujours obéi, même si un autre guide est ouvert -
 *    il remplace celui qu'il a sous les yeux, puisque c'est lui qui vient de le demander.
 *  - Montré tout seul : jamais par-dessus un guide ouvert, et la visite n'en recevra plus
 *    d'autre (`autoDejaMontre`).
 */
export function ouvrirGuide(id: string, options: { explicite: boolean; etape?: number }) {
  if (!trouverGuide(id)) return
  if (!options.explicite && etat.ouvert) return
  changer({
    ouvert: { id, etape: options.etape ?? 0, explicite: options.explicite },
    autoDejaMontre: etat.autoDejaMontre || !options.explicite,
  })
}

export function allerALEtape(etape: number) {
  if (!etat.ouvert) return
  changer({ ouvert: { ...etat.ouvert, etape } })
}

/**
 * Ferme le guide ouvert. `statut` : « termine » (il est allé au bout ou a dit avoir compris),
 * « ignore » (il l'a écarté), ou aucun (fermeture sans conséquence, p. ex. un guide relancé
 * à la main pour le relire). Fermer n'est jamais un échec : « ignore » ne diffère de
 * « termine » que par ce que le centre d'aide en dit.
 */
export function fermerGuide(statut?: StatutGuide) {
  const ouvert = etat.ouvert
  if (!ouvert) return
  const guide = trouverGuide(ouvert.id)
  if (guide && statut && etat.identite) memoriser(etat.identite, guide.id, guide.version, statut)
  changer({ ouvert: null, revision: etat.revision + 1 })
}

export function ouvrirCentre() {
  changer({ centreOuvert: true })
}

export function fermerCentre() {
  changer({ centreOuvert: false })
}

/** Ce que l'élève actuel a déjà vu. Relu à chaque appel : peu coûteux, et toujours à jour. */
export function memoireActuelle(): DonneesGuides {
  return lireDonnees(etat.identite ?? "anonyme")
}

export function reglerAidesAuto(actif: boolean) {
  if (!etat.identite) return
  definirAidesAuto(etat.identite, actif)
  changer({ revision: etat.revision + 1 })
}

export function toutRevoir() {
  if (!etat.identite) return
  toutOublier(etat.identite)
  // Les aides automatiques peuvent se remontrer à la prochaine visite, pas dans celle-ci.
  changer({ revision: etat.revision + 1 })
}

/** Pour les tests : repart d'un état neuf. */
export function reinitialiserEtat() {
  etat = INITIAL
  abonnes.forEach((rappel) => rappel())
}

/** `useEtatGuides` + la mémoire de l'élève, relue quand elle change. */
export function useGuides() {
  const courant = useEtatGuides()
  return { ...courant, memoire: lireDonnees(courant.identite ?? "anonyme") }
}
