import { useState } from "react"
import { Link, useLocation, useNavigate } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { Globe, Menu, Search, UserCircle } from "lucide-react"

import { listEpreuves } from "@/api/endpoints"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { ThemeToggle } from "@/components/ThemeToggle"
import { cn } from "@/lib/utils"
import { SITE_NAME } from "@/lib/site"
import { catalogueHomePath, coursListPath, epreuvesListPath } from "@/lib/countryPath"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Sheet, SheetContent, SheetDescription, SheetTitle, SheetTrigger } from "@/components/ui/sheet"

/**
 * `onNavigate` : appelé après un changement de pays, pour que l'exemplaire rendu
 * dans le menu mobile referme ce menu au lieu de laisser le visiteur devant un
 * panneau ouvert sur une page qui a déjà changé.
 * `dansLeMenu` : rendu à l'intérieur du menu mobile plutôt que dans la barre. La
 * contrainte de largeur y disparaît, le nom complet du pays est donc toujours
 * affiché - c'est dans la barre, et elle seule, qu'il faut se rabattre sur le code.
 */
function CountrySwitcher({ onNavigate, dansLeMenu = false }: { onNavigate?: () => void; dansLeMenu?: boolean }) {
  const { country, countries, setCountry } = useCountry()
  const navigate = useNavigate()

  // Un Country peut exister en base avant que du contenu réel n'y soit ingéré (voir
  // CountrySerializer.has_lessons côté backend) - ne proposer à la navigation que les
  // pays où il y a effectivement quelque chose à lire, pour ne jamais faire atterrir
  // un visiteur sur un catalogue vide.
  const browsableCountries = countries.filter((c) => c.has_lessons)

  function handleChange(code: string) {
    setCountry(code)
    navigate(catalogueHomePath(code))
    onNavigate?.()
  }

  if (browsableCountries.length === 0) {
    return (
      <span className="flex items-center gap-1 px-2 text-xs font-medium text-muted-foreground">
        <Globe className="size-3.5" />
        {country.toUpperCase()}
      </span>
    )
  }

  const currentLabel = browsableCountries.find((c) => c.code.toLowerCase() === country)?.label

  return (
    <Select value={country} onValueChange={handleChange}>
      <SelectTrigger
        aria-label="Changer de pays"
        className={cn(
          "shrink-0 gap-1",
          dansLeMenu
            ? "h-10 flex-1 px-3 text-sm"
            : "h-9 w-[72px] px-2 text-xs sm:w-auto sm:max-w-[150px] sm:text-sm",
        )}
      >
        <Globe className="size-3.5 shrink-0 text-muted-foreground" />
        {/* Enfant explicite (pas le comportement par défaut de SelectValue) : replié,
            le visiteur doit voir clairement sur quel pays il navigue - le nom complet
            partout où la place le permet, le code ("CM") seulement dans la barre sur
            petit écran. La liste ouverte, elle, garde toujours les noms complets. */}
        <SelectValue>
          {dansLeMenu ? (
            <span className="truncate">{currentLabel ?? country.toUpperCase()}</span>
          ) : (
            <>
              <span className="sm:hidden">{country.toUpperCase()}</span>
              <span className="hidden truncate sm:inline">{currentLabel ?? country.toUpperCase()}</span>
            </>
          )}
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        {browsableCountries.map((c) => (
          <SelectItem key={c.id} value={c.code.toLowerCase()}>
            {c.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}

export function Header() {
  const { isAuthenticated, isLoading: authLoading, user } = useAuth()
  const { country } = useCountry()
  const { pathname } = useLocation()
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  const isTarifsSection = pathname.startsWith("/tarifs")
  const isParcoursSection = !isTarifsSection && pathname.startsWith("/parcours")
  const isQuizSection = !isTarifsSection && pathname.startsWith("/quiz")
  const isCoursSection =
    !isTarifsSection && !isParcoursSection && (pathname === coursListPath(country) || pathname.startsWith("/cours"))
  const isEpreuvesSection =
    !isCoursSection &&
    !isTarifsSection &&
    !isParcoursSection &&
    (pathname === epreuvesListPath(country) || pathname.startsWith("/epreuves"))

  // Même clé de cache que CataloguePage ("epreuves-inedites-recente") : un visiteur
  // qui atterrit sur le catalogue puis navigue ailleurs ne repaie pas cette requête
  // dans la fenêtre de staleTime (60 s, voir main.tsx). Sert uniquement à savoir s'il
  // existe au moins une inédite pour ce pays - jamais le contenu de la réponse.
  const { data: inediteRecenteData } = useQuery({
    queryKey: ["epreuves-inedites-recente", country],
    queryFn: ({ signal }) => listEpreuves({ country, origine: "INEDITE", ordering: "recent" }, signal),
    enabled: Boolean(country),
  })
  const hasInedites = Boolean(inediteRecenteData && inediteRecenteData.count > 0)

  // Même triplet actif/libellé/lien que les boutons desktop juste en dessous - une
  // seule liste pour ne jamais les faire diverger (ex. un lien ajouté ici sans son
  // équivalent desktop, ou l'inverse). "Épreuves" couvre aussi les épreuves inédites
  // (mêmes filtres sur /epreuves, voir EpreuvesListPage.tsx) - pas d'entrée de nav
  // dédiée, juste le point or de `hasInedites` ci-dessous. Pointe vers /epreuves (le
  // moteur de recherche) et non plus vers l'accueil depuis la scission
  // accueil/catalogue - le logo, lui, reste le retour à l'accueil.
  const navLinks = [
    { to: epreuvesListPath(country), label: "Épreuves", active: isEpreuvesSection, badge: hasInedites },
    { to: coursListPath(country), label: "Cours", active: isCoursSection, badge: false },
    { to: "/parcours", label: "Parcours", active: isParcoursSection, badge: false },
    { to: "/quiz", label: "Quiz", active: isQuizSection, badge: false },
    { to: "/tarifs", label: "Tarifs", active: isTarifsSection, badge: false },
  ]

  return (
    <header className="sticky top-0 z-40 border-b border-border/80 bg-background/85 backdrop-blur-sm">
      <div className="h-[3px] w-full bg-gradient-to-r from-primary via-gold to-primary" />
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3.5 sm:px-6">
        <Link to={catalogueHomePath(country)} className="group flex items-baseline gap-2">
          <span className="font-display text-xl font-semibold tracking-tight text-primary">
            {SITE_NAME}
          </span>
          <span className="hidden whitespace-nowrap font-display text-xs italic text-muted-foreground sm:inline">
            réussis ton examen
          </span>
        </Link>
        <nav className="flex items-center gap-2">
          {/* Toujours visible (pas de hidden sm:), contrairement aux liens de nav
              desktop plus bas - ce bouton rend la recherche accessible depuis
              n'importe quelle page, y compris sur mobile où la place au clavier
              manque le plus. Pointe directement sur /epreuves (voir
              EpreuvesListPage.tsx), où le champ de recherche est en haut de page. */}
          <Button asChild variant="ghost" size="icon" aria-label="Rechercher une épreuve">
            <Link to={epreuvesListPath(country)}>
              <Search className="size-4.5" />
            </Link>
          </Button>
          <Sheet open={mobileNavOpen} onOpenChange={setMobileNavOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="lg:hidden" aria-label="Ouvrir le menu">
                <Menu className="size-5" />
              </Button>
            </SheetTrigger>
            <SheetContent>
              <SheetTitle>Menu</SheetTitle>
              <SheetDescription>Navigation principale d'{SITE_NAME}</SheetDescription>
              <nav className="mt-3 flex flex-col gap-1">
                {navLinks.map((link) => (
                  <Link
                    key={link.to}
                    to={link.to}
                    onClick={() => setMobileNavOpen(false)}
                    className={
                      link.active
                        ? "flex items-center gap-2 rounded-md bg-secondary px-3 py-2.5 text-base font-medium text-secondary-foreground"
                        : "flex items-center gap-2 rounded-md px-3 py-2.5 text-base font-medium text-foreground hover:bg-accent"
                    }
                  >
                    {link.label}
                    {/* Même point discret que la barre desktop (voir plus bas) - pas de
                        deuxième traitement visuel à maintenir en parallèle. */}
                    {link.badge && (
                      <span className="size-1.5 shrink-0 rounded-full bg-gold" aria-hidden="true" />
                    )}
                  </Link>
                ))}
              </nav>
              {/* Pays et thème, retirés de la barre sous `sm` faute de place (voir
                  le commentaire sur leur conteneur `hidden sm:flex`) - ils restent à
                  une tape d'ici, jamais supprimés du mobile. */}
              <div className="mt-4 flex items-center justify-between gap-3 border-t border-border pt-4 sm:hidden">
                <CountrySwitcher dansLeMenu onNavigate={() => setMobileNavOpen(false)} />
                <ThemeToggle />
              </div>
            </SheetContent>
          </Sheet>
          <span className="relative hidden lg:inline-flex">
            <Button asChild variant={isEpreuvesSection ? "secondary" : "ghost"} size="sm">
              <Link to={epreuvesListPath(country)}>
                Épreuves
                {hasInedites && <span className="sr-only"> - épreuves inédites disponibles</span>}
              </Link>
            </Button>
            {/* Pas de 6e lien pour signaler les inédites - la barre desktop est déjà
                pleine et le menu mobile perd tout à fait ce jeu de largeur (voir
                CountrySwitcher plus haut). Un point or discret sur "Épreuves" suffit :
                il ne consomme aucune largeur supplémentaire. */}
            {hasInedites && (
              <span className="pointer-events-none absolute -top-0.5 -right-0.5 flex size-2.5">
                <span className="absolute inline-flex size-full animate-ping rounded-full bg-gold opacity-75" />
                <span className="relative inline-flex size-2.5 rounded-full bg-gold ring-2 ring-background" />
              </span>
            )}
          </span>
          <Button asChild variant={isCoursSection ? "secondary" : "ghost"} size="sm" className="hidden lg:inline-flex">
            <Link to={coursListPath(country)}>Cours</Link>
          </Button>
          <Button asChild variant={isParcoursSection ? "secondary" : "ghost"} size="sm" className="hidden lg:inline-flex">
            <Link to="/parcours">Parcours</Link>
          </Button>
          <Button asChild variant={isQuizSection ? "secondary" : "ghost"} size="sm" className="hidden lg:inline-flex">
            <Link to="/quiz">Quiz</Link>
          </Button>
          <Button asChild variant={isTarifsSection ? "secondary" : "ghost"} size="sm" className="hidden lg:inline-flex">
            <Link to="/tarifs">Tarifs</Link>
          </Button>
          {/* Sous `sm`, ces deux contrôles secondaires descendent dans le menu (voir
              SheetContent plus haut) : à 375 px la barre réclamait ~419 px pour
              375 disponibles (logo + recherche + menu + pays + thème + connexion),
              et c'est le pays et le thème qu'on consulte le moins souvent. Le
              basculement est à `sm` et non à `lg` : entre les deux, les liens de nav
              desktop sont encore repliés dans le menu, la place ne manque pas. */}
          <div className="hidden items-center gap-2 sm:flex">
            <CountrySwitcher />
            <ThemeToggle />
          </div>
          {authLoading ? (
            // Le token d'accès ne survit jamais à un rechargement de page (voir
            // AuthContext) - une session valide se reconfirme silencieusement en
            // arrière-plan à chaque montage, ce qui prend un aller-retour réseau.
            // Sans ce repli neutre, un utilisateur connecté verrait le bouton
            // "Connexion" s'afficher brièvement à chaque F5, comme s'il avait été
            // déconnecté.
            <Skeleton className="h-8 w-20 rounded-md" />
          ) : isAuthenticated ? (
            <Button asChild variant="ghost" size="sm">
              <Link to="/compte" className="flex items-center gap-1.5">
                <UserCircle className="size-4 shrink-0" />
                {/* Tronqué sur petit écran : un nom complet un peu long (le champ est
                    libre) repoussait sinon la barre au-delà de la largeur de l'écran,
                    le même défaut que ci-dessus mais pour les visiteurs connectés. */}
                <span className="max-w-[7.5rem] truncate sm:max-w-none">
                  {user?.full_name || user?.pseudo || user?.phone_number}
                </span>
              </Link>
            </Button>
          ) : (
            <Button asChild size="sm">
              <Link to="/connexion">Connexion</Link>
            </Button>
          )}
        </nav>
      </div>
    </header>
  )
}
