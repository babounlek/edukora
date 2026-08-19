import type { ReactNode } from "react"
import { Link } from "react-router-dom"
import { ArrowRight } from "lucide-react"

type CalloutVariant = "piege" | "conseil" | "rappel"

interface CalloutProps {
  variant: CalloutVariant
  children?: ReactNode
  coursHrefs?: string[]
}

const STYLES: Record<CalloutVariant, { icon: string; title: string; className: string }> = {
  piege: { icon: "⚠️", title: "Piège à éviter", className: "border-warning bg-warning/10" },
  conseil: { icon: "💡", title: "Conseil", className: "border-primary bg-accent" },
  rappel: { icon: "📖", title: "Rappel de méthode", className: "border-info bg-info/10" },
}

/**
 * Encadré distinct pour les blocs "Piège à éviter" / "Conseil" / "Rappel de méthode"
 * produits par correction-experte.
 *
 * Le `not-prose` est posé sur l'habillage (titre, liens vers le cours), jamais sur le
 * conteneur : sur le conteneur, il désactivait la typographie pour tout le sous-arbre
 * - contenu compris, et sans qu'un `prose` imbriqué puisse la réactiver (voir
 * l'explication détaillée dans CoursRegleBox) - donc un rappel de méthode à plusieurs
 * paragraphes les affichait collés, listes sans puces ni retrait. Ces deux `not-prose`
 * d'habillage, eux, sont nécessaires et mesurés : sous un article `prose`, le titre
 * héritait sinon d'un `margin-top` de 1,25em (le `mb-1` ne l'emporte que sur le bas) et
 * les liens d'un `text-decoration: underline` permanent, là où le style voulu est
 * `hover:underline`.
 */
export function Callout({ variant, children, coursHrefs }: CalloutProps) {
  const { icon, title, className } = STYLES[variant]

  return (
    <div className={`my-4 rounded-lg border-l-4 px-4 py-3 text-sm leading-relaxed text-foreground ${className}`}>
      <p className="not-prose mb-1 flex items-center gap-1.5 font-semibold">
        <span aria-hidden="true">{icon}</span>
        {title}
      </p>
      {/* prose-sm pour rester à la taille du `text-sm` du conteneur, et surtout aucun
          `prose-p:my-*` : un tel override écraserait les règles `> :first-child` /
          `> :last-child` du plugin et rajouterait de la marge au padding du callout. Sans
          lui, le cas de très loin le plus courant - le corps d'un seul paragraphe, cf.
          extractCallouts dans lib/markdown - calcule `0px / 0px`, soit exactement le rendu
          d'avant : seuls les callouts réellement multi-blocs (listes comprises) changent. */}
      <div className="prose prose-sm prose-neutral max-w-none dark:prose-invert">{children}</div>
      {coursHrefs && coursHrefs.length > 0 && (
        <div className="not-prose mt-2 flex flex-col items-start gap-1">
          {coursHrefs.map((href) => (
            <Link key={href} to={href} className="flex items-center gap-1 font-medium text-primary hover:underline">
              Voir le cours complet
              <ArrowRight className="size-3.5" />
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
