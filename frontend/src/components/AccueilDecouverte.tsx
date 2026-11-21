import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, ChevronDown, ListChecks, Sparkles, Target, TrendingUp } from "lucide-react"

import { getPlanDuJour, listQuizEssais } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { Cursus, QuizEssai } from "@/api/types"
import { SelecteurExamen } from "@/components/ChoixExamen"
import { CompteAReboursBadge } from "@/components/CompteAReboursBadge"
import { LigneJour } from "@/components/LigneJour"
import { seanceSuivante } from "@/components/PremiereSeance"
import { ReprendreQuiz } from "@/components/ReprendreQuiz"
import { SeanceCompleteVerrouillee } from "@/components/SeanceDuJour"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/context/AuthContext"
import { trackEvent } from "@/lib/analytics"
import { epreuvesListPath, themesFrequentsPath } from "@/lib/countryPath"
import { libelleCursus } from "@/lib/cursus"
import { t, tn, useI18n } from "@/lib/i18n"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { FRAICHEUR_ACCUEIL_MS } from "@/lib/quizEnCours"
import { lancerQuizGratuit } from "@/lib/quizGratuit"
import { seanceAffichable } from "@/lib/seance"
import { seancesJouees } from "@/lib/seancesGratuites"
import { subjectIcon } from "@/lib/subjectIcon"
import { capitaliserTheme, cn } from "@/lib/utils"

/**
 * « Aujourd'hui » pour un élève CONNECTÉ SANS ABONNEMENT : sa page, et plus la vitrine du visiteur avec une porte
 * fermée posée dessus (audit des accueils, 2026-11-21).
 *
 * Il a donné le signal le plus fort avant de payer, un compte et un examen, et il recevait l'argumentaire écrit pour
 * un inconnu. Sa séance du jour, verrouillée, ouvrait la page ; ce qu'il pouvait faire gratuitement était au troisième
 * écran, sous un autre thème. Ici, UNE carte, dans l'ordre de ce qu'il peut faire :
 *
 *   1. qui il est et où il en est : « Bonjour », son examen (qu'il peut changer), le compte à rebours ;
 *   2. sa séance gratuite : le thème gratuit suivant de son examen (voir PremiereSeance.seanceSuivante), lancé en un
 *      toucher. C'est le bouton principal de la page ;
 *   3. ses points, son niveau et sa série (LigneJour) : un quiz gratuit joué par un compte les crédite déjà, rien ne
 *      le lui montrait ;
 *   4. la séance complète du jour, fermée, en version courte : ce que l'abonnement ajoute, le prix, un bouton (voir
 *      SeanceCompleteVerrouillee).
 *
 * Rien de plus n'est offert qu'avant : ce sont les mêmes séances gratuites, une par matière. Leur avancement est gardé
 * sur l'appareil (lib/seancesGratuites), comme pour le visiteur.
 *
 * Les preuves (extrait de corrigé, épreuve inédite de son examen) et le rappel du prix restent dessous, rendus par
 * CataloguePage ; le reste de la vitrine (promesse, « Comment ça marche », parents, questions fréquentes) ne lui est
 * plus montré.
 */
export function AccueilDecouverte({ country }: { country: string }) {
  useI18n()
  const navigate = useNavigate()
  const { user } = useAuth()
  const cursus = user?.cursus_prepare ?? null
  const prenom = (user?.profil_actif?.prenom || user?.pseudo || user?.full_name || "").trim().split(/\s+/)[0]

  // Le plan du jour porte tout ce qui lui est personnel : la séance complète (fermée), ses points, sa série.
  const { data: plan } = useQuery({
    queryKey: ["plan-du-jour"],
    queryFn: ({ signal }) => getPlanDuJour(signal),
  })
  // Même clé de cache que /quiz et que la carte du visiteur : la liste n'est demandée qu'une fois.
  const { data: essais, isPending: essaisEnAttente } = useQuery({
    queryKey: ["quiz", "essais"],
    queryFn: ({ signal }) => listQuizEssais(signal),
    staleTime: 5 * 60_000,
    enabled: cursus !== null,
  })
  const [lancement, setLancement] = useState(false)
  const [erreur, setErreur] = useState("")
  // Lu une fois au montage : la séance se joue sur une autre page, la carte est remontée au retour sur l'accueil.
  const [jouees] = useState(seancesJouees)

  if (!cursus) return null
  const { essai, faites, total } = essais ? seanceSuivante(essais, cursus.id, jouees) : { essai: null, faites: 0, total: 0 }

  async function commencer(seance: QuizEssai) {
    if (lancement) return
    setLancement(true)
    setErreur("")
    trackEvent("accueil_bouton_clic", { cible: "seance_gratuite" })
    try {
      navigate(await lancerQuizGratuit({
        cursus: seance.cursus, subject: seance.subject, theme: seance.theme, connecte: true, source: "accueil_seance",
      }))
    } catch (err) {
      setErreur(err instanceof ApiError ? err.message : t("essais.erreur"))
      setLancement(false)
    }
  }

  const seanceComplete = plan && seanceAffichable(plan) && plan.seance?.verrouillee ? plan : null

  return (
    <>
    {/* Le titre de la page, pour les lecteurs d'écran : la salutation visible contient un sélecteur d'examen. */}
    <h1 className="sr-only">{t("seance.aujourdhui")}</h1>
    {/* Un quiz commencé passe avant d'en lancer un autre, comme chez l'abonné (voir AccueilEleve) : sans cette ligne,
        une séance gratuite quittée à la question 3 ne se retrouvait que par l'historique. */}
    <ReprendreQuiz enveloppe fraicheurMs={FRAICHEUR_ACCUEIL_MS} />
    <section className="mx-auto max-w-5xl px-4 pt-5 sm:px-6 sm:pt-6" aria-label={t("seance.aujourdhui")}>
      {/* `overflow-clip` et non `overflow-hidden` : une carte rognée ainsi ne défile pas sur elle-même. */}
      <div className="animate-fade-up relative overflow-clip rounded-3xl border border-primary/20 bg-card shadow-xl shadow-primary/[0.07]">
        <Bande prenom={prenom} cursus={cursus} />

        <div className="p-5 sm:p-8">
          {essaisEnAttente ? (
            <Squelette />
          ) : essai ? (
            <SeanceGratuite
              essai={essai}
              cursus={cursus}
              rang={faites + 1}
              total={total}
              lancement={lancement}
              onCommencer={() => commencer(essai)}
            />
          ) : total > 0 ? (
            <TourFait cursus={cursus} total={total} />
          ) : (
            <>
              <p className="text-sm text-muted-foreground">{t("premiere.aucune", { cursus: libelleCursus(cursus) })}</p>
              <Button size="lg" asChild className="mt-4 h-12 rounded-full px-7 text-base">
                <Link to={`${epreuvesListPath(country)}?gratuit=true`}>
                  {t("accueil.cta_corrige_gratuit")}
                  <ArrowRight className="size-4" />
                </Link>
              </Button>
            </>
          )}
          {erreur && (
            <p role="alert" className="mt-3 text-sm text-destructive">
              {erreur}
            </p>
          )}

          {/* Ses points, son niveau, sa série : sous le bouton, comme chez l'abonné, pour ne pas le repousser sous le pli. */}
          {plan?.xp && plan.serie && (
            <div className="mt-6 [&>div]:mb-0">
              <LigneJour etat={plan.xp} serie={plan.serie} />
            </div>
          )}
        </div>

        {seanceComplete && (
          <div className="border-t border-border/70 bg-muted/30 p-5 sm:p-8">
            <SeanceCompleteVerrouillee plan={seanceComplete} />
          </div>
        )}
      </div>

      {/* Les deux autres portes gratuites, sous la carte : lire d'abord, ou voir ce qui tombe. */}
      <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 px-1 text-sm">
        <Link
          to={`${epreuvesListPath(country)}?gratuit=true`}
          onClick={() => trackEvent("accueil_bouton_clic", { cible: "corrige_gratuit" })}
          className="flex min-h-9 items-center gap-1.5 text-muted-foreground transition-colors hover:text-primary"
        >
          {t("accueil.cta_corrige_gratuit")}
          <ArrowRight className="size-3.5" aria-hidden="true" />
        </Link>
        <Link
          to={themesFrequentsPath(country)}
          onClick={() => trackEvent("accueil_bouton_clic", { cible: "themes" })}
          className="flex min-h-9 items-center gap-1.5 text-muted-foreground transition-colors hover:text-primary"
        >
          <TrendingUp className="size-3.5 text-primary" aria-hidden="true" />
          {t("accueil.themes_frequents")}
        </Link>
      </div>
    </section>
    </>
  )
}

/** « Bonjour Awa · BAC C » et le compte à rebours : la ligne de tête de la carte, comme chez l'abonné. */
function Bande({ prenom, cursus }: { prenom: string; cursus: Cursus }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1 border-b border-primary/10 bg-primary/[0.06] px-5 py-2.5 sm:px-8">
      <p className="flex flex-wrap items-center gap-x-1.5 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
        {prenom ? t("tete.bonjour_prenom", { prenom }) : t("tete.bonjour")}
        <span aria-hidden="true">·</span>
        {/* Il n'a rien payé : son examen se change d'ici, comme dans l'en-tête. */}
        <SelecteurExamen>
          <button
            type="button"
            aria-label={t("choix.pastille_aria", { cursus: libelleCursus(cursus) })}
            className="inline-flex min-h-9 items-center gap-1 uppercase tracking-[0.18em] transition-colors hover:text-primary/80"
          >
            {libelleCursus(cursus)}
            <ChevronDown className="size-3.5 opacity-70" aria-hidden="true" />
          </button>
        </SelecteurExamen>
      </p>
      {/* Masqué dès `md` : l'en-tête de la page porte déjà le compte à rebours à partir de cette largeur (voir Header). */}
      <CompteAReboursBadge variant="pilule" examenACote className="md:hidden" />
    </div>
  )
}

function SeanceGratuite({
  essai, cursus, rang, total, lancement, onCommencer,
}: {
  essai: QuizEssai
  cursus: Cursus
  /** Place de cette séance parmi les séances gratuites de l'examen : 1 tant qu'aucune n'a été jouée sur cet appareil. */
  rang: number
  total: number
  lancement: boolean
  onCommencer: () => void
}) {
  const Icone = subjectIcon(essai.subject_code)
  const nb = essai.nb_epreuves ?? 0
  const nbMatiere = essai.nb_epreuves_matiere ?? 0
  // Une fréquence d'une seule épreuve ne prouve rien : on ne l'affiche qu'à partir de deux.
  const frequence = nb >= 2 && nbMatiere >= nb ? tn("seance.frequence", nb, { total: nbMatiere }) : null

  return (
    <>
      <h2 className="font-display">
        <span className="flex items-center gap-2 font-sans text-xs font-semibold uppercase tracking-[0.18em] text-primary">
          <Sparkles className="size-3.5" aria-hidden="true" />
          {total > 1 ? t("decouverte.gratuite_rang", { n: rang, total }) : t("decouverte.gratuite")}
        </span>
        <span className="mt-2 block text-3xl font-semibold leading-[1.1] tracking-tight text-balance sm:text-4xl">
          {capitaliserTheme(essai.theme_name)}
        </span>
      </h2>
      <ul className="mt-4 flex flex-wrap gap-2 text-sm">
        <li className={cn("inline-flex items-center gap-1.5 rounded-full px-3 py-1 font-semibold", couleurMatiere(essai.subject_code).puce)}>
          <Icone className="size-3.5" aria-hidden="true" />
          {essai.subject_label}
        </li>
        <li className="inline-flex items-center gap-1.5 rounded-full border border-border px-3 py-1 text-xs font-medium text-muted-foreground">
          <ListChecks className="size-3.5" aria-hidden="true" />
          {tn("quiz.n_questions", essai.nb_questions)}
        </li>
        {frequence && (
          <li className="inline-flex items-center gap-1.5 rounded-full bg-gold/15 px-3 py-1 text-xs font-medium text-gold-foreground dark:text-gold-text">
            <Target className="size-3.5" aria-hidden="true" />
            {frequence}
          </li>
        )}
      </ul>
      <div className="mt-6 flex flex-wrap items-center gap-x-5 gap-y-3">
        <Button
          size="lg"
          data-guide="seance-gratuite"
          className="group h-12 rounded-full px-7 text-base shadow-lg shadow-primary/25 transition-all hover:-translate-y-0.5 hover:shadow-xl hover:shadow-primary/30"
          disabled={lancement}
          onClick={onCommencer}
        >
          {lancement ? t("quiz.preparation") : t("premiere.commencer")}
          {!lancement && <ArrowRight className="size-4 transition-transform group-hover:translate-x-1" />}
        </Button>
        <Link
          to={`/quiz?cursus=${cursus.id}`}
          onClick={() => trackEvent("accueil_bouton_clic", { cible: "quiz" })}
          className="flex min-h-9 items-center text-sm text-muted-foreground underline-offset-4 transition-colors hover:text-primary hover:underline"
        >
          {t("premiere.autre_matiere")}
        </Link>
      </div>
    </>
  )
}

/** Toutes les séances gratuites de l'examen sont jouées : on le dit, et on laisse rejouer ce qui est gratuit. */
function TourFait({ cursus, total }: { cursus: Cursus; total: number }) {
  return (
    <>
      <h2 className="font-display">
        <span className="flex items-center gap-2 font-sans text-xs font-semibold uppercase tracking-[0.18em] text-primary">
          <Sparkles className="size-3.5" aria-hidden="true" />
          {t("premiere.tour_etiquette")}
        </span>
        <span className="mt-2 block text-2xl font-semibold leading-tight tracking-tight sm:text-3xl">
          {tn("premiere.tour_titre", total)}
        </span>
      </h2>
      <p className="mt-3 max-w-2xl text-sm text-muted-foreground">{t("premiere.tour_texte")}</p>
      <Link
        to={`/quiz?cursus=${cursus.id}`}
        data-guide="seance-gratuite"
        onClick={() => trackEvent("accueil_bouton_clic", { cible: "quiz" })}
        className="mt-4 inline-flex min-h-11 items-center gap-1.5 text-sm font-medium text-primary underline-offset-4 hover:underline"
      >
        {t("premiere.tour_refaire")}
        <ArrowRight className="size-4" aria-hidden="true" />
      </Link>
    </>
  )
}

function Squelette() {
  return (
    <div aria-hidden="true" className="flex animate-pulse flex-col">
      <span className="h-3 w-40 rounded bg-muted" />
      <span className="mt-3 h-9 w-3/4 rounded bg-muted" />
      <span className="mt-4 h-7 w-1/2 rounded-full bg-muted" />
      <span className="mt-6 h-12 w-48 rounded-full bg-muted" />
    </div>
  )
}
