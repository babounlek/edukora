import { useState, type ReactNode } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, Check, ChevronDown, ListChecks, Target } from "lucide-react"

import { listQuizEssais } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { Cursus, QuizEssai } from "@/api/types"
import { SelecteurExamen } from "@/components/ChoixExamen"
import { CompteAReboursBadge } from "@/components/CompteAReboursBadge"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/context/AuthContext"
import { trackEvent } from "@/lib/analytics"
import { epreuvesListPath } from "@/lib/countryPath"
import { libelleCursus, trierCursus } from "@/lib/cursus"
import { useCursusPrepareDeclare } from "@/lib/cursusAccueil"
import { useCursusListe } from "@/lib/cursusLangue"
import { useDeclarerCursus } from "@/lib/declarerCursus"
import { langueDeListe } from "@/lib/discipline"
import { t, tn, useI18n } from "@/lib/i18n"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { lancerQuizGratuit } from "@/lib/quizGratuit"
import { cleSeance, scoresDesSeances, seancesJouees, type ScoreSeance } from "@/lib/seancesGratuites"
import { subjectIcon } from "@/lib/subjectIcon"
import { capitaliserTheme, cn } from "@/lib/utils"

/**
 * La séance offerte à un visiteur pour un examen : le thème gratuit de mathématiques quand il existe (la matière que
 * tous les examens partagent), sinon celui qui est tombé dans le plus d'épreuves officielles. Chaque essai est déjà
 * « le thème le plus fréquent de sa matière » (voir quiz.gratuits côté backend).
 */
export function choisirEssai(essais: QuizEssai[], cursusId: number): QuizEssai | null {
  return ordonnerEssais(essais, cursusId)[0] ?? null
}

/** Les séances gratuites d'un examen, dans l'ordre où la carte les propose : les mathématiques, puis du thème le plus tombé au moins tombé. */
function ordonnerEssais(essais: QuizEssai[], cursusId: number): QuizEssai[] {
  const maths = (e: QuizEssai) => Number(/MATH/.test(e.subject_code))
  return essais
    .filter((e) => e.cursus === cursusId)
    .sort((a, b) => maths(b) - maths(a) || (b.nb_epreuves ?? 0) - (a.nb_epreuves ?? 0) || a.subject_label.localeCompare(b.subject_label))
}

/**
 * Où en est ce visiteur dans les séances gratuites de son examen : la prochaine qu'il n'a pas encore jouée sur cet
 * appareil (voir lib/seancesGratuites), combien il en a fait, combien l'examen en offre. `essai` est null quand il a
 * fait le tour - ou quand l'examen n'en a aucune (`total` vaut alors 0).
 *
 * La carte répétait « Ta première séance » sur le même thème à chaque visite : un visiteur qui hésite plusieurs jours
 * retrouvait les mêmes questions, sous un titre qui promet « chaque jour, on te dit quoi réviser ». Rien de plus n'est
 * offert pour autant : ce sont les thèmes gratuits qui existent déjà, un par matière (voir quiz.gratuits).
 */
export function seanceSuivante(essais: QuizEssai[], cursusId: number, jouees: ReadonlySet<string>) {
  const ordonnes = ordonnerEssais(essais, cursusId)
  const restantes = ordonnes.filter((e) => !jouees.has(cleSeance(e.cursus, e.theme)))
  return { essai: restantes[0] ?? null, faites: ordonnes.length - restantes.length, total: ordonnes.length }
}

/**
 * La carte du hero de l'accueil visiteur (audit de l'accueil du 2026-11-15, R6 et R7). Le titre promet « chaque jour,
 * on te dit quoi réviser » : cette carte le fait tout de suite, à la place de la photo d'illustration.
 *
 *   - sans examen déclaré : elle pose la seule question dont dépend tout le reste (« Tu prépares quel examen ? ») ;
 *   - examen déclaré : elle montre une vraie première séance (thème, matière, fréquence aux épreuves officielles,
 *     compte à rebours) et la lance en un toucher, sans compte (voir lib/quizGratuit) ;
 *   - séance déjà jouée sur cet appareil : elle avance à la matière gratuite suivante (« Ta séance suivante · 2 sur 7 »),
 *     puis, le tour fait, dit ce que l'abonnement ajoute (voir seanceSuivante).
 *
 * Rien n'est inventé : le thème et ses chiffres viennent de l'API des essais gratuits. Sans essai pour l'examen
 * choisi, la carte renvoie vers les corrigés gratuits plutôt que de promettre une séance qui n'existe pas.
 *
 * Hauteur minimale réservée : la carte change de contenu (question, puis séance) sans pousser la page.
 */
/**
 * Le meilleur score du visiteur parmi les séances gratuites qu'il a jouées pour cet examen sur cet appareil (voir
 * lib/seancesGratuites) : celui dont la part de bonnes réponses est la plus haute. Null sans score connu.
 */
export function meilleurScore(scores: ReadonlyMap<string, ScoreSeance | null>, cursusId: number): ScoreSeance | null {
  let meilleur: ScoreSeance | null = null
  for (const [cle, score] of scores) {
    if (!score || !cle.startsWith(`${cursusId}:`)) continue
    if (!meilleur || score.reussies / score.total > meilleur.reussies / meilleur.total) meilleur = score
  }
  return meilleur
}

/**
 * Où en est le visiteur et de quoi lancer sa séance : partagé par la carte du hero et par la barre « Commencer » qui
 * suit le défilement sur un téléphone (voir BarreCommencer). Chacune a son propre état de lancement ; les requêtes,
 * elles, sont partagées par leur clé de cache.
 */
export function usePremiereSeance(country: string, cible: "premiere_seance" | "barre_commencer" = "premiere_seance") {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const choisi = useCursusPrepareDeclare(country)
  // Même clé de cache que /quiz (EssaisGratuitsQuiz) : la liste n'est demandée qu'une fois, et seulement quand
  // un examen est choisi - la question « quel examen ? » n'a besoin d'aucune requête de plus.
  const { data: essais, isPending: essaisEnAttente } = useQuery({
    queryKey: ["quiz", "essais"],
    queryFn: ({ signal }) => listQuizEssais(signal),
    staleTime: 5 * 60_000,
    enabled: choisi !== null,
  })
  const [lancement, setLancement] = useState(false)
  const [erreur, setErreur] = useState("")
  // Lus une fois au montage : la séance se joue sur une autre page, la carte est remontée au retour sur l'accueil.
  const [jouees] = useState(seancesJouees)
  const [scores] = useState(scoresDesSeances)

  const { essai, faites, total } = choisi && essais ? seanceSuivante(essais, choisi.id, jouees) : { essai: null, faites: 0, total: 0 }

  async function commencer(seance: QuizEssai) {
    if (lancement) return
    setLancement(true)
    setErreur("")
    trackEvent("accueil_bouton_clic", { cible })
    try {
      navigate(await lancerQuizGratuit({
        cursus: seance.cursus, subject: seance.subject, theme: seance.theme, connecte: isAuthenticated, source: "accueil_seance",
      }))
    } catch (err) {
      setErreur(err instanceof ApiError ? err.message : t("essais.erreur"))
      setLancement(false)
    }
  }

  return {
    choisi, connecte: isAuthenticated, essaisEnAttente: choisi !== null && essaisEnAttente, essai, faites, total,
    meilleur: choisi ? meilleurScore(scores, choisi.id) : null,
    lancement, erreur, commencer,
  }
}

export function PremiereSeance({ country }: { country: string }) {
  useI18n()
  const { choisi, connecte, essaisEnAttente, essai, faites, total, meilleur, lancement, erreur, commencer } = usePremiereSeance(country)
  const { data: cursusList, isPending: listeEnAttente } = useCursusListe(country, { langue: langueDeListe("", false) })
  const { declarer, enCours: declarationEnCours } = useDeclarerCursus()

  return (
    <section
      aria-label={t("premiere.aria")}
      // Repère lu par le tutoriel du visiteur, qui ne s'ouvre pas par-dessus cette carte (voir lib/guides/contenu.ts).
      data-guide="premiere-seance"
      className="flex min-h-[19.5rem] flex-col overflow-hidden rounded-2xl border border-primary/25 bg-card shadow-lg shadow-primary/5"
    >
      {choisi ? (
        <>
          <EnTete cursus={choisi} />
          <div className="flex flex-1 flex-col p-5">
            {essaisEnAttente ? (
              <Squelette />
            ) : essai ? (
              <Seance
                essai={essai}
                cursus={choisi}
                rang={faites + 1}
                total={total}
                connecte={connecte}
                lancement={lancement}
                onCommencer={() => commencer(essai)}
                dejaFait={<DejaFait faites={faites} meilleur={meilleur} connecte={connecte} />}
              />
            ) : total > 0 ? (
              <TourFait cursus={choisi} total={total} dejaFait={<DejaFait faites={faites} meilleur={meilleur} connecte={connecte} />} />
            ) : (
              <>
                <p className="text-sm text-muted-foreground">{t("premiere.aucune", { cursus: libelleCursus(choisi) })}</p>
                <Button size="lg" asChild className="mt-auto w-full">
                  <Link to={`${epreuvesListPath(country)}?gratuit=true`} onClick={() => trackEvent("accueil_bouton_clic", { cible: "corrige_gratuit" })}>
                    {t("accueil.cta_corrige_gratuit")}
                    <ArrowRight />
                  </Link>
                </Button>
              </>
            )}
            {erreur && (
              <p role="alert" className="mt-3 text-sm text-destructive">
                {erreur}
              </p>
            )}
          </div>
        </>
      ) : (
        <div className="flex flex-1 flex-col p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">{t("premiere.etiquette")}</p>
          <h2 className="mt-2 font-display text-2xl font-semibold leading-tight">{t("premiere.question")}</h2>
          <div className="mt-4 flex flex-wrap gap-2">
            {listeEnAttente
              ? Array.from({ length: 6 }, (_, i) => (
                  <span key={i} aria-hidden="true" className="h-9 w-24 animate-pulse rounded-full bg-muted" />
                ))
              : trierCursus(cursusList).map((cursus) => (
                  <Button
                    key={cursus.id}
                    variant="outline"
                    className="h-9 rounded-full border-primary/30 px-3.5 text-sm hover:border-primary hover:bg-primary/5"
                    disabled={declarationEnCours}
                    onClick={() => declarer(cursus, undefined, "hero")}
                  >
                    {cursus.examen_display}
                    {cursus.series ? ` ${cursus.series.code}` : ""}
                  </Button>
                ))}
          </div>
          <p className="mt-auto pt-4 text-sm text-muted-foreground">{t("premiere.aide")}</p>
        </div>
      )}
    </section>
  )
}

/** L'examen choisi, le moyen d'en changer et le compte à rebours : le bandeau de tête de la carte, comme sur la séance du jour. */
function EnTete({ cursus }: { cursus: Cursus }) {
  return (
    <div className="flex items-center justify-between gap-3 border-b border-primary/15 bg-primary/[0.07] px-5 py-3">
      <SelecteurExamen>
        <button
          type="button"
          aria-label={t("choix.pastille_aria", { cursus: libelleCursus(cursus) })}
          className="inline-flex min-h-9 items-center gap-1 rounded-full font-display text-base font-semibold text-primary transition-colors hover:text-primary/80"
        >
          {libelleCursus(cursus)}
          <ChevronDown className="size-4 opacity-70" aria-hidden="true" />
        </button>
      </SelecteurExamen>
      <CompteAReboursBadge variant="pilule" examenACote />
    </div>
  )
}

function Seance({
  essai,
  cursus,
  rang,
  total,
  connecte,
  lancement,
  onCommencer,
  dejaFait,
}: {
  essai: QuizEssai
  cursus: Cursus
  /** Place de cette séance parmi les séances gratuites de l'examen : 1 pour un visiteur qui n'a encore rien joué. */
  rang: number
  total: number
  connecte: boolean
  lancement: boolean
  onCommencer: () => void
  /** Ce que le visiteur a déjà fait sur cet appareil (voir DejaFait) ; rien à la première visite. */
  dejaFait?: ReactNode
}) {
  const Icone = subjectIcon(essai.subject_code)
  const nb = essai.nb_epreuves ?? 0
  const nbMatiere = essai.nb_epreuves_matiere ?? 0
  // Une fréquence d'une seule épreuve ne prouve rien : on ne l'affiche qu'à partir de deux.
  const frequence = nb >= 2 && nbMatiere >= nb ? tn("seance.frequence", nb, { total: nbMatiere }) : null

  return (
    <>
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">
        {rang > 1 ? t("premiere.etiquette_suivante", { n: rang, total }) : t("premiere.etiquette")}
      </p>
      <h2 className="mt-2 font-display text-2xl font-semibold leading-tight">{capitaliserTheme(essai.theme_name)}</h2>
      <ul className="mt-3 flex flex-wrap gap-2 text-sm">
        <li className={cn("inline-flex items-center gap-1.5 rounded-full px-3 py-1 font-medium", couleurMatiere(essai.subject_code).puce)}>
          <Icone className="size-3.5" aria-hidden="true" />
          {essai.subject_label}
        </li>
        <li className="inline-flex items-center gap-1.5 rounded-full border border-border px-3 py-1 text-muted-foreground">
          <ListChecks className="size-3.5" aria-hidden="true" />
          {tn("quiz.n_questions", essai.nb_questions)}
        </li>
        {frequence && (
          <li className="inline-flex items-center gap-1.5 rounded-full bg-gold/10 px-3 py-1 text-gold-text">
            <Target className="size-3.5" aria-hidden="true" />
            {frequence}
          </li>
        )}
      </ul>
      <div className="mt-auto pt-5">
        <Button size="lg" className="w-full" disabled={lancement} onClick={onCommencer}>
          {lancement ? t("quiz.preparation") : t(connecte ? "premiere.commencer" : "premiere.commencer_anonyme")}
          {!lancement && <ArrowRight />}
        </Button>
        <Link
          to={`/quiz?cursus=${cursus.id}`}
          onClick={() => trackEvent("accueil_bouton_clic", { cible: "quiz" })}
          className="mt-3 block text-center text-sm text-muted-foreground underline-offset-4 transition-colors hover:text-primary hover:underline"
        >
          {t("premiere.autre_matiere")}
        </Link>
        {/* Sous le bouton : au-dessus, ces deux lignes le faisaient descendre de 95 px chez le visiteur qui revient
            (566 px du haut, puis 660, mesuré à 375 x 812). */}
        {dejaFait}
        {/* Ce que la carte lance est le quiz d'une séance, pas la séance : le titre de la page promet « un cours, un vrai
            exercice, un quiz », on dit donc ce que l'abonnement ajoute (audit des accueils, 2026-11-21, V4). */}
        <p className="mt-3 text-center text-xs text-muted-foreground">{t("premiere.avec_abonnement")}</p>
      </div>
    </>
  )
}

/**
 * « 2 séances gratuites déjà faites · meilleur score : 4 sur 5 » : le visiteur qui revient retrouve ce qu'il a fait.
 * Ses scores sont gardés sur l'appareil (voir lib/seancesGratuites) et la carte n'en disait rien. À partir de la
 * troisième séance, on lui propose de créer son compte : ses points y sont repris, alors qu'un autre téléphone ou un
 * stockage vidé les lui ferait perdre. Pas avant : il n'a encore rien à garder.
 */
const SEANCES_AVANT_INVITATION_COMPTE = 3

function DejaFait({ faites, meilleur, connecte }: { faites: number; meilleur: ScoreSeance | null; connecte: boolean }) {
  if (faites < 1) return null
  return (
    <p className="mt-4 border-t border-border/60 pt-3 text-sm text-muted-foreground">
      <span className="flex items-start gap-1.5">
        <Check className="mt-0.5 size-4 shrink-0 text-success" aria-hidden="true" />
        <span>
          {tn("premiere.deja_fait", faites)}
          {meilleur && <> · {t("premiere.meilleur_score", { r: meilleur.reussies, n: meilleur.total })}</>}
        </span>
      </span>
      {!connecte && faites >= SEANCES_AVANT_INVITATION_COMPTE && (
        <Link
          to="/connexion"
          onClick={() => trackEvent("accueil_bouton_clic", { cible: "creer_compte" })}
          className="mt-1.5 inline-flex min-h-9 items-center gap-1 font-medium text-primary underline-offset-4 hover:underline"
        >
          {t("premiere.garder_points")}
          <ArrowRight className="size-3.5" aria-hidden="true" />
        </Link>
      )}
    </p>
  )
}

/**
 * Toutes les séances gratuites de l'examen sont jouées : la carte ne repropose pas la première comme si de rien n'était.
 * Elle dit ce qui vient ensuite (la séance de chaque jour, avec l'abonnement) et laisse rejouer ce qui est gratuit.
 */
function TourFait({ cursus, total, dejaFait }: { cursus: Cursus; total: number; dejaFait?: ReactNode }) {
  return (
    <>
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">{t("premiere.tour_etiquette")}</p>
      <h2 className="mt-2 font-display text-2xl font-semibold leading-tight">{tn("premiere.tour_titre", total)}</h2>
      <p className="mt-3 text-sm text-muted-foreground">{t("premiere.tour_texte")}</p>
      {dejaFait}
      <div className="mt-auto pt-5">
        <Button size="lg" asChild className="w-full">
          <Link to="/tarifs" onClick={() => trackEvent("accueil_bouton_clic", { cible: "prix" })}>
            {t("essai.voir_abonnements")}
            <ArrowRight />
          </Link>
        </Button>
        <Link
          to={`/quiz?cursus=${cursus.id}`}
          onClick={() => trackEvent("accueil_bouton_clic", { cible: "quiz" })}
          className="mt-3 block text-center text-sm text-muted-foreground underline-offset-4 transition-colors hover:text-primary hover:underline"
        >
          {t("premiere.tour_refaire")}
        </Link>
      </div>
    </>
  )
}

function Squelette() {
  return (
    <div aria-hidden="true" className="flex flex-1 animate-pulse flex-col">
      <span className="h-3 w-32 rounded bg-muted" />
      <span className="mt-3 h-7 w-3/4 rounded bg-muted" />
      <span className="mt-4 h-7 w-1/2 rounded-full bg-muted" />
      <span className="mt-auto h-11 w-full rounded-md bg-muted" />
    </div>
  )
}
