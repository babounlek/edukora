import { Link } from "react-router-dom"
import {
  ArrowRight,
  BookOpen,
  Check,
  Heart,
  Landmark,
  Mail,
  MessageCircle,
  ShieldCheck,
  Smartphone,
} from "lucide-react"

import { useSeo } from "@/lib/seo"
import { SITE_DOMAIN, SITE_NAME } from "@/lib/site"
import { useCountry } from "@/context/CountryContext"
import { epreuvesListPath } from "@/lib/countryPath"
import { Button } from "@/components/ui/button"

const CONTACT_EMAIL = `contact@${SITE_DOMAIN}`

const PILLARS = [
  {
    label: "Épreuves",
    title: "Sujets officiels",
    body: "Les annales du BEPC, du Probatoire et du BAC, toujours consultables gratuitement. Le corrigé détaillé s'ouvre avec un abonnement.",
  },
  {
    label: "Cours",
    title: "Une notion à la fois",
    body: "La règle, la méthode, les erreurs classiques à éviter : pas un résumé vague recopié d'un manuel.",
  },
  {
    label: "Quiz",
    title: "Auto-évaluation ciblée",
    body: "Des questions par compétence pour savoir précisément ce qu'il te reste à travailler avant l'examen.",
  },
]

const METHOD_STEPS = [
  {
    title: "Sélection",
    body: "Uniquement des sujets réellement tombés à l'examen, jamais des exercices inventés pour l'occasion.",
  },
  {
    title: "Rédaction experte",
    body: "Un corrigé écrit à un niveau supérieur à celui d'un répétiteur classique : le raisonnement complet, pas seulement la réponse finale.",
  },
  {
    title: "Alignement au programme officiel",
    body: "Chaque cours est vérifié par rapport au référentiel officiel du pays, matière par matière, série par série.",
  },
  {
    title: "Vérification continue",
    body: "Chaque contenu publié est audité ; une erreur signalée est corrigée, pas simplement notée pour plus tard.",
  },
]

const AUDIENCES = [
  {
    icon: BookOpen,
    title: "Élève",
    points: [
      <><strong className="text-foreground">Les sujets sont toujours gratuits</strong>, avec ou sans compte.</>,
      "Le corrigé explique la méthode et les pièges, pas juste « la bonne réponse ».",
      "Un quiz d'auto-évaluation par compétence pour cibler ce qui te fait vraiment perdre des points.",
      "Accessible depuis un téléphone simple, aucune carte bancaire à saisir.",
    ],
  },
  {
    icon: ShieldCheck,
    title: "Parent",
    points: [
      <><strong className="text-foreground">Aucune carte bancaire enregistrée</strong> : paiement direct par Mobile Money (Orange Money, MTN).</>,
      "Aucune reconduction automatique : l'abonnement s'arrête à sa date, il ne se débite jamais tout seul.",
      "Un éditeur identifié et joignable, pas un site anonyme derrière un formulaire.",
      "Aucune donnée revendue ni utilisée à des fins publicitaires.",
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

const STATS = [
  { value: "15", label: "matières couvertes, des maths à la philosophie" },
  { value: "6", label: "séries : A, C, D, E, SES, TI" },
  { value: "3", label: "examens : BEPC, Probatoire, BAC" },
  { value: "1", label: "pays actif aujourd'hui : le Cameroun. D'autres pays francophones sont en préparation." },
]

function Eyebrow({ children }: { children: React.ReactNode }) {
  return (
    <p className="mb-3 flex items-center gap-2.5 font-display text-sm italic text-primary">
      <span className="h-px w-8 bg-gold" />
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

export function AboutPage() {
  useSeo({
    title: "À propos",
    description: `Qui est derrière ${SITE_NAME}, comment les corrigés sont produits, et pourquoi élèves, parents et établissements peuvent nous faire confiance.`,
  })
  const { country } = useCountry()

  return (
    <div className="animate-fade-up">
      {/* Hero - même gabarit de carte (bordure arrondie, fond pointillé, icône) que Tarifs,
          Fiches, CGU et Confidentialité : seule la mise en page à deux colonnes et la carte
          "18/20" restent propres à cette page. */}
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
              <div className="mb-3 flex size-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
                <Heart className="size-5" />
              </div>
              <Eyebrow>À propos</Eyebrow>
              <h1 className="font-display text-4xl font-semibold leading-[1.1] tracking-tight text-balance sm:text-5xl lg:text-[3.1rem]">
                Un bon corrigé ne devrait pas dépendre du portefeuille de tes parents.
              </h1>
              <p className="mt-5 max-w-xl text-lg leading-relaxed text-muted-foreground">
                {SITE_NAME} réunit les sujets officiels du BEPC, du Probatoire et du BAC, et les corrige à un niveau
                que peu de répétiteurs atteignent, accessible depuis un simple téléphone, payable en Mobile Money,
                sans carte bancaire ni engagement caché.
              </p>

              <div className="mt-5 flex flex-wrap gap-2">
                <ChipReassurance icon={<BookOpen className="size-3.5 text-primary" />}>
                  15 matières couvertes
                </ChipReassurance>
                <ChipReassurance icon={<ShieldCheck className="size-3.5 text-success" />}>
                  Sujets toujours gratuits
                </ChipReassurance>
                <ChipReassurance icon={<Smartphone className="size-3.5 text-gold" />}>
                  Mobile Money, sans carte
                </ChipReassurance>
              </div>

              <div className="mt-8 flex flex-wrap gap-3">
                <Button asChild size="lg">
                  <Link to={epreuvesListPath(country)}>
                    Découvrir le catalogue
                    <ArrowRight className="size-4" />
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline">
                  <Link to="/tarifs">Voir les tarifs</Link>
                </Button>
              </div>
            </div>

            <div className="relative mx-auto w-full max-w-[19rem] lg:mx-0 lg:justify-self-end">
              <span className="absolute -top-3 right-7 z-10 rotate-2 rounded-md bg-gold px-3 py-1 text-[0.65rem] font-bold uppercase tracking-wider text-gold-foreground shadow-md">
                Corrigé {SITE_NAME}
              </span>
              <div className="-rotate-2 rounded-lg border border-border bg-card p-7 shadow-xl transition-transform duration-300 hover:rotate-0">
                <div className="relative inline-flex items-center">
                  <span className="absolute -inset-x-3 -inset-y-2 -rotate-3 rounded-[50%] border-[2.5px] border-destructive/60" />
                  <span className="relative flex items-center gap-2 font-display text-4xl italic text-destructive">
                    18/20
                    <Check className="size-6 shrink-0" strokeWidth={3} />
                  </span>
                </div>
                <div className="my-4 h-px bg-gradient-to-r from-gold/0 via-gold/70 to-gold/0" />
                <p className="font-display text-base italic leading-relaxed text-muted-foreground">
                  « Raisonnement complet, méthode bien justifiée, aucun raccourci. »
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pillars */}
      <section className="mx-auto max-w-5xl px-4 py-14 sm:px-6">
        <Eyebrow>Ce que tu trouves ici</Eyebrow>
        <h2 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">
          Trois façons de préparer un examen sérieusement
        </h2>
        <div className="mt-10 grid grid-cols-1 gap-px overflow-hidden rounded-xl border border-border bg-border sm:grid-cols-3">
          {PILLARS.map((pillar) => (
            <div key={pillar.label} className="bg-card p-6">
              <span className="text-xs font-semibold uppercase tracking-wider text-primary">{pillar.label}</span>
              <h3 className="mt-2 font-display text-base font-semibold">{pillar.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{pillar.body}</p>
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
        <div className="mt-10 grid grid-cols-1 gap-5 sm:grid-cols-2">
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
              Découvrir le catalogue
              <ArrowRight className="size-4" />
            </Link>
          </Button>
        </div>
      </section>
    </div>
  )
}
