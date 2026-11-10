import { useEffect, useSyncExternalStore } from "react"

/**
 * La langue du TEXTE de la page affichée, quand c'est un contenu (cours, épreuve, article d'aide) : « fr » pour
 * un contenu qui n'existe qu'en français (BEPC, Probatoire, BAC), « en » pour celui qui a une version
 * anglaise (le GCE, un article d'aide traduit). Sans elle, BalisesDeRoute ne sait pas si `/en/cm/past-papers/x`
 * est une vraie page anglaise ou du français habillé d'une interface anglaise.
 *
 * Pourquoi c'est utile aux moteurs de recherche : un contenu français sous `/en/...` serait une copie quasi
 * identique de la page française. Il déclare donc pour canonical la page française et n'annonce aucun hreflang
 * (voir BalisesDeRoute) - le sitemap fait déjà ce choix, et la page prérendue pour les robots aussi (voir
 * backend/catalog/prerendu.py).
 *
 * Un petit magasin partagé plutôt qu'un contexte : la page qui connaît la langue (celle qui charge le contenu) et
 * le composant qui pose les balises (BalisesDeRoute, en dehors des routes) n'ont aucun parent commun utile.
 */
export type LangueContenu = "fr" | "en"

let courante: LangueContenu | null = null
const ecouteurs = new Set<() => void>()

function emettre() {
  ecouteurs.forEach((f) => f())
}

function abonner(f: () => void) {
  ecouteurs.add(f)
  return () => {
    ecouteurs.delete(f)
  }
}

/** À appeler par la page de contenu, avec la langue de ce contenu dès qu'elle est connue (`undefined` avant). */
export function useDeclarerLangueContenu(langue: LangueContenu | null | undefined) {
  useEffect(() => {
    if (!langue) return
    courante = langue
    emettre()
    // Ne retire que sa propre déclaration : jamais celle de la page suivante, déjà posée.
    return () => {
      if (courante === langue) {
        courante = null
        emettre()
      }
    }
  }, [langue])
}

/** La langue déclarée par la page affichée, ou null (accueil, listes, pages sans contenu propre). */
export function useLangueContenu(): LangueContenu | null {
  return useSyncExternalStore(
    abonner,
    () => courante,
    () => null,
  )
}
