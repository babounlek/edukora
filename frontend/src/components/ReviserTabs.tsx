import { Link, useLocation } from "react-router-dom"
import { Search } from "lucide-react"

import { useCountry } from "@/context/CountryContext"
import { coursListPath, epreuvesListPath, recherchePath, themesFrequentsPath } from "@/lib/countryPath"
import { ETAT_FOCUS_RECHERCHE } from "@/lib/recherche"
import { cn } from "@/lib/utils"

/**
 * Les surfaces de révision sous un seul chapeau : Épreuves, Cours, Thèmes, Quiz.
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
  const surLaRecherche = pathname.startsWith(recherchePath(country))

  const onglets = [
    { to: epreuvesListPath(country), label: "Épreuves", actif: pathname.startsWith(epreuvesListPath(country)) },
    { to: coursListPath(country), label: "Cours", actif: pathname.startsWith(coursListPath(country)) },
    { to: themesFrequentsPath(country), label: "Thèmes", actif: pathname.startsWith(themesFrequentsPath(country)) },
    { to: "/quiz", label: "Quiz", actif: pathname.startsWith("/quiz") },
  ]

  // Sans conteneur ni marge propres : rendu comme premier enfant du conteneur que
  // chaque page a déjà (`mx-auto max-w-5xl px-4`), pour ne pas empiler deux fois la
  // même largeur et la même gouttière.
  return (
    <nav aria-label="Réviser" className="mb-6">
      <div className="flex items-end justify-between gap-3 border-b border-border">
        <div className="flex gap-1">
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
        {/* La recherche de TOUT le site (thèmes, cours, épreuves, exercices, quiz), pas un cinquième type de
            contenu : un lien en forme de champ vers la page de recherche, champ prêt à écrire. Volontairement
            pas un vrai champ - les pages Épreuves et Cours ont déjà le leur, qui ne filtre que leur propre
            liste, et deux champs côte à côte se feraient concurrence. Sous `sm`, la loupe seule : quatre
            onglets tiennent à peine dans 375 px. Absent de la page de recherche elle-même, qui a son grand
            champ juste en dessous. */}
        {!surLaRecherche && (
          <Link
            to={recherchePath(country)}
            state={ETAT_FOCUS_RECHERCHE}
            aria-label="Rechercher sur tout le site"
            aria-keyshortcuts="/ Control+K Meta+K"
            className="mb-1 inline-flex h-8 shrink-0 items-center gap-2 rounded-md border border-border bg-background px-2.5 text-sm text-muted-foreground transition-colors hover:border-primary/50 hover:text-foreground sm:w-56 sm:justify-start"
          >
            <Search className="size-4 shrink-0" aria-hidden="true" />
            <span className="hidden sm:inline">Rechercher partout…</span>
            <kbd className="ml-auto hidden rounded border border-border px-1.5 text-[11px] leading-5 sm:inline" aria-hidden="true">/</kbd>
          </Link>
        )}
      </div>
    </nav>
  )
}
