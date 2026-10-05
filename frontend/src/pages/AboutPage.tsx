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
import { SITE_DOMAIN, SITE_NAME } from "@/lib/site"
import { useCountry } from "@/context/CountryContext"
import { catalogueHomePath, epreuvesListPath } from "@/lib/countryPath"
import { formatAmount } from "@/lib/utils"
import { Button } from "@/components/ui/button"

const CONTACT_EMAIL = `contact@${SITE_DOMAIN}`

// Du plus tôt au plus tard dans la scolarité, pas l'ordre alphabétique de l'API.
const ORDRE_EXAMENS = ["BEPC", "PROBATOIRE", "BAC"]

const OUTILS = [
  {
    icon: CalendarCheck,
    label: "Séance du jour",
    title: "Chaque jour, on te dit quoi réviser",
    body: "Un thème qui tombe vraiment à ton examen : le cours pour la méthode, un exercice réellement posé, un quiz pour vérifier. Environ 25 minutes.",
  },
  {
    icon: Sparkles,
    label: "Mémoire",
    title: "On retient ce que tu rates",
    body: "Un thème raté revient demain, puis dans trois jours, puis dans une semaine, jusqu'à ce qu'il soit acquis. Tu n'as rien à noter ni à planifier.",
  },
  {
    icon: TrendingUp,
    label: "Thèmes qui reviennent",
    title: "Ce qui tombe vraiment",
    body: "Le classement des notions les plus posées à ton examen, matière par matière, calculé sur les épreuves officielles. Un thème traité trois fois dans un même sujet ne compte qu'une fois.",
  },
  {
    icon: FileText,
    label: "Épreuves corrigées",
    title: "Les annales officielles",
    body: "Les sujets du BEPC, du Probatoire et du BAC sont toujours consultables gratuitement. Le corrigé détaillé, pas à pas, s'ouvre avec l'abonnement.",
  },
  {
    icon: BookOpen,
    label: "Cours et quiz",
    title: "La méthode, puis le test",
    body: "Un cours par méthode : la règle, la façon de faire, les pièges classiques. Puis un quiz d'auto-évaluation par compétence pour voir ce qui reste fragile.",
  },
  {
    icon: ListChecks,
    label: "Épreuves inédites",
    title: "S'entraîner comme le jour J",
    body: "Des sujets originaux, jamais tirés des annales, au même niveau et au même barème que l'examen, à composer chronométrés.",
  },
]

const METHOD_STEPS = [
  {
    title: "Sélection",
    body: "Les corrigés portent uniquement sur des sujets réellement tombés à l'examen. Les épreuves inédites sont, elles, toujours signalées comme telles.",
  },
  {
    title: "Rédaction experte",
    body: "Un corrigé écrit à un niveau supérieur à celui d'un répétiteur classique : le raisonnement complet, pas seulement la réponse finale.",
  },
  {
    title: "Classement par thème",
    body: "Chaque question est rattachée aux notions qu'elle mobilise. C'est ce qui permet de savoir ce qui tombe vraiment, et de te proposer la bonne séance.",
  },
  {
    title: "Contrôle avant publication",
    body: "La structure, les thèmes et l'affichage des formules sont vérifiés avant qu'un contenu soit mis en ligne. Une erreur signalée est corrigée, pas simplement notée pour plus tard.",
  },
]

const AUDIENCES = [
  {
    icon: BookOpen,
    title: "Élève",
    points: [
      <><strong className="text-foreground">Les sujets sont toujours gratuits</strong>, avec ou sans compte.</>,
      "Une séance courte chaque jour qui te dit quoi réviser, au lieu de te laisser chercher seul·e parmi des milliers de pages.",
      "Le corrigé explique la méthode et les pièges, pas juste « la bonne réponse ».",
      "Accessible depuis un téléphone simple, aucune carte bancaire à saisir.",
    ],
  },
  {
    icon: Users,
    title: "Parent",
    points: [
      <><strong className="text-foreground">Un seul compte pour plusieurs enfants</strong> : chacun a son profil, sa progression et son abonnement.</>,
      "Un abonnement unique, valable jusqu'à l'examen, dont le prix payé est figé le jour de l'achat.",
      "Paiement direct par Mobile Money (Orange Money, MTN), sans carte bancaire et sans reconduction automatique.",
      "Un éditeur identifié et joignable, et aucune donnée revendue ni utilisée à des fins publicitaires.",
    ],
  },
  {
    icon: Landmark,
    title: "Établissement & autorité éducative",
    points: [
      <><strong className="text-foreground">Éditeur identifié et localisé</strong>, responsable de son contenu (voir « Qui sommes-nous » ci-dessous).</>,
      "Les sujets utilisés sont les épreuves officielles déjà publiques ; les corrigés sont un travail original propre à la plateforme.",
      "Données personnelles réduites au strict nécessaire (téléphone, e-mail ou compte Google selon la méthode de connexion), jamais revendues.",
      "Ouverts à échanger avec les établissements et les autorités éducatives sur le contenu et son usage.",
    ],
  },
]

const COMMITMENTS = [
  {
    title: "Pas de faux témoignages",
    body: "Les avis affichés ne sont publiés que s'ils sont réels. Sans avis vérifié, cette section de la page disparaît ; elle ne se remplit jamais de contenu fabriqué.",
  },
  {
    title: "Pas de carte bancaire enregistrée",
    body: "Seul le Mobile Money passe par notre prestataire de paiement ; nous ne recevons ni ne stockons jamais tes identifiants.",
  },
  {
    title: "Pas de reconduction automatique",
    body: "Un abonnement expire, il ne se renouvelle jamais tout seul sans une action de ta part.",
  },
  {
    title: "Pas de revente de données",
    body: "Aucune donnée personnelle n'est partagée à des fins publicitaires. Détails dans notre politique de confidentialité.",
  },
]

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

/** "A, C, D, E et TI" : liste lisible, sans dépendre d'un tableau codé en dur. */
function listeFrancaise(items: string[]): string {
  if (items.length <= 1) return items.join("")
  return `${items.slice(0, -1).join(", ")} et ${items[items.length - 1]}`
}

export function AboutPage() {
  useSeo({
    title: "À propos",
    description: `Qui est derrière ${SITE_NAME}, comment fonctionnent la séance du jour et les corrigés, et pourquoi élèves, parents et établissements peuvent nous faire confiance.`,
  })
  const { country, countries } = useCountry()
  const countryLabel = countries.find((c) => c.code.toLowerCase() === country)?.label

  // Chiffres réels, jamais codés en dur : ils ont dérivé plus d'une fois de la
  // réalité du catalogue. Mêmes clés de cache que le pied de page et l'accueil.
  const { data: stats } = useQuery({ queryKey: ["platform-stats"], queryFn: getPlatformStats })
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
    { value: stats ? formatAmount(stats.corriges_disponibles) : "-", label: "épreuves corrigées, annales officielles et épreuves inédites" },
    { value: stats ? formatAmount(stats.cours_disponibles) : "-", label: "cours et fiches, une notion à la fois" },
    { value: nbMatieres !== undefined ? String(nbMatieres) : "-", label: "matières couvertes, des maths à la philosophie" },
    {
      value: cursusList ? String(cursusList.length) : "-",
      label: cursusList
        ? `parcours d'examen : ${listeFrancaise(examens)}${series.length > 0 ? `, séries ${listeFrancaise(series)}` : ""}`
        : "parcours d'examen",
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
              <Eyebrow>À propos</Eyebrow>
              <h1 className="font-display text-4xl font-semibold leading-[1.1] tracking-tight text-balance sm:text-5xl lg:text-[3.1rem]">
                Réviser ce qui tombe vraiment, un peu chaque jour.
              </h1>
              <p className="mt-5 max-w-xl text-lg leading-relaxed text-muted-foreground">
                {SITE_NAME} réunit les sujets officiels du BEPC, du Probatoire et du BAC, les corrige à un niveau que
                peu de répétiteurs atteignent, et en tire chaque jour une séance courte sur les thèmes les plus posés à
                ton examen. Accessible depuis un simple téléphone, payable en Mobile Money, sans carte bancaire ni
                engagement caché.
              </p>

              <div className="mt-5 flex flex-wrap gap-2">
                <ChipReassurance icon={<BookOpen className="size-3.5 text-primary" />}>
                  {nbMatieres !== undefined ? `${nbMatieres} matières couvertes` : "Toutes les matières"}
                </ChipReassurance>
                <ChipReassurance icon={<ShieldCheck className="size-3.5 text-success" />}>
                  Sujets toujours gratuits
                </ChipReassurance>
                <ChipReassurance icon={<Smartphone className="size-3.5 text-gold-text" />}>
                  Mobile Money, sans carte
                </ChipReassurance>
              </div>

              <div className="mt-8 flex flex-wrap gap-3">
                <Button asChild size="lg">
                  <Link to={catalogueHomePath(country)}>
                    Commencer
                    <ArrowRight className="size-4" />
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline">
                  <Link to="/tarifs">Voir les prix</Link>
                </Button>
              </div>
            </div>

            {/* La séance du jour en un coup d'œil : la forme, sans données inventées. */}
            <div className="relative mx-auto w-full max-w-[19rem] lg:mx-0 lg:justify-self-end">
              <span className="absolute -top-3 right-7 z-10 rotate-2 rounded-md bg-gold px-3 py-1 text-[0.65rem] font-bold uppercase tracking-wider text-gold-foreground shadow-md">
                Séance du jour
              </span>
              <div className="-rotate-2 rounded-lg border border-border bg-card p-6 shadow-xl transition-transform duration-300 hover:rotate-0">
                <p className="flex items-baseline justify-between text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                  Ton parcours
                  <span className="font-sans normal-case tracking-normal tabular-nums">environ 25 min</span>
                </p>
                <ol className="mt-4 flex flex-col gap-3">
                  {[
                    { icon: BookOpen, titre: "Le cours", detail: "la méthode, sans détour" },
                    { icon: FileText, titre: "Un exercice", detail: "réellement posé à l'examen" },
                    { icon: ListChecks, titre: "Un quiz", detail: "pour vérifier que c'est acquis" },
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
                  « Un thème qui tombe vraiment : on te dit dans combien des dernières épreuves. »
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Outils */}
      <section className="mx-auto max-w-5xl px-4 py-14 sm:px-6">
        <Eyebrow>Ce que tu trouves ici</Eyebrow>
        <h2 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">
          Six outils, un seul objectif : ton examen
        </h2>
        <div className="mt-10 grid grid-cols-1 gap-px overflow-hidden rounded-xl border border-border bg-border sm:grid-cols-2 lg:grid-cols-3">
          {OUTILS.map((outil) => (
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
        <Eyebrow>Notre méthode</Eyebrow>
        <h2 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">
          La rigueur derrière chaque corrigé
        </h2>
        <p className="mt-2 max-w-xl text-sm text-muted-foreground">
          Quatre étapes, dans cet ordre, pour chaque contenu publié, jamais l'inverse.
        </p>
        <div className="mt-10 max-w-2xl border-l border-border">
          {METHOD_STEPS.map((step, index) => (
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
        <Eyebrow>Que tu sois...</Eyebrow>
        <h2 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">
          Ce qu'{SITE_NAME} te doit, concrètement
        </h2>
        <div className="mt-10 grid grid-cols-1 gap-5 lg:grid-cols-3">
          {AUDIENCES.map((audience) => (
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
                    <span>{point}</span>
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
          <Eyebrow>Nos engagements</Eyebrow>
          <h2 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">
            Ce que nous ne ferons jamais
          </h2>
          <div className="mt-10 grid grid-cols-1 gap-x-10 gap-y-6 sm:grid-cols-2">
            {COMMITMENTS.map((commitment) => (
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
        <Eyebrow>Couverture</Eyebrow>
        <h2 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">Ce qui est déjà en place</h2>
        <div className="mt-10 grid grid-cols-1 gap-px overflow-hidden rounded-xl border border-border bg-border sm:grid-cols-2 lg:grid-cols-4">
          {STATS.map((stat) => (
            <div key={stat.label} className="bg-card p-6">
              <div className="font-display text-4xl font-semibold tabular-nums text-primary">{stat.value}</div>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{stat.label}</p>
            </div>
          ))}
        </div>
        <p className="mt-4 text-sm text-muted-foreground">
          {countryLabel ? `Un seul pays est actif aujourd'hui : ${countryLabel}.` : "Un seul pays est actif aujourd'hui."}{" "}
          D'autres pays francophones sont en préparation.
        </p>
      </section>

      {/* Qui sommes-nous */}
      <section className="mx-auto max-w-5xl px-4 py-14 sm:px-6">
        <Eyebrow>Qui sommes-nous</Eyebrow>
        <h2 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">
          Un éditeur identifié, pas un site anonyme
        </h2>
        <div className="mt-10 flex flex-col gap-6 rounded-xl border border-border bg-card p-7 shadow-sm sm:flex-row sm:items-start">
          <span className="flex size-16 shrink-0 items-center justify-center rounded-full bg-primary font-display text-xl font-semibold text-primary-foreground ring-2 ring-gold/50 ring-offset-2 ring-offset-card">
            BSG
          </span>
          <div>
            <h3 className="font-display text-lg font-semibold">BABOUNLEK Serge Guyguy</h3>
            <p className="mt-0.5 text-sm text-muted-foreground">Yaoundé, Cameroun</p>
            <div className="mt-4 flex flex-wrap gap-5">
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
            <p className="mt-5 border-t border-border pt-4 text-sm text-muted-foreground">
              Détails légaux complets :{" "}
              <Link to="/cgu" className="underline underline-offset-2 hover:text-foreground">
                Conditions d'utilisation
              </Link>{" "}
              ·{" "}
              <Link to="/confidentialite" className="underline underline-offset-2 hover:text-foreground">
                Politique de confidentialité
              </Link>
            </p>
          </div>
        </div>
      </section>

      {/* CTA band */}
      <section className="bg-primary">
        <div className="mx-auto flex max-w-5xl flex-col items-center gap-5 px-4 py-14 text-center sm:flex-row sm:justify-between sm:px-6 sm:text-left">
          <h2 className="font-display text-2xl font-semibold tracking-tight text-primary-foreground sm:text-3xl">
            Prêt·e à voir ce qu'un vrai corrigé peut faire ?
          </h2>
          <Button asChild size="lg" className="shrink-0 bg-gold text-gold-foreground hover:bg-gold/90">
            <Link to={epreuvesListPath(country)}>
              Parcourir les épreuves
              <ArrowRight className="size-4" />
            </Link>
          </Button>
        </div>
      </section>
    </div>
  )
}
