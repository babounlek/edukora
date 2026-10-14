import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import {
  ArrowRight,
  BookOpen,
  CalendarCheck,
  Check,
  FileText,
  Landmark,
  ListChecks,
  Mail,
  MessageCircle,
  ShieldCheck,
  Smartphone,
  Sparkles,
  TrendingUp,
  Users,
} from "lucide-react"

import { getPlatformStats, listCursus, listSubjects } from "@/api/endpoints"
import { useSeo } from "@/lib/seo"
import { nomPays } from "@/lib/pays"
import { SITE_NAME, CONTACT_EMAIL, CONTACT_WHATSAPP_URL, CONTACT_WHATSAPP_AFFICHAGE } from "@/lib/site"
import { useCountry } from "@/context/CountryContext"
import { catalogueHomePath, epreuvesListPath } from "@/lib/countryPath"
import { localeCourante, t, useI18n } from "@/lib/i18n"
import { texteRiche } from "@/lib/texteRiche"
import { Button } from "@/components/ui/button"


// Du plus tôt au plus tard dans la scolarité, pas l'ordre alphabétique de l'API.
const ORDRE_EXAMENS = ["BEPC", "PROBATOIRE", "BAC"]

// Construits au rendu (et non au chargement du module) pour suivre la langue courante.
function outils() {
  return [
    { icon: CalendarCheck, label: t("ab.outil1_label"), title: t("ab.outil1_titre"), body: t("ab.outil1_texte") },
    { icon: Sparkles, label: t("ab.outil2_label"), title: t("ab.outil2_titre"), body: t("ab.outil2_texte") },
    { icon: TrendingUp, label: t("ab.outil3_label"), title: t("ab.outil3_titre"), body: t("ab.outil3_texte") },
    { icon: FileText, label: t("ab.outil4_label"), title: t("ab.outil4_titre"), body: t("ab.outil4_texte") },
    { icon: BookOpen, label: t("ab.outil5_label"), title: t("ab.outil5_titre"), body: t("ab.outil5_texte") },
    { icon: ListChecks, label: t("ab.outil6_label"), title: t("ab.outil6_titre"), body: t("ab.outil6_texte") },
  ]
}

function etapesMethode() {
  return [
    { title: t("ab.etape1_titre"), body: t("ab.etape1_texte") },
    { title: t("ab.etape2_titre"), body: t("ab.etape2_texte") },
    { title: t("ab.etape3_titre"), body: t("ab.etape3_texte") },
    { title: t("ab.etape4_titre"), body: t("ab.etape4_texte") },
  ]
}

function publics() {
  return [
    {
      icon: BookOpen,
      title: t("ab.aud1_titre"),
      points: [t("ab.aud1_p1"), t("ab.aud1_p2"), t("ab.aud1_p3"), t("ab.aud1_p4")],
    },
    {
      icon: Users,
      title: t("ab.aud2_titre"),
      points: [t("ab.aud2_p1"), t("ab.aud2_p2"), t("ab.aud2_p3"), t("ab.aud2_p4")],
    },
    {
      icon: Landmark,
      title: t("ab.aud3_titre"),
      points: [t("ab.aud3_p1"), t("ab.aud3_p2"), t("ab.aud3_p3"), t("ab.aud3_p4")],
    },
  ]
}

function engagements() {
  return [
    { title: t("ab.eng1_titre"), body: t("ab.eng1_texte") },
    { title: t("ab.eng2_titre"), body: t("ab.eng2_texte") },
    { title: t("ab.eng3_titre"), body: t("ab.eng3_texte") },
    { title: t("ab.eng4_titre"), body: t("ab.eng4_texte") },
  ]
}

function Eyebrow({ children }: { children: React.ReactNode }) {
  return (
    <p className="mb-3 flex items-center gap-2.5 font-display text-sm italic text-primary">
      {children}
    </p>
  )
}

function ChipReassurance({ icon, children }: { icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <span className="flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-sm">
      {icon}
      <span className="text-muted-foreground">{children}</span>
    </span>
  )
}

/** "A, C, D, E et TI" / "A, C, D, E and TI" : liste lisible dans la langue courante. */
function listeLisible(items: string[]): string {
  return new Intl.ListFormat(localeCourante(), { style: "long", type: "conjunction" }).format(items)
}

export function AboutPage() {
  useI18n()
  useSeo({
    title: t("ab.seo_titre"),
    description: t("ab.seo_description", { site: SITE_NAME }),
  })
  const { country, countries } = useCountry()
  const countryLabel = nomPays(countries, country)

  // Chiffres réels, jamais codés en dur : ils ont dérivé plus d'une fois de la
  // réalité du catalogue. Mêmes clés de cache que le pied de page et l'accueil.
  // Toutes langues confondues : la page présente la plateforme entière, matières et parcours compris.
  const { data: stats } = useQuery({ queryKey: ["platform-stats"], queryFn: () => getPlatformStats() })
  const { data: subjects } = useQuery({
    queryKey: ["subjects", country],
    queryFn: ({ signal }) => listSubjects(country, signal),
    enabled: Boolean(country),
  })
  const { data: cursusList } = useQuery({
    queryKey: ["cursus", country],
    queryFn: ({ signal }) => listCursus(country, signal),
    enabled: Boolean(country),
  })

  const nbMatieres = subjects?.length
  const examens = [...new Map(
    [...(cursusList ?? [])]
      .sort((a, b) => (ORDRE_EXAMENS.indexOf(a.examen) + 1 || 99) - (ORDRE_EXAMENS.indexOf(b.examen) + 1 || 99))
      .map((c) => [c.examen, c.examen_display] as const),
  ).values()]
  const series = [...new Set((cursusList ?? []).flatMap((c) => (c.series ? [c.series.code] : [])))].sort()

  const STATS = [
    { value: stats ? new Intl.NumberFormat(localeCourante()).format(stats.corriges_disponibles) : "-", label: t("ab.stat_corriges") },
    { value: stats ? new Intl.NumberFormat(localeCourante()).format(stats.cours_disponibles) : "-", label: t("ab.stat_cours") },
    { value: nbMatieres !== undefined ? String(nbMatieres) : "-", label: t("ab.stat_matieres") },
    {
      value: cursusList ? String(cursusList.length) : "-",
      label: cursusList
        ? t("ab.stat_parcours", {
            examens: listeLisible(examens),
            series: series.length > 0 ? t("ab.stat_series", { series: listeLisible(series) }) : "",
          })
        : t("ab.stat_parcours_vide"),
    },
  ]

  return (
    <div className="animate-fade-up">
      {/* Hero - même gabarit de carte (bordure arrondie, fond pointillé, icône) que Tarifs,
          Fiches, CGU et Confidentialité : seule la mise en page à deux colonnes et la carte
          "séance du jour" restent propres à cette page. */}
      <section className="mx-auto max-w-5xl px-4 pt-8 sm:px-6">
        <div className="relative overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-primary/[0.07] via-transparent to-transparent p-6 sm:p-8 lg:p-12">
          <div
            className="absolute inset-0 opacity-[0.04]"
            style={{
              backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
              backgroundSize: "24px 24px",
            }}
          />
          <div className="relative grid gap-12 lg:grid-cols-[1.2fr_0.8fr] lg:items-center lg:gap-16">
            <div>
              <Eyebrow>{t("ab.eyebrow")}</Eyebrow>
              <h1 className="font-display text-4xl font-semibold leading-[1.1] tracking-tight text-balance sm:text-5xl lg:text-[3.1rem]">
                {t("ab.h1")}
              </h1>
              <p className="mt-5 max-w-xl text-lg leading-relaxed text-muted-foreground">
                {t("ab.hero_texte", { site: SITE_NAME })}
              </p>

              <div className="mt-5 flex flex-wrap gap-2">
                <ChipReassurance icon={<BookOpen className="size-3.5 text-primary" />}>
                  {nbMatieres !== undefined ? t("ab.chip_matieres", { n: nbMatieres }) : t("ab.chip_toutes")}
                </ChipReassurance>
                <ChipReassurance icon={<ShieldCheck className="size-3.5 text-success" />}>
                  {t("ab.chip_gratuits")}
                </ChipReassurance>
                <ChipReassurance icon={<Smartphone className="size-3.5 text-gold-text" />}>
                  {t("ab.chip_momo")}
                </ChipReassurance>
              </div>

              <div className="mt-8 flex flex-wrap gap-3">
                <Button asChild size="lg">
                  <Link to={catalogueHomePath(country)}>
                    {t("ab.commencer")}
                    <ArrowRight className="size-4" />
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline">
                  <Link to="/tarifs">{t("ft.voir_prix")}</Link>
                </Button>
              </div>
            </div>

            {/* La séance du jour en un coup d'œil : la forme, sans données inventées. */}
            <div className="relative mx-auto w-full max-w-[19rem] lg:mx-0 lg:justify-self-end">
              <span className="absolute -top-3 right-7 z-10 rotate-2 rounded-md bg-gold px-3 py-1 text-[0.65rem] font-bold uppercase tracking-wider text-gold-foreground shadow-md">
                {t("ab.carte_etiquette")}
              </span>
              <div className="-rotate-2 rounded-lg border border-border bg-card p-6 shadow-xl transition-transform duration-300 hover:rotate-0">
                <p className="flex items-baseline justify-between text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                  {t("ab.carte_parcours")}
                  <span className="font-sans normal-case tracking-normal tabular-nums">{t("ab.carte_duree")}</span>
                </p>
                <ol className="mt-4 flex flex-col gap-3">
                  {[
                    { icon: BookOpen, titre: t("ab.carte_cours"), detail: t("ab.carte_cours_detail") },
                    { icon: FileText, titre: t("ab.carte_exercice"), detail: t("ab.carte_exercice_detail") },
                    { icon: ListChecks, titre: t("ab.carte_quiz"), detail: t("ab.carte_quiz_detail") },
                  ].map(({ icon: Icon, titre, detail }, index) => (
                    <li key={titre} className="flex items-center gap-3">
                      <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground shadow-sm shadow-primary/30">
                        {index + 1}
                      </span>
                      <span className="min-w-0 flex-1">
                        <span className="flex items-center gap-1.5 font-display text-sm font-semibold">
                          <Icon className="size-3.5 text-primary" aria-hidden="true" />
                          {titre}
                        </span>
                        <span className="block text-xs text-muted-foreground">{detail}</span>
                      </span>
                    </li>
                  ))}
                </ol>
                <div className="my-4 h-px bg-gradient-to-r from-gold/0 via-gold/70 to-gold/0" />
                <p className="font-display text-sm italic leading-relaxed text-muted-foreground">
                  {t("ab.carte_citation")}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Outils */}
      <section className="mx-auto max-w-5xl px-4 py-14 sm:px-6">
        <Eyebrow>{t("ab.outils_eyebrow")}</Eyebrow>
        <h2 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">
          {t("ab.outils_titre")}
        </h2>
        <div className="mt-10 grid grid-cols-1 gap-px overflow-hidden rounded-xl border border-border bg-border sm:grid-cols-2 lg:grid-cols-3">
          {outils().map((outil) => (
            <div key={outil.label} className="bg-card p-6">
              <div className="flex items-center gap-2.5">
                <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <outil.icon className="size-4" aria-hidden="true" />
                </span>
                <span className="text-xs font-semibold uppercase tracking-wider text-primary">{outil.label}</span>
              </div>
              <h3 className="mt-3 font-display text-base font-semibold">{outil.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{outil.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Method */}
      <section className="mx-auto max-w-5xl px-4 py-14 sm:px-6">
        <Eyebrow>{t("ab.methode_eyebrow")}</Eyebrow>
        <h2 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">
          {t("ab.methode_titre")}
        </h2>
        <p className="mt-2 max-w-xl text-sm text-muted-foreground">
          {t("ab.methode_texte")}
        </p>
        <div className="mt-10 max-w-2xl border-l border-border">
          {etapesMethode().map((step, index) => (
            <div key={step.title} className="relative py-2 pl-9 pb-9 last:pb-0">
              <span className="absolute -left-4 top-0 flex size-8 items-center justify-center rounded-full border border-border bg-background font-display text-sm font-semibold tabular-nums text-primary">
                {String(index + 1).padStart(2, "0")}
              </span>
              <h3 className="font-display text-base font-semibold">{step.title}</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{step.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Audiences */}
      <section className="mx-auto max-w-5xl px-4 py-14 sm:px-6">
        <Eyebrow>{t("ab.aud_eyebrow")}</Eyebrow>
        <h2 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">
          {t("ab.aud_titre", { site: SITE_NAME })}
        </h2>
        <div className="mt-10 grid grid-cols-1 gap-5 lg:grid-cols-3">
          {publics().map((audience) => (
            <div
              key={audience.title}
              className="rounded-xl border border-border bg-card p-6 shadow-sm transition-shadow duration-300 hover:shadow-md"
            >
              <div className="flex items-center gap-3">
                <span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-accent text-primary">
                  <audience.icon className="size-5" />
                </span>
                <h3 className="font-display text-lg font-semibold">{audience.title}</h3>
              </div>
              <ul className="mt-4 flex flex-col gap-2.5">
                {audience.points.map((point, index) => (
                  <li key={index} className="flex gap-2.5 text-sm leading-relaxed text-muted-foreground">
                    <span className="mt-2 size-1.5 shrink-0 rounded-full bg-gold" />
                    <span>{texteRiche(point)}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* Commitments */}
      <section className="border-y border-border bg-secondary/30">
        <div className="mx-auto max-w-5xl px-4 py-14 sm:px-6">
          <Eyebrow>{t("ab.eng_eyebrow")}</Eyebrow>
          <h2 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">
            {t("ab.eng_titre")}
          </h2>
          <div className="mt-10 grid grid-cols-1 gap-x-10 gap-y-6 sm:grid-cols-2">
            {engagements().map((commitment) => (
              <div key={commitment.title} className="flex gap-3.5">
                <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-destructive/10 text-destructive">
                  <Check className="size-4" />
                </span>
                <div>
                  <h3 className="font-display text-base font-semibold">{commitment.title}</h3>
                  <p className="mt-1 text-sm leading-relaxed text-muted-foreground">{commitment.body}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Coverage */}
      <section className="mx-auto max-w-5xl px-4 py-14 sm:px-6">
        <Eyebrow>{t("ab.couv_eyebrow")}</Eyebrow>
        <h2 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">{t("ab.couv_titre")}</h2>
        <div className="mt-10 grid grid-cols-1 gap-px overflow-hidden rounded-xl border border-border bg-border sm:grid-cols-2 lg:grid-cols-4">
          {STATS.map((stat) => (
            <div key={stat.label} className="bg-card p-6">
              <div className="font-display text-4xl font-semibold tabular-nums text-primary">{stat.value}</div>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{stat.label}</p>
            </div>
          ))}
        </div>
        <p className="mt-4 text-sm text-muted-foreground">
          {countryLabel ? t("ab.pays_un", { pays: countryLabel }) : t("ab.pays_un_sans")}{" "}
          {t("ab.pays_autres")}
        </p>
      </section>

      {/* Qui sommes-nous */}
      <section className="mx-auto max-w-5xl px-4 py-14 sm:px-6">
        <Eyebrow>{t("ab.qui_eyebrow")}</Eyebrow>
        <h2 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">
          {t("ab.qui_titre")}
        </h2>
        <div className="mt-10 flex flex-col gap-6 rounded-xl border border-border bg-card p-7 shadow-sm sm:flex-row sm:items-start">
          <span className="flex size-16 shrink-0 items-center justify-center rounded-full bg-primary font-display text-xl font-semibold text-primary-foreground ring-2 ring-gold/50 ring-offset-2 ring-offset-card">
            BSG
          </span>
          <div>
            <h3 className="font-display text-lg font-semibold">BABOUNLEK Serge Guyguy</h3>
            <p className="mt-0.5 text-sm text-muted-foreground">{t("ab.qui_lieu")}</p>
            <div className="mt-4 flex flex-wrap gap-5">
              <a
                href={`mailto:${CONTACT_EMAIL}`}
                className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
              >
                <Mail className="size-4" />
                {CONTACT_EMAIL}
              </a>
              <a
                href={CONTACT_WHATSAPP_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
              >
                <MessageCircle className="size-4" />
                WhatsApp {CONTACT_WHATSAPP_AFFICHAGE}
              </a>
            </div>
            <p className="mt-5 border-t border-border pt-4 text-sm text-muted-foreground">
              {t("ab.qui_legal")}{" "}
              <Link to="/cgu" className="underline underline-offset-2 hover:text-foreground">
                {t("conf.voir_aussi")}
              </Link>{" "}
              ·{" "}
              <Link to="/confidentialite" className="underline underline-offset-2 hover:text-foreground">
                {t("cgu.voir_aussi")}
              </Link>
            </p>
          </div>
        </div>
      </section>

      {/* CTA band */}
      <section className="bg-primary">
        <div className="mx-auto flex max-w-5xl flex-col items-center gap-5 px-4 py-14 text-center sm:flex-row sm:justify-between sm:px-6 sm:text-left">
          <h2 className="font-display text-2xl font-semibold tracking-tight text-primary-foreground sm:text-3xl">
            {t("ab.cta_titre")}
          </h2>
          <Button asChild size="lg" className="shrink-0 bg-gold text-gold-foreground hover:bg-gold/90">
            <Link to={epreuvesListPath(country)}>
              {t("ab.cta_bouton")}
              <ArrowRight className="size-4" />
            </Link>
          </Button>
        </div>
      </section>
    </div>
  )
}
