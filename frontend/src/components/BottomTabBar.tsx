import { Link, useLocation } from "react-router-dom"
import { BookOpen, CalendarCheck, TrendingUp } from "lucide-react"

import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { catalogueHomePath, epreuvesListPath, themesFrequentsPath, coursListPath } from "@/lib/countryPath"
import { cn } from "@/lib/utils"

/**
 * Les trois entrées de l'élève, en bas de l'écran, atteignables au pouce.
 *
 * C'est le bénéfice le plus concret du passage de cinq entrées à trois, et il n'était
 * pas possible avant : sur un téléphone d'entrée de gamme, la navigation vivait
 * derrière un bouton hamburger (voir Header), c'est-à-dire qu'elle n'existait pas.
 * Trois entrées, c'est exactement ce qui tient dans une barre permanente.
 *
 * Réservée à l'élève qui suit un plan - un visiteur anonyme garde la barre du haut et
 * son hamburger : il n'a que trois liens lui aussi, mais il est là pour lire une page,
 * pas pour revenir tous les jours. Le hamburger reste dans tous les cas pour les
 * réglages secondaires (pays, thème, compte).
 */
export function BottomTabBar() {
  const { isAuthenticated, user } = useAuth()
  const { country } = useCountry()
  const { pathname } = useLocation()

  if (!isAuthenticated || !user?.cursus_prepare) return null

  const accueil = catalogueHomePath(country)
  const estAccueil = pathname === accueil || pathname === `${accueil}/`
  const estReviser =
    pathname.startsWith(epreuvesListPath(country)) ||
    pathname.startsWith(coursListPath(country)) ||
    pathname.startsWith(themesFrequentsPath(country)) ||
    pathname.startsWith("/epreuves") ||
    pathname.startsWith("/cours")

  const onglets = [
    { to: accueil, label: "Aujourd'hui", icon: CalendarCheck, actif: estAccueil },
    { to: epreuvesListPath(country), label: "Réviser", icon: BookOpen, actif: estReviser },
    { to: "/parcours", label: "Ma progression", icon: TrendingUp, actif: pathname.startsWith("/parcours") },
  ]

  return (
    <nav
      aria-label="Navigation principale"
      // `pb-[env(safe-area-inset-bottom)]` : sur un téléphone à barre gestuelle, la
      // dernière rangée de pixels n'est pas cliquable - sans cette marge, le libellé
      // est lisible mais la cible ne réagit pas, ce qui se lit comme un bug.
      className="fixed inset-x-0 bottom-0 z-40 border-t border-border bg-background/95 pb-[env(safe-area-inset-bottom)] backdrop-blur-sm lg:hidden"
    >
      <div className="flex items-stretch">
        {onglets.map((onglet) => (
          <Link
            key={onglet.to}
            to={onglet.to}
            aria-current={onglet.actif ? "page" : undefined}
            className={cn(
              "flex flex-1 flex-col items-center gap-0.5 px-2 py-2 text-[11px] font-medium transition-colors",
              onglet.actif ? "text-primary" : "text-muted-foreground hover:text-foreground",
            )}
          >
            <onglet.icon className="size-5 shrink-0" />
            {onglet.label}
          </Link>
        ))}
      </div>
    </nav>
  )
}
