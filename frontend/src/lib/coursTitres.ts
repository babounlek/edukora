import { useEffect, useState } from "react"

import { getCoursTitres } from "@/api/endpoints"

/**
 * Titre d'un cours à partir de son slug, pour nommer les boutons « Voir le cours complet ».
 *
 * Un marqueur `[COURS_LINK:<slug>]` du corrigé ne porte que le slug : deux liens côte à côte étaient
 * indiscernables. Chaque lien demande donc son titre ici ; les demandes faites dans la même fenêtre
 * (toute la page se rend d'un coup, souvent 20 liens) partent en UNE requête, et un titre connu n'est
 * jamais redemandé. Une réponse sans titre (cours inconnu ou non publié) ou un échec donne `null` : le
 * lien garde alors son libellé générique, rien ne casse.
 */
const FENETRE_MS = 30
const TAILLE_LOT = 50

const connus = new Map<string, Promise<string | null>>()
const enAttente = new Map<string, (titre: string | null) => void>()
let minuteur: ReturnType<typeof setTimeout> | null = null

async function vider() {
  minuteur = null
  const attentes = new Map(enAttente)
  enAttente.clear()
  const slugs = [...attentes.keys()]
  for (let i = 0; i < slugs.length; i += TAILLE_LOT) {
    const lot = slugs.slice(i, i + TAILLE_LOT)
    try {
      const titres = await getCoursTitres(lot)
      lot.forEach((slug) => attentes.get(slug)?.(titres[slug] ?? null))
    } catch {
      // Échec réseau : libellé générique pour l'instant, mais pas d'échec mémorisé - le slug sera redemandé.
      lot.forEach((slug) => {
        connus.delete(slug)
        attentes.get(slug)?.(null)
      })
    }
  }
}

export function titreDuCours(slug: string): Promise<string | null> {
  if (!slug) return Promise.resolve(null)
  const deja = connus.get(slug)
  if (deja) return deja
  const promesse = new Promise<string | null>((resolve) => {
    enAttente.set(slug, resolve)
  })
  connus.set(slug, promesse)
  if (minuteur === null) minuteur = setTimeout(() => void vider(), FENETRE_MS)
  return promesse
}

/** Remise à zéro du cache et de la file : pour les tests. */
export function reinitialiserTitresCours() {
  connus.clear()
  enAttente.clear()
  if (minuteur !== null) clearTimeout(minuteur)
  minuteur = null
}

/** Le titre du cours `slug` (null tant qu'il n'est pas connu, ou s'il n'existe pas). */
export function useTitreCours(slug: string): string | null {
  const [titre, setTitre] = useState<string | null>(null)
  useEffect(() => {
    let actif = true
    void titreDuCours(slug).then((t) => {
      if (actif) setTitre(t)
    })
    return () => {
      actif = false
    }
  }, [slug])
  return titre
}
