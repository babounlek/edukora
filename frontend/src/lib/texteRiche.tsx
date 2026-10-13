import { Fragment, type ReactNode } from "react"

/**
 * Mini-balisage pour les textes traduits qui portent du gras ou un exposant : `**gras**`
 * et `^exposant^`. Évite de découper une phrase en trois clés autour d'un `<strong>` - la
 * traduction garde ainsi sa phrase entière, et l'ordre des mots reste libre d'une langue à l'autre.
 */
export function texteRiche(texte: string): ReactNode {
  return texte.split(/(\*\*[^*]+\*\*|\^[^^]+\^)/).map((morceau, i) => {
    if (morceau.startsWith("**")) return <strong key={i}>{morceau.slice(2, -2)}</strong>
    if (morceau.startsWith("^")) return <sup key={i}>{morceau.slice(1, -1)}</sup>
    return <Fragment key={i}>{morceau}</Fragment>
  })
}
