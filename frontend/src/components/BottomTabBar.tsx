import { useEffect, useRef } from "react"
import { Link, useLocation } from "react-router-dom"
import { BookOpen, CalendarCheck, NotebookPen, TrendingUp } from "lucide-react"

import { CompteAReboursBadge } from "@/components/CompteAReboursBadge"
import { useNotesDues } from "@/components/RangeeNotes"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { catalogueHomePath, epreuvesListPath, recherchePath, themesFrequentsPath, coursListPath } from "@/lib/countryPath"
import { cn } from "@/lib/utils"
import { useI18n } from "@/lib/i18n"

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
  const { t } = useI18n()
  const barRef = useRef<HTMLElement>(null)
  const visible = isAuthenticated && Boolean(user?.cursus_prepare)
  // Le point sur « Mes notes » : des notes sont à réviser aujourd'hui.
  const notesDues = useNotesDues(visible)?.total ?? 0

  // Publie la hauteur réelle de la barre (comptage à rebours compris, qui varie) dans
  // --bottom-tab-bar : une barre d'action fixée en bas d'une page (voir
  // EpreuveInediteDetailPage) se pose ainsi AU-DESSUS, sans en deviner la hauteur.
  useEffect(() => {
    const barre = barRef.current
    if (!visible || !barre || typeof ResizeObserver === "undefined") return
    const racine = document.documentElement
    const publier = () => racine.style.setProperty("--bottom-tab-bar", `${barre.offsetHeight}px`)
    publier()
    const observateur = new ResizeObserver(publier)
    observateur.observe(barre)
    return () => {
      observateur.disconnect()
      racine.style.removeProperty("--bottom-tab-bar")
    }
  }, [visible])

  if (!visible) return null

  const accueil = catalogueHomePath(country)
  const estAccueil = pathname === accueil || pathname === `${accueil}/`
  const estReviser =
    pathname.startsWith(epreuvesListPath(country)) ||
    pathname.startsWith(coursListPath(country)) ||
    pathname.startsWith(themesFrequentsPath(country)) ||
    pathname.startsWith(recherchePath(country)) ||
    pathname.startsWith("/epreuves") ||
    pathname.startsWith("/cours") ||
    pathname.startsWith("/fiches-edukora") ||
    pathname.startsWith("/examens-blancs") ||
    pathname.startsWith("/quiz")

  const onglets = [
    { to: accueil, label: t("nav.aujourdhui"), icon: CalendarCheck, actif: estAccueil },
    { to: epreuvesListPath(country), label: t("nav.reviser"), icon: BookOpen, actif: estReviser },
    { to: "/parcours", label: t("nav.progression"), icon: TrendingUp, actif: pathname.startsWith("/parcours") },
    { to: "/carnet", label: t("cpt.carnet"), icon: NotebookPen, actif: pathname.startsWith("/carnet"), pastille: notesDues > 0 },
  ]

  return (
    <nav
      ref={barRef}
      aria-label={t("nav.principale")}
      // `pb-[env(safe-area-inset-bottom)]` : sur un téléphone à barre gestuelle, la
      // dernière rangée de pixels n'est pas cliquable - sans cette marge, le libellé
      // est lisible mais la cible ne réagit pas, ce qui se lit comme un bug.
      className="fixed inset-x-0 bottom-0 z-40 border-t border-border bg-background/95 pb-[env(safe-area-inset-bottom)] backdrop-blur-sm lg:hidden"
    >
      {/* Sur mobile, le décompte n'existait que derrière le hamburger : autant dire
          qu'il n'existait pas. Ici il reste sous le pouce sur chaque écran, en gris
          comme partout ailleurs. Silencieusement absent sans date d'examen connue. Absent
          aussi sur « Aujourd'hui » : la bande du coach y dit déjà le même repère, en grand
          (voir TeteAccueil), et la pilule en double prenait de la hauteur à la barre. */}
      <div className="flex justify-center pt-1.5 empty:hidden">
        {/* Pas sur l'accueil (la bande y est déjà), ni pendant un quiz : la pastille se posait sur les réponses C et D (test élève Gogo). */}
        {!estAccueil && !pathname.startsWith("/quiz/") && <CompteAReboursBadge variant="pilule" className="whitespace-nowrap" />}
      </div>
      <div className="flex items-stretch">
        {onglets.map((onglet) => (
          <Link
            key={onglet.to}
            to={onglet.to}
            aria-current={onglet.actif ? "page" : undefined}
            className={cn(
              "flex flex-1 flex-col items-center gap-0.5 px-2 py-2 text-xs font-medium transition-colors",
              onglet.actif ? "text-primary" : "text-muted-foreground hover:text-foreground",
            )}
          >
            <span className="relative">
              <onglet.icon className="size-5 shrink-0" />
              {"pastille" in onglet && onglet.pastille && (
                <span className="absolute -right-1 -top-0.5 size-2 rounded-full bg-gold ring-2 ring-background" aria-hidden="true" />
              )}
            </span>
            {onglet.label}
          </Link>
        ))}
      </div>
    </nav>
  )
}
