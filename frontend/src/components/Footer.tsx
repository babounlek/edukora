import type { ReactNode } from "react"
import { Link, useLocation } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, ChevronDown, Mail, MessageCircle } from "lucide-react"

import { listExamens } from "@/api/endpoints"
import type { Cursus, PlanDuJour, User } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { ouvrirCentre } from "@/lib/guides/etat"
import { useAbonneActif } from "@/lib/abonneActif"
import { useCountry } from "@/context/CountryContext"
import { CONTACT_EMAIL, CONTACT_WHATSAPP_AFFICHAGE, CONTACT_WHATSAPP_URL, EDITEUR_NOM } from "@/lib/site"
import { catalogueHomePath, coursListPath, epreuvesListPath, examenPath, themesFrequentsPath } from "@/lib/countryPath"
import { cn } from "@/lib/utils"
import { Logo } from "@/components/Logo"
import { ACCUEIL_PAYS_RE } from "@/components/CoquilleAccueil"
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
 * Une colonne de liens. Sur un téléphone, les colonnes étaient autant de tiroirs fermés : le pied de page ne
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
  const entete = "text-sm font-semibold text-foreground"
  if (!repliable) {
    return (
      <nav aria-label={t("ft.aria_nav", { titre: titre.toLowerCase() })} className={cn("flex flex-col gap-1", className)}>
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
      <nav aria-label={t("ft.aria_nav", { titre: titre.toLowerCase() })} className={cn("hidden flex-col gap-1 sm:flex", className)}>
        <span className={cn(entete, "mb-1")}>{titre}</span>
        {children}
      </nav>
    </>
  )
}

function Lien({ to, children }: { to: string; children: ReactNode }) {
  return (
    <Link
      to={to}
      // min-h-8 : une cible tactile de 32 px au moins (les liens du pied de page en faisaient ~20, audit UX-08).
      className="inline-flex min-h-8 w-fit items-center text-sm text-muted-foreground transition-colors hover:text-primary"
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
    !vitrineAvecSonAppel &&
    // Un abonné actif a sa séance sur son accueil, dans le menu et dans la barre d'onglets : le bloc du bas de page le
    // poussait hors de ce qu'il était en train de faire (Mes notes, lecture). Il reste pour le visiteur et l'inscrit sans
    // abonnement, dont c'est l'un des rares appels à s'inscrire ou à voir les prix.
    !user?.a_un_abonnement_actif

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
    // Sobre, sans décor (2026-11-25) : le filet doré, la carte à dégradé et à pois, les pastilles et les cases des séries
    // attiraient tous l'œil en même temps. Pas de sélecteur de langue ici : il est dans la barre du haut et dans son menu.
    <footer className="mt-auto border-t border-border bg-muted/60">
      {/* Bande 1 : l'action qui correspond à celui qui lit. */}
      {afficherInvitation && (
        <div className="mx-auto max-w-5xl px-4 sm:px-6">
          <div className="flex flex-col gap-4 border-b border-border/80 py-6 sm:flex-row sm:items-center sm:justify-between sm:gap-8">
            <p className="text-base font-medium leading-snug text-balance text-foreground">{invitation.message}</p>
            <div className="flex shrink-0 flex-col items-stretch gap-2 sm:flex-row-reverse sm:items-center sm:gap-5">
              <Link
                to={invitation.lien}
                className="inline-flex h-11 items-center justify-center gap-2 rounded-md bg-primary px-5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
              >
                {invitation.bouton}
                <ArrowRight className="size-4" aria-hidden="true" />
              </Link>
              {invitation.secondaire && (
                <Link
                  to={invitation.secondaire.lien}
                  className="inline-flex min-h-9 items-center justify-center text-sm text-muted-foreground underline-offset-4 hover:text-primary hover:underline"
                >
                  {invitation.secondaire.label}
                </Link>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Bande 2 : la marque et la navigation. */}
      {/* Sur un téléphone : la marque sur toute la largeur, puis « Réviser » à gauche, « EduKora » à droite, et les
          examens en tiroir dessous. À partir de `sm`, la marque au-dessus de trois colonnes ; à partir de `lg`, la
          marque en première colonne. */}
      <div className="mx-auto grid max-w-5xl grid-cols-2 gap-x-6 gap-y-8 px-4 py-10 sm:grid-cols-3 sm:gap-x-8 sm:px-6 lg:grid-cols-[1.5fr_1fr_1.2fr_1fr]">
        <div className="col-span-2 sm:col-span-3 lg:col-span-1">
          <Link to={catalogueHomePath(country)} className="inline-flex">
            <Logo variante="horizontal" className="h-10" />
          </Link>
          {/* Qui édite le site, où, et comment lui écrire : c'est ici qu'un parent le cherche. Le numéro et l'adresse
              sont écrits en clair, pas cachés derrière « Écris-nous ». */}
          <address className="mt-3 flex flex-col items-start text-sm not-italic text-muted-foreground">
            <span>{t("confiance.editeur_titre", { editeur: EDITEUR_NOM })}</span>
            <span>{t("ab.qui_lieu")}</span>
            <a
              href={CONTACT_WHATSAPP_URL}
              target="_blank"
              rel="noopener noreferrer"
              title={t("ft.whatsapp_titre")}
              className="mt-2 inline-flex min-h-9 items-center gap-2 whitespace-nowrap transition-colors hover:text-primary"
            >
              <MessageCircle className="size-4 shrink-0" aria-hidden="true" />
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

        <Colonne titre={t("ft.col_reviser")}>
          <Lien to={epreuvesListPath(country)}>{t("ft.epreuves")}</Lien>
          <Lien to={coursListPath(country)}>{t("ft.cours")}</Lien>
          <Lien to={themesFrequentsPath(country)}>{t("ft.themes")}</Lien>
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
                  // Les séries : du texte, sans case, mais avec la place d'un doigt (36 px sur un téléphone, 32 px au-delà).
                  <p className="flex flex-wrap items-center">
                    <span className="w-full text-foreground/80">{examen}</span>
                    {cursus.map((c) => (
                      <Link
                        key={c.id}
                        to={lienExamen(c)}
                        className="inline-flex min-h-9 min-w-9 items-center text-muted-foreground underline-offset-4 transition-colors hover:text-primary hover:underline sm:min-h-8 sm:min-w-8"
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
          <Lien to="/aide">{t("ft.aide_centre")}</Lien>
          <button
            type="button"
            onClick={ouvrirCentre}
            className="inline-flex min-h-8 w-fit items-center text-left text-sm text-muted-foreground transition-colors hover:text-primary"
          >
            {t("guide.aide.footer")}
          </button>
        </Colonne>
      </div>

      {/* Bande 3 : mentions et moyens de paiement, en texte (droits d'usage des logos des opérateurs non établis). */}
      <div className="mx-auto max-w-5xl px-4 sm:px-6">
        <div className="flex flex-col items-center gap-2 border-t border-border/80 py-4 text-center text-xs text-muted-foreground lg:flex-row lg:justify-between lg:text-left">
          <div className="flex flex-wrap items-center justify-center gap-x-3">
            {/* Sur un téléphone, le copyright prend sa ligne : sinon un « · » restait seul en bout de ligne. */}
            <span className="max-sm:w-full">© {year} {EDITEUR_NOM}</span>
            <span aria-hidden className="max-sm:hidden">·</span>
            <Link to="/cgu" className="inline-flex min-h-8 items-center hover:text-primary">{t("ft.cgu")}</Link>
            <span aria-hidden>·</span>
            <Link to="/confidentialite" className="inline-flex min-h-8 items-center hover:text-primary">{t("ft.confidentialite")}</Link>
          </div>
          <span>{t("ft.paiement_securise")}</span>
        </div>
      </div>
    </footer>
  )
}
