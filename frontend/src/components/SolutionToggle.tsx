import { createContext, useContext, useId, useState, type ReactNode } from "react"
import { Eye, EyeOff } from "lucide-react"

import { t, useI18n } from "@/lib/i18n"

/**
 * Vrai quand l'élève a DÉJÀ demandé la correction (quiz : « Voir la correction ») : un second bouton « Afficher la solution »
 * à l'intérieur de ce corrigé faisait demander deux fois la même chose (test élève Gogo). La solution est alors montrée
 * directement, sans bouton.
 */
export const SolutionsOuvertesContext = createContext(false)

interface SolutionToggleProps {
  children?: ReactNode
}

/**
 * Masque la solution d'un exercice d'auto-évaluation derrière un bouton, pour que
 * l'élève cherche avant de la voir.
 *
 * Pas de `not-prose` sur le conteneur : il désactivait la typographie pour tout le
 * sous-arbre, y compris le `prose` de la solution révélée, qu'un `prose` imbriqué ne
 * réactive jamais (voir l'explication détaillée dans CoursRegleBox) - la solution
 * s'affichait donc sans marges ni puces partout, aussi bien dans les "Exercices
 * d'application" d'un Cours que dans un corrigé d'épreuve. Rien à protéger côté
 * habillage : @tailwindcss/typography ne cible ni les `div`, ni les `button`, ni les
 * `svg` (mesuré), le bouton garde donc son style intact même sous un article `prose`.
 */
export function SolutionToggle({ children }: SolutionToggleProps) {
  useI18n()
  const [open, setOpen] = useState(false)
  const idContenu = useId()
  const ouvertesDOffice = useContext(SolutionsOuvertesContext)

  if (ouvertesDOffice) {
    return (
      <div className="prose prose-neutral my-4 max-w-none text-justify border-l-2 border-border pl-4 dark:prose-invert">
        {children}
      </div>
    )
  }

  return (
    <div className="my-4">
      {/* aria-expanded/aria-controls : sans eux, un lecteur d'écran ne sait pas que le bouton déplie
          un contenu. min-h-10 : cible tactile utilisable (le bouton faisait ≈ 32 px). */}
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        aria-expanded={open}
        aria-controls={idContenu}
        className="flex min-h-10 items-center gap-1.5 rounded-md border border-border px-3.5 py-2 text-sm font-medium text-primary transition-colors hover:bg-accent"
      >
        {open ? <EyeOff className="size-3.5" aria-hidden="true" /> : <Eye className="size-3.5" aria-hidden="true" />}
        {open ? t("co.masquer_solution") : t("co.voir_solution")}
      </button>
      {open && (
        <div id={idContenu} className="prose prose-neutral mt-3 max-w-none text-justify border-l-2 border-border pl-4 dark:prose-invert">
          {children}
        </div>
      )}
    </div>
  )
}
