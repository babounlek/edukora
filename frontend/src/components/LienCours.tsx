import { ArrowRight } from "lucide-react"
import { Link } from "react-router-dom"

import { useTitreCours } from "@/lib/coursTitres"

interface LienCoursProps {
  slug: string
  to: string
  /** Libellé générique (« Voir le cours complet »), gardé tant que le titre n'est pas connu. */
  label: string
  className: string
  /** Dans une liste déjà introduite (« Cours liés à cet exercice ») : le titre remplace le libellé. */
  titreSeul?: boolean
}

/**
 * Bouton vers un cours, nommé par le TITRE du cours. Le marqueur `[COURS_LINK:slug]` du corrigé ne porte que le
 * slug : sans titre, deux liens côte à côte s'appelaient tous « Voir le cours complet ». Le titre arrive
 * après le rendu (une requête groupée pour toute la page, voir lib/coursTitres) ; en attendant, ou s'il est
 * introuvable, le libellé générique reste.
 */
export function LienCours({ slug, to, label, className, titreSeul }: LienCoursProps) {
  const titre = useTitreCours(slug)
  return (
    // `flex-wrap` et libellé insécable : dans un encadré étroit (mobile), le long titre du cours écrasait
    // « Voir le cours complet » sur trois lignes ; le titre passe maintenant sous le libellé s'il manque de place.
    <Link to={to} className={`${className} flex-wrap`} aria-label={titre ? `${label} : ${titre}` : undefined}>
      {titre && titreSeul ? titre : <span className="whitespace-nowrap">{label}</span>}
      {titre && !titreSeul && <span className="font-normal text-muted-foreground">· {titre}</span>}
      <ArrowRight className="size-3.5 shrink-0" />
    </Link>
  )
}
