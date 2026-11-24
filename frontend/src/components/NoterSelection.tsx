import { useEffect, useState, type RefObject } from "react"
import { NotebookPen } from "lucide-react"

import { AjouterNoteDialog } from "@/components/AjouterNoteDialog"
import { useAuth } from "@/context/AuthContext"
import { t, useI18n } from "@/lib/i18n"

const LONGUEUR_MIN = 4
const LONGUEUR_MAX = 600

/**
 * Le texte sélectionné, tel qu'on l'écrirait à la main : une formule KaTeX est rendue deux fois dans la page (en MathML pour
 * les lecteurs d'écran, puis en HTML) ; on la remplace par son écriture LaTeX d'origine entre « $ », sinon la citation
 * contiendrait la formule en double, lettre par lettre.
 */
export function texteDeLaSelection(plage: Range): string {
  const boite = document.createElement("div")
  boite.appendChild(plage.cloneContents())
  boite.querySelectorAll(".katex").forEach((k) => {
    const tex = k.querySelector('annotation[encoding="application/x-tex"]')?.textContent
    k.replaceWith(document.createTextNode(tex ? `$${tex}$` : ""))
  })
  return (boite.textContent ?? "").replace(/\s+/g, " ").trim()
}

/**
 * « Noter ça » : sélectionne un passage du cours ou du corrigé, un bouton apparaît sous la sélection, et le passage devient la
 * citation d'une note rangée dans la matière du document. C'est le geste le plus court pour prendre une note : sans lui, il
 * fallait descendre au pied de la section, retaper ce qu'on voulait garder.
 *
 * Le bouton se place SOUS la sélection : au-dessus, il tombait sous la barre d'actions native du téléphone. `onPointerDown`
 * empêche le navigateur de désélectionner avant le clic. Réservé aux comptes connectés (une note s'y enregistre).
 */
export function NoterSelection({
  cibleRef, subjectId,
}: { cibleRef: RefObject<HTMLElement | null>; subjectId?: number | null }) {
  useI18n()
  const { isAuthenticated } = useAuth()
  const [bouton, setBouton] = useState<{ x: number; y: number } | null>(null)
  const [citation, setCitation] = useState<string | null>(null)

  useEffect(() => {
    if (!isAuthenticated || !subjectId) return
    let minuteur = 0
    function lire() {
      const selection = window.getSelection()
      const zone = cibleRef.current
      if (!selection || selection.isCollapsed || selection.rangeCount === 0 || !zone) return setBouton(null)
      const plage = selection.getRangeAt(0)
      if (!zone.contains(plage.commonAncestorContainer)) return setBouton(null)
      const longueur = selection.toString().trim().length
      if (longueur < LONGUEUR_MIN || longueur > LONGUEUR_MAX) return setBouton(null)
      const rect = plage.getBoundingClientRect()
      // Centré sous la sélection, sans sortir de l'écran (le bouton fait environ 150 px de large).
      const x = Math.min(Math.max(rect.left + rect.width / 2, 90), window.innerWidth - 90)
      setBouton({ x, y: Math.min(rect.bottom + 10, window.innerHeight - 60) })
    }
    function planifier() {
      // La sélection bouge à chaque glissement du doigt : on attend qu'elle se stabilise avant d'afficher le bouton.
      window.clearTimeout(minuteur)
      minuteur = window.setTimeout(lire, 250)
    }
    document.addEventListener("selectionchange", planifier)
    return () => {
      document.removeEventListener("selectionchange", planifier)
      window.clearTimeout(minuteur)
    }
  }, [cibleRef, isAuthenticated, subjectId])

  function noter() {
    const selection = window.getSelection()
    if (selection && selection.rangeCount > 0) {
      const texte = texteDeLaSelection(selection.getRangeAt(0))
      if (texte) setCitation(texte)
    }
    setBouton(null)
  }

  if (!isAuthenticated || !subjectId) return null
  return (
    <>
      {bouton && citation === null && (
        <button
          type="button"
          style={{ left: bouton.x, top: bouton.y }}
          className="fixed z-50 flex -translate-x-1/2 items-center gap-1.5 rounded-full bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground shadow-lg print:hidden"
          onPointerDown={(e) => e.preventDefault()}
          onClick={noter}
        >
          <NotebookPen className="size-4" aria-hidden="true" />
          {t("ca.noter_ca")}
        </button>
      )}
      <AjouterNoteDialog
        open={citation !== null}
        onOpenChange={(ouvert) => !ouvert && setCitation(null)}
        subjectId={subjectId}
        citation={citation ?? undefined}
      />
    </>
  )
}
