import type { ReactNode } from "react"
import { Link, useLocation } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, ArrowUp, ChevronDown, Mail, MessageCircle, ShieldCheck, Sparkles } from "lucide-react"

import { listExamens } from "@/api/endpoints"
import type { Cursus, PlanDuJour, User } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { ouvrirCentre } from "@/lib/guides/etat"
import { useAbonneActif } from "@/lib/abonneActif"
import { useCountry } from "@/context/CountryContext"
import { CONTACT_EMAIL, CONTACT_WHATSAPP_AFFICHAGE, CONTACT_WHATSAPP_URL, EDITEUR_NOM, SITE_NAME } from "@/lib/site"
import { catalogueHomePath, coursListPath, epreuvesListPath, examenPath, themesFrequentsPath } from "@/lib/countryPath"
import { cn } from "@/lib/utils"
import { Logo } from "@/components/Logo"
import { PastilleOperateur } from "@/components/PastilleOperateur"
import { ACCUEIL_PAYS_RE } from "@/components/CoquilleAccueil"
import { SelecteurLangue } from "@/components/SelecteurLangue"
import { useCursusListe } from "@/lib/cursusLangue"
import { langueDeListe } from "@/lib/discipline"
import { t, tn, useI18n } from "@/lib/i18n"


// Ordre de lecture d'un élève : du premier examen au dernier.
const ORDRE_EXAMENS = ["BEPC", "Probatoire", "BAC"]
const ORDRE_EXAMENS_EN = ["GCE O Level", "GCE A Level"]

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
    return tn("ft.mois", mois, { session: cr.session_label })
  }
  return tn("ft.jours", cr.jours_restants, { session: cr.session_label })
}

/**
 * L'appel à l'action du bas de page, selon qui lit : on ne dit pas la même chose à un
 * visiteur, à un élève inscrit mais pas abonné, et à un abonné qui a sa séance à faire.
 * Aucune requête de plus : tout vient de l'utilisateur déjà chargé (compte à rebours,
 * cursus déclaré, abonnement actif).
 */
function invitationPour(user: User | null, country: string, seanceFaite = false): Invitation {
  if (!user) {
    return {
      message: (
        <>
          {t("ft.anon_debut")}{" "}
          <span className="text-primary">{t("ft.anon_fin")}</span>
        </>
      ),
      bouton: t("ft.creer_compte"),
      lien: "/connexion",
      secondaire: { label: t("ft.voir_prix"), lien: "/tarifs" },
    }
  }
  const compteARebours = phraseCompteARebours(user)
  if (!user.a_un_abonnement_actif) {
    const cursus = user.cursus_prepare ? libelleCursus(user.cursus_prepare) : null
    return {
      message: (
        <>
          {compteARebours ? `${compteARebours}. ` : ""}
          {cursus ? t("ft.debloque_cursus", { cursus }) : t("ft.debloque")}{" "}
          <span className="text-primary">{t("ft.debloque_fin")}</span>
        </>
      ),
      bouton: t("ft.voir_prix"),
      lien: "/tarifs",
    }
  }
  if (seanceFaite) {
    // « Ta séance est prête » après une séance faite : le pied de page disait le contraire de l'accueil.
    return {
      message: (
        <>
          {compteARebours ? `${compteARebours} · ` : ""}
          <span className="text-primary">{t("ft.seance_faite")}</span>
        </>
      ),
      bouton: t("ft.encore_un_quiz"),
      lien: "/quiz",
    }
  }
  return {
    message: (
      <>
        {compteARebours ? `${compteARebours} · ` : ""}
        <span className="text-primary">{t(compteARebours ? "ft.seance_prete_suite" : "ft.seance_prete")}</span>
      </>
    ),
    bouton: t("ft.faire_seance"),
    lien: catalogueHomePath(country),
  }
}

/**
 * Une colonne de liens. Sur un téléphone, les quatre colonnes étaient quatre tiroirs fermés : le pied de page ne
 * montrait qu'un logo et quatre titres, et « À propos » ou « Centre d'aide » étaient à deux touchers (revue du pied de
 * page, 2026-11-23). Les colonnes courtes sont maintenant ouvertes, sur deux colonnes ; seule la liste des examens, la
 * plus longue, reste `repliable` sous `sm`. Pour elle, deux rendus plutôt qu'un <details> forcé ouvert : l'état
 * ouvert d'un <details> ne se pilote pas en CSS.
 */
function Colonne({ titre, children, repliable = false, className }: {
  titre: string
  children: ReactNode
  repliable?: boolean
  /** Placement dans la grille du pied de page. */
  className?: string
}) {
  useI18n()
  const entete = "text-xs font-semibold uppercase tracking-[0.14em] text-foreground/70"
  if (!repliable) {
    return (
      <nav aria-label={t("ft.aria_nav", { titre: titre.toLowerCase() })} className={cn("flex flex-col gap-2 sm:gap-2.5", className)}>
        <span className={cn(entete, "mb-1")}>{titre}</span>
        {children}
      </nav>
    )
  }
  return (
    <>
      <details className={cn("group border-y border-border/70 sm:hidden", className)}>
        <summary className={cn(entete, "flex cursor-pointer list-none items-center justify-between py-3.5")}>
          {titre}
          <ChevronDown className="size-4 text-muted-foreground transition-transform group-open:rotate-180" />
        </summary>
        <nav aria-label={t("ft.aria_nav", { titre: titre.toLowerCase() })} className="flex flex-col gap-3 pb-4">
          {children}
        </nav>
      </details>
      <nav aria-label={t("ft.aria_nav", { titre: titre.toLowerCase() })} className={cn("hidden flex-col gap-2.5 sm:flex", className)}>
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
        // min-h-8 : une cible tactile de 32 px au moins (les liens du pied de page en faisaient ~20, audit UX-08).
        "inline-flex min-h-8 w-fit items-center gap-1.5 text-sm transition-colors hover:text-primary",
        vedette ? "font-medium text-foreground" : "text-muted-foreground",
      )}
    >
      {children}
    </Link>
  )
}

const PAGES_SANS_PIED = /^\/quiz\/(session|essai)/
// Pages où le bandeau « crée ton compte / voir les prix » parlerait d'autre chose que de la page : la candidature et l'espace
// des revendeurs ont leur propre appel à l'action ; sur /tarifs, il renvoyait vers les prix depuis la page des prix, et le
// bouton « Continuer » du récapitulatif mène déjà à la création du compte (le chemin du routeur est toujours en français,
// même sous /en).
const PAGES_SANS_INVITATION = /^\/(devenir-revendeur|espace-revendeur)|^\/tarifs\/?$/

function remonter() {
  const reduit = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches
  window.scrollTo({ top: 0, behavior: reduit ? "auto" : "smooth" })
}

export function Footer() {
  useI18n()
  const year = new Date().getFullYear()
  const { country } = useCountry()
  const { user, isAuthenticated } = useAuth()
  const { pathname } = useLocation()

  // Le pied de page ne porte plus les chiffres de la plateforme : l'accueil les dit en grand (voir BandePreuves), et ici
  // le même total portait un autre nom (« cours et fiches » contre « cours structurés »). À leur place, l'éditeur et
  // ses moyens de contact (revue du pied de page, 2026-11-23).
  const langueStats = langueDeListe("", false)
  const abonne = useAbonneActif()
  // Même clé que /epreuves et /themes-frequents : déjà en cache la plupart du temps.
  // Examens de la langue de l'interface (voir lib/cursusLangue) : BEPC, Probatoire, BAC en français, GCE en anglais.
  const { data: cursusList } = useCursusListe(country, { langue: langueStats })

  // Les examens qui ont une page d'atterrissage (/cm/examens/bepc) : le pied de page y mène, ce qui donne aux moteurs
  // un lien depuis chaque page du site. Un examen qui n'en a pas (aucune épreuve publiée) garde le filtre de la liste.
  const { data: pagesExamen } = useQuery({
    queryKey: ["examens", country],
    queryFn: () => listExamens(country as string),
    enabled: Boolean(country),
    staleTime: 10 * 60 * 1000,
  })
  function lienExamen(c: Cursus): string {
    const page = pagesExamen?.find((e) => e.cursus_id === c.id)
    return page ? examenPath(country as string, page.slug) : `${epreuvesListPath(country)}?cursus=${c.id}`
  }

  // Le plan du jour est lu dans le cache seulement (aucune requête de plus) : il y est dès que l'élève a vu son accueil.
  const { data: plan } = useQuery<PlanDuJour | null>({ queryKey: ["plan-du-jour"], queryFn: () => Promise.resolve(null), enabled: false })
  const invitation = invitationPour(isAuthenticated ? user : null, country, plan?.etat === "deja_fait_aujourdhui")
  // Pas d'invitation vers la page où l'on est déjà (les tarifs sur /tarifs, la séance
  // sur l'accueil) : un bouton qui ne mène nulle part affaiblit tous les autres.
  const cible = invitation.lien.split("?")[0]
  // /quiz porte déjà son propre appel principal pour qui n'a pas d'abonnement (voir QuizCompletVisiteur) :
  // le répéter dans le pied de page ferait deux boutons identiques à la suite.
  // Sur l'accueil d'un visiteur ou d'un élève sans abonnement, la vitrine se termine déjà par son appel (« Prêt à
  // commencer ? », avec les prix et « Créer mon compte », voir CataloguePage) : l'invitation d'ici le répétait juste
  // dessous (audit visuel de l'accueil, 2026-11-23). Un abonné, lui, a un autre accueil et garde la sienne.
  const vitrineAvecSonAppel = ACCUEIL_PAYS_RE.test(pathname) && !user?.a_un_abonnement_actif
  const afficherInvitation =
    pathname !== cible &&
    !(pathname === "/quiz" && !user?.a_un_abonnement_actif) &&
    !PAGES_SANS_INVITATION.test(pathname) &&
    !vitrineAvecSonAppel

  const examens = (langueStats === "en" ? ORDRE_EXAMENS_EN : ORDRE_EXAMENS).map((examen) => ({
    examen,
    cursus: cursusList
      // Un abonné ne se voit proposer que son examen (voir useAbonneActif).
      .filter((c) => c.examen_display === examen && (!abonne || c.id === user?.cursus_prepare?.id))
      .sort((a, b) => (a.series?.code ?? "").localeCompare(b.series?.code ?? "", "fr")),
  })).filter((groupe) => groupe.cursus.length > 0)

  // Pendant un quiz (séance ou essai) : ni pied de page ni invitation « Commencer ma séance » sous le bouton « Question suivante »
  // (test élève Gogo) - l'élève est déjà dans sa séance, et la page n'a plus à vendre quoi que ce soit.
  if (PAGES_SANS_PIED.test(pathname)) return null

  return (
    // Le ton des bandes de l'accueil (« Comment ça marche », le mot du fondateur) : son fond se confondait avec la page.
    <footer className="mt-auto border-t border-border bg-muted/60">
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
      {/* Sur un téléphone : la marque sur toute la largeur, puis « Réviser » à gauche, « EduKora » et « Aide » l'une
          sous l'autre à droite, et les examens en tiroir dessous. À partir de `sm`, quatre colonnes dans l'ordre du
          code ; à partir de `lg`, la marque en première colonne. */}
      <div className="mx-auto grid max-w-5xl grid-cols-2 gap-x-6 gap-y-8 px-4 py-12 sm:grid-cols-4 sm:gap-x-8 sm:gap-y-10 sm:px-6 sm:py-14 lg:grid-cols-[1.5fr_1fr_1.2fr_1fr_1fr]">
        <div className="col-span-2 sm:col-span-4 lg:col-span-1">
          <Link to={catalogueHomePath(country)} className="flex items-center gap-2.5">
            <Logo variante="horizontal" className="h-14" />
          </Link>
          {/* Qui édite le site, où, et comment lui écrire : c'est ici qu'un parent le cherche, et l'éditeur n'était
              nommé que dans la ligne du copyright. Le numéro et l'adresse sont écrits en clair, pas cachés derrière
              « Écris-nous ». */}
          <address className="mt-4 flex flex-col items-start gap-1 text-sm not-italic text-muted-foreground">
            <span className="font-medium text-foreground">{t("confiance.editeur_titre", { editeur: EDITEUR_NOM })}</span>
            <span>{t("ab.qui_lieu")}</span>
            <a
              href={CONTACT_WHATSAPP_URL}
              target="_blank"
              rel="noopener noreferrer"
              title={t("ft.whatsapp_titre")}
              className="mt-2 inline-flex min-h-9 items-center gap-2 whitespace-nowrap rounded-full bg-[#25D366]/10 px-3 font-medium text-[#128C7E] ring-1 ring-[#25D366]/30 transition-colors hover:bg-[#25D366]/20 dark:text-[#25D366]"
            >
              <MessageCircle className="size-4" aria-hidden="true" />
              WhatsApp {CONTACT_WHATSAPP_AFFICHAGE}
            </a>
            <a
              href={`mailto:${CONTACT_EMAIL}`}
              className="inline-flex min-h-9 items-center gap-2 transition-colors hover:text-primary"
            >
              <Mail className="size-4 shrink-0" aria-hidden="true" />
              {CONTACT_EMAIL}
            </a>
          </address>
        </div>

        <Colonne titre={t("ft.col_reviser")} className="max-sm:row-span-2">
          <Lien to={epreuvesListPath(country)}>{t("ft.epreuves")}</Lien>
          <Lien to={coursListPath(country)}>{t("ft.cours")}</Lien>
          <Lien to={themesFrequentsPath(country)} vedette>
            {t("ft.themes")}
            <span className="rounded-full bg-gold/20 px-1.5 py-px text-[0.65rem] font-semibold uppercase tracking-wide text-gold-text">
              {t("ft.top")}
            </span>
          </Lien>
          <Lien to="/quiz">{t("ft.quiz")}</Lien>
          <Lien to={`${epreuvesListPath(country)}?origine=INEDITE`}>{t("ft.inedites")}</Lien>
        </Colonne>

        <Colonne titre={t("ft.col_examen")} repliable className="max-sm:order-last max-sm:col-span-2">
          {examens.length === 0 ? (
            <Lien to={epreuvesListPath(country)}>{t("ft.tous_examens")}</Lien>
          ) : (
            examens.map(({ examen, cursus }) => (
              <div key={examen} className="text-sm">
                {cursus.length === 1 && !cursus[0].series ? (
                  <Lien to={lienExamen(cursus[0])}>{examen}</Lien>
                ) : (
                  // Les séries étaient des pastilles de 20 px, la moitié de ce qu'il faut pour un doigt : 36 px sur un
                  // téléphone, 32 px au-delà (la taille des autres liens du pied de page).
                  <p className="flex flex-wrap items-center gap-1.5 sm:gap-1">
                    <span className="w-full text-foreground/80 sm:mb-0.5">{examen}</span>
                    {cursus.map((c) => (
                      <Link
                        key={c.id}
                        to={lienExamen(c)}
                        className="inline-flex min-h-9 min-w-9 items-center justify-center rounded-md bg-card px-2 text-muted-foreground ring-1 ring-border transition-colors hover:text-primary hover:ring-primary/40 sm:min-h-8 sm:min-w-[1.875rem] sm:px-1"
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

        <Colonne titre={t("ft.col_edukora")}>
          <Lien to="/a-propos">{t("ft.a_propos")}</Lien>
          <Lien to="/tarifs">{t("ft.prix")}</Lien>
          <Lien to="/devenir-revendeur">{t("cand.lien_compte")}</Lien>
        </Colonne>

        <Colonne titre={t("ft.col_aide")}>
          <Lien to="/aide">{t("ft.aide_centre")}</Lien>
          <button
            type="button"
            onClick={ouvrirCentre}
            className="inline-flex min-h-8 w-fit items-center gap-1.5 text-left text-sm font-medium text-foreground transition-colors hover:text-primary"
          >
            {t("guide.aide.footer")}
          </button>
        </Colonne>
      </div>

      {/* Bande 3 : confiance et mentions. Pastilles en texte aux couleurs des opérateurs,
          pas leurs logos (droits d'usage non établis). */}
      <div className="border-t border-border/80">
        <div className="mx-auto flex max-w-5xl flex-col gap-4 px-4 py-5 text-xs text-muted-foreground sm:px-6">
          <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
            <div className="flex flex-wrap items-center justify-center gap-2">
              <span className="flex items-center gap-1.5 font-medium text-foreground/70">
                <ShieldCheck className="size-3.5 shrink-0 text-primary" />
                {t("ft.paiement_securise")}
              </span>
              <PastilleOperateur operateur="ORANGE">Orange Money</PastilleOperateur>
              <PastilleOperateur operateur="MTN">MTN MoMo</PastilleOperateur>
            </div>
            <div className="flex items-center gap-3">
              {/* Le sélecteur s'efface de lui-même une fois le profil abonné (voir SelecteurLangue). */}
              <SelecteurLangue />
              <button
                type="button"
                onClick={remonter}
                className="inline-flex h-9 items-center gap-1.5 rounded-md border border-border px-3 font-medium text-foreground/80 transition-colors hover:border-primary/40 hover:text-primary"
              >
                <ArrowUp className="size-3.5" aria-hidden="true" />
                {t("ft.haut")}
              </button>
            </div>
          </div>
          <div className="flex flex-col items-center gap-2 border-t border-border/60 pt-4 sm:flex-row sm:justify-between">
            <span>© {year} {SITE_NAME} - {EDITEUR_NOM}</span>
            <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1">
              <Link to="/cgu" className="inline-flex min-h-8 items-center hover:text-primary">{t("ft.cgu")}</Link>
              <span aria-hidden>·</span>
              <Link to="/confidentialite" className="inline-flex min-h-8 items-center hover:text-primary">{t("ft.confidentialite")}</Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}
