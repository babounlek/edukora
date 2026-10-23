import { useEffect, useState } from "react"

/**
 * Les éléments qu'un guide met en évidence sont repérés par `data-guide="nom"` - un
 * attribut posé exprès dans la page, jamais une classe CSS (qui est décorative et change
 * au gré des retouches de style).
 */

const ATTRIBUT_ACTIF = "data-guide-actif"

function selecteur(nom: string): string {
  // Les noms sont écrits dans contenu.ts, jamais saisis : on échappe quand même les
  // guillemets pour qu'un nom étrange ne casse pas le sélecteur.
  return `[data-guide="${nom.replace(/"/g, '\\"')}"]`
}

/**
 * Un élément est « à l'écran » s'il n'est caché par aucun de ses ancêtres (attribut `hidden`,
 * `display: none`, `visibility: hidden`). `aria-hidden` n'entre PAS en compte : Radix le pose
 * sur toute la page pendant qu'un panneau modal est ouvert (le centre d'aide, par exemple), et
 * un guide relancé depuis ce panneau y verrait, à tort, toutes ses cibles disparues.
 */
function estVisible(element: Element): boolean {
  for (let courant: Element | null = element; courant; courant = courant.parentElement) {
    if (courant instanceof HTMLElement && courant.hidden) return false
    const style = getComputedStyle(courant)
    if (style.display === "none" || style.visibility === "hidden") return false
  }
  return true
}

export function trouverCible(nom: string): HTMLElement | null {
  for (const element of document.querySelectorAll<HTMLElement>(selecteur(nom))) {
    if (estVisible(element)) return element
  }
  return null
}

export function ciblePresente(nom: string): boolean {
  return trouverCible(nom) !== null
}

/** Une fenêtre modale (code PIN, menu, centre d'aide...) est-elle ouverte en ce moment ? */
export function dialogueOuvert(): boolean {
  return document.querySelector('[role="dialog"][data-state="open"], [role="alertdialog"]') !== null
}

/**
 * Met une cible en évidence (contour, voir index.css) et l'amène à l'écran. Retourne la
 * fonction qui retire la mise en évidence - à appeler au changement d'étape et à la
 * fermeture. Le défilement est instantané si l'élève préfère les animations réduites.
 */
export function mettreEnEvidence(nom: string | undefined): () => void {
  if (!nom) return () => {}
  const element = trouverCible(nom)
  if (!element) return () => {}
  element.setAttribute(ATTRIBUT_ACTIF, "true")
  const reduit = typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches
  element.scrollIntoView({ block: "center", behavior: reduit ? "auto" : "smooth" })
  return () => element.removeAttribute(ATTRIBUT_ACTIF)
}

/**
 * Un compteur qui change quand la page change (éléments ajoutés ou retirés). Sert à
 * réévaluer « ma cible est-elle arrivée ? » après le chargement d'une page. N'observe que
 * tant que `actif` est vrai : sur le reste du site, aucun observateur ne tourne.
 */
export function useChangementsDePage(actif: boolean): number {
  const [version, setVersion] = useState(0)
  useEffect(() => {
    if (!actif || typeof MutationObserver === "undefined") return
    let planifie = 0
    const observateur = new MutationObserver(() => {
      if (planifie) return
      planifie = requestAnimationFrame(() => {
        planifie = 0
        setVersion((v) => v + 1)
      })
    })
    observateur.observe(document.body, { childList: true, subtree: true })
    return () => {
      observateur.disconnect()
      if (planifie) cancelAnimationFrame(planifie)
    }
  }, [actif])
  return version
}
