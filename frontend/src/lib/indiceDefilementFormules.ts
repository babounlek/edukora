/**
 * Dit à chaque formule centrée (`.katex-display`) plus large que son bloc de quel côté il en reste à voir,
 * par l'attribut data-defile (« droite », « gauche », « les-deux », absent si elle tient) ; le CSS s'en sert
 * pour estomper ce bord (voir index.css). Sans cela, un tableau de variations de 565 px dans 270 px de large
 * n'avait aucune marque visible : sa dernière colonne (+∞) semblait simplement absente.
 *
 * Posé une fois pour toute l'application plutôt que dans chaque composant de rendu : le Markdown (quiz,
 * cours, corrigés) n'a pas d'élément englobant où accrocher un effet. Le marquage est regroupé sur une
 * image d'animation, et refait quand le DOM change, que la fenêtre change de taille ou que les polices
 * KaTeX finissent de charger (elles changent la largeur des formules).
 */
export function installerIndiceDefilementFormules(): () => void {
  if (typeof document === "undefined" || typeof window === "undefined") return () => {}

  let planifie = false

  const marquer = (el: HTMLElement) => {
    const reste = el.scrollWidth - el.clientWidth
    let etat = ""
    if (reste > 1) {
      if (el.scrollLeft <= 1) etat = "droite"
      else if (el.scrollLeft >= reste - 1) etat = "gauche"
      else etat = "les-deux"
    }
    if (etat) {
      if (el.dataset.defile !== etat) el.dataset.defile = etat
    } else if (el.dataset.defile !== undefined) {
      delete el.dataset.defile
    }
  }

  const toutMarquer = () => {
    planifie = false
    document.querySelectorAll<HTMLElement>(".katex-display").forEach(marquer)
  }

  const planifier = () => {
    if (planifie) return
    planifie = true
    window.requestAnimationFrame(toutMarquer)
  }

  // `scroll` ne remonte pas : on l'écoute en phase de capture, sur le document.
  const surDefilement = (evenement: Event) => {
    const cible = evenement.target
    if (cible instanceof HTMLElement && cible.classList.contains("katex-display")) marquer(cible)
  }

  document.addEventListener("scroll", surDefilement, true)
  window.addEventListener("resize", planifier)
  const observateur = typeof MutationObserver === "undefined" ? null : new MutationObserver(planifier)
  observateur?.observe(document.body, { childList: true, subtree: true })
  void document.fonts?.ready.then(planifier)
  planifier()

  return () => {
    document.removeEventListener("scroll", surDefilement, true)
    window.removeEventListener("resize", planifier)
    observateur?.disconnect()
  }
}
