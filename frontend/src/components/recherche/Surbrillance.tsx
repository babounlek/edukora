import { decouperSurbrillance } from "@/lib/recherche"

/** Texte dont les mots cherchés sont surlignés - sans tenir compte des accents ni de la casse, et
 * sans jamais injecter de HTML (le texte vient du catalogue : rendu en simples nœuds React). */
export function Surbrillance({ texte, jetons }: { texte: string; jetons: string[] }) {
  return (
    <>
      {decouperSurbrillance(texte, jetons).map((morceau, index) =>
        morceau.surligne ? (
          <mark key={index} className="rounded-sm bg-gold/30 px-0.5 font-medium text-inherit">
            {morceau.texte}
          </mark>
        ) : (
          <span key={index}>{morceau.texte}</span>
        ),
      )}
    </>
  )
}
