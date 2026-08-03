import { Link } from "react-router-dom"
import { Mail, MessageCircle } from "lucide-react"
import { SITE_DOMAIN, SITE_NAME } from "@/lib/site"
import { useCountry } from "@/context/CountryContext"
import { catalogueHomePath, coursListPath } from "@/lib/countryPath"

const CONTACT_EMAIL = `contact@${SITE_DOMAIN}`

export function Footer() {
  const year = new Date().getFullYear()
  const { country } = useCountry()

  return (
    <footer className="mt-auto border-t border-border/80 bg-background">
      <div className="mx-auto flex max-w-5xl flex-col gap-8 px-4 py-10 sm:flex-row sm:items-start sm:justify-between sm:px-6">
        <div>
          <Link to={catalogueHomePath(country)} className="flex items-baseline gap-2">
            <span className="font-display text-lg font-semibold tracking-tight text-primary">
              {SITE_NAME}
            </span>
            <span className="font-display text-xs italic text-muted-foreground">
              réussis ton examen
            </span>
          </Link>
          <p className="mt-2 max-w-xs text-sm text-muted-foreground">
            Cours, corrigés d'annales et quiz pour le BEPC, le Probatoire et le BAC.
          </p>
        </div>

        <nav className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-muted-foreground">
          <Link to={catalogueHomePath(country)} className="transition-colors hover:text-foreground">Épreuves</Link>
          <Link to={coursListPath(country)} className="transition-colors hover:text-foreground">Cours</Link>
          <Link to="/tarifs" className="transition-colors hover:text-foreground">Tarifs</Link>
          <Link to="/compte" className="transition-colors hover:text-foreground">Mon compte</Link>
        </nav>

        <div className="flex flex-col gap-2 text-sm text-muted-foreground">
          <span className="font-medium text-foreground">Contact</span>
          <a
            href={`mailto:${CONTACT_EMAIL}`}
            className="flex items-center gap-1.5 transition-colors hover:text-foreground"
          >
            <Mail className="size-3.5 shrink-0" />
            {CONTACT_EMAIL}
          </a>
          <a
            href="https://wa.me/237670401393"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 transition-colors hover:text-foreground"
          >
            <MessageCircle className="size-3.5 shrink-0" />
            +237 670 40 13 93
          </a>
        </div>
      </div>

      <div className="border-t border-border/80">
        <div className="mx-auto flex max-w-5xl flex-col gap-2 px-4 py-4 text-xs text-muted-foreground sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <span>© {year} {SITE_NAME}. Tous droits réservés.</span>
          <nav className="flex flex-wrap gap-x-4 gap-y-1">
            <Link to="/cgu" className="transition-colors hover:text-foreground">CGU</Link>
            <Link to="/confidentialite" className="transition-colors hover:text-foreground">Confidentialité</Link>
          </nav>
        </div>
      </div>
    </footer>
  )
}
