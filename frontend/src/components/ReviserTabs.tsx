import { Link, useLocation } from "react-router-dom"

import { useCountry } from "@/context/CountryContext"
import { coursListPath, epreuvesListPath, themesFrequentsPath } from "@/lib/countryPath"
import { cn } from "@/lib/utils"

/**
 * Les trois surfaces de la bibliothèque sous un seul chapeau : Épreuves, Cours,
 * Thèmes.
 *
 * Elles étaient trois entrées de menu séparées, c'est-à-dire trois portes d'entrée à
 * choisir AVANT de savoir ce qu'on cherche. Regroupées ici, l'unité de navigation
 * devient le sujet qu'on révise et non le type de document - et "Thèmes", jusqu'ici
 * absente du menu, remonte au même rang que les deux autres alors que c'est la plus
 * proche de la façon dont on révise réellement.
 *
 * Des LIENS vers les pages existantes, jamais un onglet qui les ré-embarque : chaque
 * page garde son URL, son référencement et son code. Seul le chemin pour y arriver
 * change.
 */
export function ReviserTabs() {
  const { country } = useCountry()
  const { pathname } = useLocation()

  const onglets = [
    { to: epreuvesListPath(country), label: "Épreuves", actif: pathname.startsWith(epreuvesListPath(country)) },
    { to: coursListPath(country), label: "Cours", actif: pathname.startsWith(coursListPath(country)) },
    { to: themesFrequentsPath(country), label: "Thèmes", actif: pathname.startsWith(themesFrequentsPath(country)) },
  ]

  // Sans conteneur ni marge propres : rendu comme premier enfant du conteneur que
  // chaque page a déjà (`mx-auto max-w-5xl px-4`), pour ne pas empiler deux fois la
  // même largeur et la même gouttière.
  return (
    <nav aria-label="Réviser" className="mb-6">
      <div className="flex gap-1 border-b border-border">
        {onglets.map((onglet) => (
          <Link
            key={onglet.to}
            to={onglet.to}
            aria-current={onglet.actif ? "page" : undefined}
            className={cn(
              "-mb-px border-b-2 px-3 py-2 text-sm font-medium transition-colors",
              onglet.actif
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:border-border hover:text-foreground",
            )}
          >
            {onglet.label}
          </Link>
        ))}
      </div>
    </nav>
  )
}
