import { Link, useLocation } from "react-router-dom"
import { UserCircle } from "lucide-react"

import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/ThemeToggle"
import { SITE_NAME } from "@/lib/site"

export function Header() {
  const { isAuthenticated, user } = useAuth()
  const { pathname } = useLocation()
  const isCoursSection = pathname.startsWith("/cours")
  const isTarifsSection = pathname.startsWith("/tarifs")
  const isLeconsSection = !isCoursSection && !isTarifsSection && (pathname === "/" || pathname.startsWith("/lecons"))

  return (
    <header className="sticky top-0 z-40 border-b border-border/80 bg-background/85 backdrop-blur-sm">
      <div className="h-[3px] w-full bg-gradient-to-r from-primary via-gold to-primary" />
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3.5 sm:px-6">
        <Link to="/" className="group flex items-baseline gap-2">
          <span className="font-display text-xl font-semibold tracking-tight text-primary">
            {SITE_NAME}
          </span>
          <span className="hidden font-display text-xs italic text-muted-foreground sm:inline">
            réussis ton examen
          </span>
        </Link>
        <nav className="flex items-center gap-2">
          <Button asChild variant={isLeconsSection ? "secondary" : "ghost"} size="sm" className="hidden sm:inline-flex">
            <Link to="/">Leçons</Link>
          </Button>
          <Button asChild variant={isCoursSection ? "secondary" : "ghost"} size="sm" className="hidden sm:inline-flex">
            <Link to="/cours">Cours</Link>
          </Button>
          <Button asChild variant={isTarifsSection ? "secondary" : "ghost"} size="sm" className="hidden sm:inline-flex">
            <Link to="/tarifs">Tarifs</Link>
          </Button>
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
