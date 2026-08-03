import { useState } from "react"
import { Link, useLocation, useNavigate } from "react-router-dom"
import { Globe, Menu, UserCircle } from "lucide-react"

import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/ThemeToggle"
import { SITE_NAME } from "@/lib/site"
import { catalogueHomePath, coursListPath } from "@/lib/countryPath"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Sheet, SheetContent, SheetDescription, SheetTitle, SheetTrigger } from "@/components/ui/sheet"

function CountrySwitcher() {
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
      <SelectTrigger className="h-9 w-[72px] shrink-0 gap-1 px-2 text-xs sm:w-auto sm:max-w-[150px] sm:text-sm">
        <Globe className="size-3.5 shrink-0 text-muted-foreground" />
        {/* Enfant explicite (pas le comportement par défaut de SelectValue) : replié,
            le visiteur doit voir clairement sur quel pays il navigue - le nom complet
            sur desktop, le code ("CM") sur mobile faute de place. La liste ouverte,
            elle, garde toujours les noms complets. */}
        <SelectValue>
          <span className="sm:hidden">{country.toUpperCase()}</span>
          <span className="hidden truncate sm:inline">{currentLabel ?? country.toUpperCase()}</span>
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
  const { isAuthenticated, user } = useAuth()
  const { country } = useCountry()
  const { pathname } = useLocation()
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  const isTarifsSection = pathname.startsWith("/tarifs")
  const isQuizSection = !isTarifsSection && pathname.startsWith("/quiz")
  const isCoursSection = !isTarifsSection && !isQuizSection && (pathname === coursListPath(country) || pathname.startsWith("/cours"))
  const isEpreuvesSection =
    !isCoursSection &&
    !isTarifsSection &&
    !isQuizSection &&
    (pathname === catalogueHomePath(country) || pathname.startsWith("/epreuves"))

  // Même triplet actif/libellé/lien que les boutons desktop juste en dessous - une
  // seule liste pour ne jamais les faire diverger (ex. un lien ajouté ici sans son
  // équivalent desktop, ou l'inverse).
  const navLinks = [
    { to: catalogueHomePath(country), label: "Épreuves", active: isEpreuvesSection },
    { to: coursListPath(country), label: "Cours", active: isCoursSection },
    { to: "/quiz", label: "Quiz", active: isQuizSection },
    { to: "/tarifs", label: "Tarifs", active: isTarifsSection },
  ]

  return (
    <header className="sticky top-0 z-40 border-b border-border/80 bg-background/85 backdrop-blur-sm">
      <div className="h-[3px] w-full bg-gradient-to-r from-primary via-gold to-primary" />
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3.5 sm:px-6">
        <Link to={catalogueHomePath(country)} className="group flex items-baseline gap-2">
          <span className="font-display text-xl font-semibold tracking-tight text-primary">
            {SITE_NAME}
          </span>
          <span className="hidden font-display text-xs italic text-muted-foreground sm:inline">
            réussis ton examen
          </span>
        </Link>
        <nav className="flex items-center gap-2">
          <Sheet open={mobileNavOpen} onOpenChange={setMobileNavOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="sm:hidden" aria-label="Ouvrir le menu">
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
                        ? "rounded-md bg-secondary px-3 py-2.5 text-base font-medium text-secondary-foreground"
                        : "rounded-md px-3 py-2.5 text-base font-medium text-foreground hover:bg-accent"
                    }
                  >
                    {link.label}
                  </Link>
                ))}
              </nav>
            </SheetContent>
          </Sheet>
          <Button asChild variant={isEpreuvesSection ? "secondary" : "ghost"} size="sm" className="hidden sm:inline-flex">
            <Link to={catalogueHomePath(country)}>Épreuves</Link>
          </Button>
          <Button asChild variant={isCoursSection ? "secondary" : "ghost"} size="sm" className="hidden sm:inline-flex">
            <Link to={coursListPath(country)}>Cours</Link>
          </Button>
          <Button asChild variant={isQuizSection ? "secondary" : "ghost"} size="sm" className="hidden sm:inline-flex">
            <Link to="/quiz">Quiz</Link>
          </Button>
          <Button asChild variant={isTarifsSection ? "secondary" : "ghost"} size="sm" className="hidden sm:inline-flex">
            <Link to="/tarifs">Tarifs</Link>
          </Button>
          <CountrySwitcher />
          <ThemeToggle />
          {isAuthenticated ? (
            <Button asChild variant="ghost" size="sm">
              <Link to="/compte" className="flex items-center gap-1.5">
                <UserCircle className="size-4" />
                {user?.full_name || user?.phone_number}
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
