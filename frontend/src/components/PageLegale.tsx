import type { ReactNode } from "react"
import { Link } from "react-router-dom"
import { ArrowLeft, Mail, MessageCircle, type LucideIcon } from "lucide-react"

import { useCountry } from "@/context/CountryContext"
import { epreuvesListPath } from "@/lib/countryPath"
import { SITE_DOMAIN } from "@/lib/site"

const CONTACT_EMAIL = `contact@${SITE_DOMAIN}`

export interface SectionLegale {
  id: string
  titre: string
  contenu: ReactNode
}

/** Liste à puces dorées, commune aux deux pages. */
export function ListeLegale({ children }: { children: ReactNode }) {
  return <ul className="mt-3 flex flex-col gap-2.5">{children}</ul>
}

export function PuceLegale({ children }: { children: ReactNode }) {
  return (
    <li className="flex gap-3">
      <span aria-hidden className="mt-[0.6rem] size-1.5 shrink-0 rounded-full bg-gold" />
      <span>{children}</span>
    </li>
  )
}

function Chip({ icone, children }: { icone: ReactNode; children: ReactNode }) {
  return (
    <span className="flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-sm">
      {icone}
      <span className="text-muted-foreground">{children}</span>
    </span>
  )
}

export function ChipLegale({ icone: Icone, className, children }: { icone: LucideIcon; className?: string; children: ReactNode }) {
  return <Chip icone={<Icone className={`size-3.5 ${className ?? "text-success"}`} />}>{children}</Chip>
}

/**
 * Gabarit des pages juridiques (CGU, confidentialité) : même largeur que les autres pages
 * du site (max-w-5xl), même hero que /tarifs, puis un sommaire collant à gauche et le texte
 * à droite - une colonne de lecture confortable, sans une boîte par paragraphe. Le contenu
 * lui-même vit dans chaque page ; ici seulement la présentation.
 */
export function PageLegale({
  icone: Icone, titre, introduction, puces, miseAJour, sections, voirAussi,
}: {
  icone: LucideIcon
  titre: string
  introduction: string
  puces: ReactNode
  miseAJour: string
  sections: SectionLegale[]
  voirAussi: { to: string; libelle: string }
}) {
  const { country } = useCountry()

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-8 sm:px-6 sm:py-10">
      <Link
        to={epreuvesListPath(country)}
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
      >
        <ArrowLeft className="size-4" />
        Retour au catalogue
      </Link>

      <div className="relative mb-10 overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-primary/[0.08] via-transparent to-transparent p-6 sm:p-10">
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
        <div className="pointer-events-none absolute -right-24 -top-24 size-72 rounded-full bg-gold/10 blur-3xl" aria-hidden />
        <div className="relative max-w-2xl">
          <div className="mb-3 flex size-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <Icone className="size-5" />
          </div>
          <p className="mb-1 font-display text-sm italic text-primary">Informations légales</p>
          <h1 className="font-display text-3xl font-semibold leading-[1.15] sm:text-4xl">{titre}</h1>
          <p className="mt-2 text-muted-foreground">{introduction}</p>
          <div className="mt-5 flex flex-wrap gap-2">{puces}</div>
          <p className="mt-5 text-xs text-muted-foreground">Dernière mise à jour : {miseAJour}</p>
        </div>
      </div>

      <div className="grid gap-10 lg:grid-cols-[14rem_minmax(0,1fr)] lg:gap-14">
        <nav aria-label="Sommaire" className="hidden lg:block">
          <ol className="sticky top-24 flex flex-col gap-1 border-l border-border text-sm">
            {sections.map((section, index) => (
              <li key={section.id}>
                <a
                  href={`#${section.id}`}
                  className="-ml-px flex gap-2.5 border-l border-transparent py-1.5 pl-4 text-muted-foreground transition-colors hover:border-primary hover:text-foreground"
                >
                  <span className="font-display tabular-nums text-primary/70">{String(index + 1).padStart(2, "0")}</span>
                  <span>{section.titre}</span>
                </a>
              </li>
            ))}
          </ol>
        </nav>

        <div className="min-w-0">
          <div className="flex max-w-[44rem] flex-col gap-10">
            {sections.map((section, index) => (
              <section key={section.id} id={section.id} className="scroll-mt-24">
                <p className="font-display text-sm tabular-nums text-primary/70">{String(index + 1).padStart(2, "0")}</p>
                <h2 className="mt-0.5 font-display text-xl font-semibold">{section.titre}</h2>
                <div className="mt-3 text-[0.95rem] leading-relaxed text-muted-foreground [&_strong]:font-medium [&_strong]:text-foreground">
                  {section.contenu}
                </div>
              </section>
            ))}
          </div>

          <div className="mt-14 flex max-w-[44rem] flex-col gap-5 rounded-2xl border border-border bg-card p-6 shadow-sm sm:flex-row sm:items-start">
            <span className="flex size-14 shrink-0 items-center justify-center rounded-full bg-primary font-display text-lg font-semibold text-primary-foreground ring-2 ring-gold/50 ring-offset-2 ring-offset-card">
              BSG
            </span>
            <div>
              <h2 className="font-display text-lg font-semibold">BABOUNLEK Serge Guyguy</h2>
              <p className="mt-0.5 text-sm text-muted-foreground">
                Éditeur de la plateforme - Yaoundé, Cameroun - +237 698 19 29 91
              </p>
              <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2">
                <a
                  href={`mailto:${CONTACT_EMAIL}`}
                  className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
                >
                  <Mail className="size-4" />
                  {CONTACT_EMAIL}
                </a>
                <a
                  href="https://wa.me/237670401393"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
                >
                  <MessageCircle className="size-4" />
                  WhatsApp +237 670 40 13 93
                </a>
              </div>
              <p className="mt-4 border-t border-border pt-3 text-sm text-muted-foreground">
                Voir aussi :{" "}
                <Link to={voirAussi.to} className="underline underline-offset-2 hover:text-foreground">
                  {voirAussi.libelle}
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
