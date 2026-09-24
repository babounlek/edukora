import { Link } from "react-router-dom"
import { Mail, MessageCircle, ShieldCheck } from "lucide-react"

import { SITE_DOMAIN, SITE_NAME } from "@/lib/site"
import { useCountry } from "@/context/CountryContext"
import { catalogueHomePath, coursListPath, epreuvesListPath } from "@/lib/countryPath"

const CONTACT_EMAIL = `contact@${SITE_DOMAIN}`
const CONTACT_WHATSAPP = "+237 670 40 13 93"

export function Footer() {
  const year = new Date().getFullYear()
  const { country } = useCountry()

  const platformLinks = [
    { to: epreuvesListPath(country), label: "Épreuves" },
    { to: coursListPath(country), label: "Cours" },
    { to: "/parcours", label: "Parcours" },
    { to: "/quiz", label: "Quiz" },
    { to: "/tarifs", label: "Tarifs" },
  ]

  const accountLinks = [
    { to: "/compte", label: "Mon compte" },
    { to: "/mes-paiements", label: "Mes paiements" },
  ]

  const legalLinks = [
    { to: "/a-propos", label: "À propos" },
    { to: "/cgu", label: "Conditions d'utilisation" },
    { to: "/confidentialite", label: "Confidentialité" },
  ]

  return (
    <footer className="mt-auto border-t border-border/80 bg-secondary/30">
      <div className="h-px w-full bg-gradient-to-r from-primary/0 via-gold/70 to-primary/0" />

      <div className="mx-auto grid max-w-5xl gap-10 px-4 py-14 sm:px-6 lg:grid-cols-[1.3fr_1fr_1fr_1fr] lg:gap-6">
        <div className="max-w-xs">
          <Link to={catalogueHomePath(country)} className="flex items-baseline gap-2">
            <span className="font-display text-xl font-semibold tracking-tight text-primary">
              {SITE_NAME}
            </span>
            <span className="font-display text-xs italic text-muted-foreground">
              réussis ton examen
            </span>
          </Link>
          <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
            Chaque jour, on te dit quoi réviser pour le BEPC, le Probatoire ou le BAC : les
            thèmes qui tombent vraiment, et on retient ce que tu rates.
          </p>

          <div className="mt-6 flex flex-col gap-3">
            <a
              href={`mailto:${CONTACT_EMAIL}`}
              className="group flex items-center gap-3 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-background text-primary ring-1 ring-border transition-colors group-hover:ring-primary/50">
                <Mail className="size-3.5" />
              </span>
              {CONTACT_EMAIL}
            </a>
            <a
              href="https://wa.me/237670401393"
              target="_blank"
              rel="noopener noreferrer"
              className="group flex items-center gap-3 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-background text-primary ring-1 ring-border transition-colors group-hover:ring-primary/50">
                <MessageCircle className="size-3.5" />
              </span>
              {CONTACT_WHATSAPP}
            </a>
          </div>
        </div>

        <nav className="flex flex-col gap-2.5">
          <span className="text-xs font-semibold uppercase tracking-wider text-foreground/70">
            Plateforme
          </span>
          {platformLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className="text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <nav className="flex flex-col gap-2.5">
          <span className="text-xs font-semibold uppercase tracking-wider text-foreground/70">
            Mon espace
          </span>
          {accountLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className="text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <nav className="flex flex-col gap-2.5">
          <span className="text-xs font-semibold uppercase tracking-wider text-foreground/70">
            Légal
          </span>
          {legalLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className="text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>

      <div className="border-t border-border/80">
        <div className="mx-auto flex max-w-5xl flex-col-reverse items-center gap-3 px-4 py-5 text-xs text-muted-foreground sm:flex-row sm:justify-between sm:px-6">
          <span>© {year} {SITE_NAME}. Tous droits réservés.</span>
          <div className="flex items-center gap-1.5 font-medium text-foreground/70">
            <ShieldCheck className="size-3.5 shrink-0 text-primary" />
            Paiement sécurisé via Orange Money &amp; MTN Mobile Money
          </div>
        </div>
      </div>
    </footer>
  )
}
