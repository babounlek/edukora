import type { ReactNode } from "react"
import { Link, useLocation } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, ChevronDown, MessageCircle, ShieldCheck, Sparkles } from "lucide-react"

import { getPlatformStats, listCursus } from "@/api/endpoints"
import type { Cursus, User } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { SITE_DOMAIN, SITE_NAME } from "@/lib/site"
import { catalogueHomePath, coursListPath, epreuvesListPath, themesFrequentsPath } from "@/lib/countryPath"
import { cn, formatAmount } from "@/lib/utils"

const CONTACT_EMAIL = `contact@${SITE_DOMAIN}`
const CONTACT_WHATSAPP_URL = "https://wa.me/237670401393"

// Ordre de lecture d'un élève : du premier examen au dernier.
const ORDRE_EXAMENS = ["BEPC", "Probatoire", "BAC"]

interface Invitation {
  message: ReactNode
  bouton: string
  lien: string
  secondaire?: { label: string; lien: string }
}

function libelleCursus(c: Pick<Cursus, "examen_display" | "series">) {
  return `${c.examen_display}${c.series ? ` ${c.series.code}` : ""}`
}

/** Le compte à rebours en une phrase - au mois près quand la date n'est qu'estimée
 * (voir CompteARebours.estimee : jamais un nombre de jours sur une date supposée). */
function phraseCompteARebours(user: User) {
  const cr = user.compte_a_rebours
  if (!cr || cr.jours_restants < 0) return null
  if (cr.estimee) {
    const mois = Math.max(1, Math.round(cr.jours_restants / 30))
    return `${cr.session_label} dans environ ${mois} mois`
  }
  return `${cr.session_label} dans ${cr.jours_restants} jour${cr.jours_restants > 1 ? "s" : ""}`
}

/**
 * L'appel à l'action du bas de page, selon qui lit : on ne dit pas la même chose à un
 * visiteur, à un élève inscrit mais pas abonné, et à un abonné qui a sa séance à faire.
 * Aucune requête de plus : tout vient de l'utilisateur déjà chargé (compte à rebours,
 * cursus déclaré, abonnement actif).
 */
function invitationPour(user: User | null, country: string): Invitation {
  if (!user) {
    return {
      message: (
        <>
          Corrigés détaillés, quiz et thèmes qui tombent vraiment :{" "}
          <span className="text-primary">commence gratuitement.</span>
        </>
      ),
      bouton: "Créer mon compte",
      lien: "/connexion",
      secondaire: { label: "Voir les tarifs", lien: "/tarifs" },
    }
  }
  const compteARebours = phraseCompteARebours(user)
  if (!user.a_un_abonnement_actif) {
    const cursus = user.cursus_prepare ? libelleCursus(user.cursus_prepare) : null
    return {
      message: (
        <>
          {compteARebours ? `${compteARebours}. ` : ""}
          Débloque tous les corrigés{cursus ? ` de ton ${cursus}` : ""}{" "}
          <span className="text-primary">et révise ce qui tombe vraiment.</span>
        </>
      ),
      bouton: "Voir les tarifs",
      lien: "/tarifs",
    }
  }
  return {
    message: (
      <>
        {compteARebours ? `${compteARebours} · ` : ""}
        <span className="text-primary">{compteARebours ? "ta" : "Ta"} séance du jour est prête.</span>
      </>
    ),
    bouton: "Faire ma séance",
    lien: catalogueHomePath(country),
  }
}

/** Une colonne de liens : repliable sur téléphone (la pile de quatre colonnes y faisait
 * ~700 px), toujours dépliée dès `sm`. Deux rendus plutôt qu'un <details> forcé ouvert :
 * l'état ouvert d'un <details> ne se pilote pas en CSS. */
function Colonne({ titre, children }: { titre: string; children: ReactNode }) {
  const entete = "text-xs font-semibold uppercase tracking-[0.14em] text-foreground/70"
  return (
    <>
      <details className="group border-b border-border/70 sm:hidden">
        <summary className={cn(entete, "flex cursor-pointer list-none items-center justify-between py-3.5")}>
          {titre}
          <ChevronDown className="size-4 text-muted-foreground transition-transform group-open:rotate-180" />
        </summary>
        <nav aria-label={`Pied de page : ${titre.toLowerCase()}`} className="flex flex-col gap-3 pb-4">
          {children}
        </nav>
      </details>
      <nav aria-label={`Pied de page : ${titre.toLowerCase()}`} className="hidden flex-col gap-2.5 sm:flex">
        <span className={cn(entete, "mb-1")}>{titre}</span>
        {children}
      </nav>
    </>
  )
}

function Lien({ to, children, vedette }: { to: string; children: ReactNode; vedette?: boolean }) {
  return (
    <Link
      to={to}
      className={cn(
        "inline-flex w-fit items-center gap-1.5 text-sm transition-colors hover:text-primary",
        vedette ? "font-medium text-foreground" : "text-muted-foreground",
      )}
    >
      {children}
    </Link>
  )
}

export function Footer() {
  const year = new Date().getFullYear()
  const { country } = useCountry()
  const { user, isAuthenticated } = useAuth()
  const { pathname } = useLocation()

  // Chiffres réels, jamais codés en dur (voir project_about_page_hardcoded_stats) : un
  // compteur figé finit toujours par mentir.
  const { data: stats } = useQuery({
    queryKey: ["platform-stats"],
    queryFn: getPlatformStats,
    staleTime: 60 * 60 * 1000,
  })
  // Même clé que /epreuves et /themes-frequents : déjà en cache la plupart du temps.
  const { data: cursusList = [] } = useQuery({
    queryKey: ["cursus", country],
    queryFn: ({ signal }) => listCursus(country, signal),
  })

  const invitation = invitationPour(isAuthenticated ? user : null, country)
  // Pas d'invitation vers la page où l'on est déjà (les tarifs sur /tarifs, la séance
  // sur l'accueil) : un bouton qui ne mène nulle part affaiblit tous les autres.
  const cible = invitation.lien.split("?")[0]
  const afficherInvitation = pathname !== cible

  const examens = ORDRE_EXAMENS.map((examen) => ({
    examen,
    cursus: cursusList
      .filter((c) => c.examen_display === examen)
      .sort((a, b) => (a.series?.code ?? "").localeCompare(b.series?.code ?? "", "fr")),
  })).filter((groupe) => groupe.cursus.length > 0)

  return (
    <footer className="mt-auto border-t border-border/80 bg-secondary/30">
      <div className="h-px w-full bg-gradient-to-r from-primary/0 via-gold/70 to-primary/0" />

      {/* Bande 1 : l'action qui correspond à celui qui lit. */}
      {afficherInvitation && (
        <div className="mx-auto max-w-5xl px-4 pt-10 sm:px-6">
          <div className="relative overflow-hidden rounded-3xl border border-border bg-gradient-to-br from-primary/[0.10] via-primary/[0.04] to-gold/[0.08] p-5 sm:p-7">
            <div
              aria-hidden
              className="absolute inset-0 opacity-[0.04]"
              style={{
                backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
                backgroundSize: "24px 24px",
              }}
            />
            <div className="relative flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-start gap-3">
                <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm shadow-primary/30">
                  <Sparkles className="size-5" />
                </span>
                <p className="font-display text-lg font-semibold leading-snug text-balance sm:text-xl">
                  {invitation.message}
                </p>
              </div>
              <div className="flex shrink-0 flex-col items-stretch gap-2 sm:items-end">
                <Link
                  to={invitation.lien}
                  className="inline-flex h-11 items-center justify-center gap-2 rounded-md bg-primary px-5 text-sm font-medium text-primary-foreground shadow-sm transition-colors hover:bg-primary/90"
                >
                  {invitation.bouton}
                  <ArrowRight className="size-4" />
                </Link>
                {invitation.secondaire && (
                  <Link
                    to={invitation.secondaire.lien}
                    className="text-center text-sm text-muted-foreground underline-offset-4 hover:text-primary hover:underline"
                  >
                    {invitation.secondaire.label}
                  </Link>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Bande 2 : la marque et la navigation. */}
      <div className="mx-auto grid max-w-5xl gap-x-6 px-4 py-10 sm:grid-cols-3 sm:gap-y-10 sm:px-6 sm:py-12 lg:grid-cols-[1.3fr_1fr_1.2fr_1fr]">
        <div className="mb-6 sm:col-span-3 sm:mb-0 lg:col-span-1">
          <Link to={catalogueHomePath(country)} className="flex items-baseline gap-2">
            <span className="font-display text-xl font-semibold tracking-tight text-primary">{SITE_NAME}</span>
            <span className="font-display text-xs italic text-muted-foreground">réussis ton examen</span>
          </Link>
          <p className="mt-3 max-w-xs text-sm leading-relaxed text-muted-foreground">
            Chaque jour, ce qu'il faut réviser pour ton examen - et on retient ce que tu rates.
          </p>
          {stats && (
            <div className="mt-5 flex gap-6">
              <div>
                <p className="font-display text-2xl font-semibold tabular-nums text-foreground">
                  {formatAmount(stats.corriges_disponibles)}
                </p>
                <p className="text-xs text-muted-foreground">épreuves corrigées</p>
              </div>
              <div>
                <p className="font-display text-2xl font-semibold tabular-nums text-foreground">
                  {formatAmount(stats.cours_disponibles)}
                </p>
                <p className="text-xs text-muted-foreground">cours et fiches</p>
              </div>
            </div>
          )}
        </div>

        <Colonne titre="Réviser">
          <Lien to={epreuvesListPath(country)}>Épreuves corrigées</Lien>
          <Lien to={coursListPath(country)}>Cours</Lien>
          <Lien to={themesFrequentsPath(country)} vedette>
            Thèmes qui tombent
            <span className="rounded-full bg-gold/20 px-1.5 py-px text-[0.65rem] font-semibold uppercase tracking-wide text-gold-text">
              Top
            </span>
          </Lien>
          <Lien to="/quiz">Quiz</Lien>
          <Lien to="/fiches">Fiches</Lien>
          <Lien to={`${epreuvesListPath(country)}?origine=INEDITE`}>Épreuves inédites</Lien>
        </Colonne>

        <Colonne titre="Par examen">
          {examens.length === 0 ? (
            <Lien to={epreuvesListPath(country)}>Tous les examens</Lien>
          ) : (
            examens.map(({ examen, cursus }) => (
              <div key={examen} className="text-sm">
                {cursus.length === 1 && !cursus[0].series ? (
                  <Lien to={`${epreuvesListPath(country)}?cursus=${cursus[0].id}`}>{examen}</Lien>
                ) : (
                  <p className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
                    <span className="text-foreground/80">{examen}</span>
                    {cursus.map((c) => (
                      <Link
                        key={c.id}
                        to={`${epreuvesListPath(country)}?cursus=${c.id}`}
                        className="rounded-md px-1 text-muted-foreground ring-1 ring-border transition-colors hover:text-primary hover:ring-primary/40"
                        aria-label={libelleCursus(c)}
                      >
                        {c.series?.code ?? examen}
                      </Link>
                    ))}
                  </p>
                )}
              </div>
            ))
          )}
        </Colonne>

        <Colonne titre="Aide">
          <Lien to="/tarifs">Tarifs</Lien>
          <Lien to="/a-propos">À propos</Lien>
          <a
            href={CONTACT_WHATSAPP_URL}
            target="_blank"
            rel="noopener noreferrer"
            title="Écris-nous sur WhatsApp"
            className="inline-flex w-fit items-center gap-2 whitespace-nowrap rounded-full bg-[#25D366]/10 px-3 py-1.5 text-sm font-medium text-[#128C7E] ring-1 ring-[#25D366]/30 transition-colors hover:bg-[#25D366]/20 dark:text-[#25D366]"
          >
            <MessageCircle className="size-4" />
            Écris-nous
          </a>
          <a
            href={`mailto:${CONTACT_EMAIL}`}
            className="w-fit text-sm text-muted-foreground transition-colors hover:text-primary"
          >
            {CONTACT_EMAIL}
          </a>
        </Colonne>
      </div>

      {/* Bande 3 : confiance et mentions. Pastilles en texte aux couleurs des opérateurs,
          pas leurs logos (droits d'usage non établis). */}
      <div className="border-t border-border/80">
        <div className="mx-auto flex max-w-5xl flex-col items-center gap-4 px-4 py-5 text-xs text-muted-foreground sm:flex-row sm:justify-between sm:px-6">
          <div className="flex flex-wrap items-center justify-center gap-2">
            <span className="flex items-center gap-1.5 font-medium text-foreground/70">
              <ShieldCheck className="size-3.5 shrink-0 text-primary" />
              Paiement sécurisé
            </span>
            <span className="rounded-md bg-[#FF7900] px-2 py-0.5 text-[0.7rem] font-bold text-white">Orange Money</span>
            <span className="rounded-md bg-[#FFCB05] px-2 py-0.5 text-[0.7rem] font-bold text-[#1a1a1a]">MTN MoMo</span>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1">
            <span>© {year} {SITE_NAME}</span>
            <span aria-hidden>·</span>
            <Link to="/cgu" className="hover:text-primary">Conditions d'utilisation</Link>
            <span aria-hidden>·</span>
            <Link to="/confidentialite" className="hover:text-primary">Confidentialité</Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
