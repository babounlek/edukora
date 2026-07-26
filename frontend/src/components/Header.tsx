import { Link, useLocation, useNavigate } from "react-router-dom"
import { Globe, UserCircle } from "lucide-react"

import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/ThemeToggle"
import { SITE_NAME } from "@/lib/site"
import { catalogueHomePath, coursListPath, replaceCountryInPath } from "@/lib/countryPath"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

function CountrySwitcher() {
  const { country, countries, setCountry } = useCountry()
  const { pathname } = useLocation()
  const navigate = useNavigate()

  function handleChange(code: string) {
    setCountry(code)
    const swapped = replaceCountryInPath(pathname, code)
    if (swapped !== pathname) navigate(swapped)
  }

  if (countries.length === 0) {
    return (
      <span className="flex items-center gap-1 px-2 text-xs font-medium text-muted-foreground">
        <Globe className="size-3.5" />
        {country.toUpperCase()}
      </span>
    )
  }

  const currentLabel = countries.find((c) => c.code.toLowerCase() === country)?.label

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
        {countries.map((c) => (
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

  const isTarifsSection = pathname.startsWith("/tarifs")
  const isQuizSection = !isTarifsSection && pathname.startsWith("/quiz")
  const isCoursSection = !isTarifsSection && !isQuizSection && (pathname === coursListPath(country) || pathname.startsWith("/cours"))
  const isLeconsSection =
    !isCoursSection &&
    !isTarifsSection &&
    !isQuizSection &&
    (pathname === catalogueHomePath(country) || pathname.startsWith("/lecons"))

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
          <Button asChild variant={isLeconsSection ? "secondary" : "ghost"} size="sm" className="hidden sm:inline-flex">
            <Link to={catalogueHomePath(country)}>Leçons</Link>
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
