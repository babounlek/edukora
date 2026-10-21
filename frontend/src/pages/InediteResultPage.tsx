import { useEffect, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { ClipboardCheck, Info, Trophy } from "lucide-react"

import { ApiError } from "@/api/client"
import type { TentativeInediteResult } from "@/api/types"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { CartePertes, CartePosition, CarteTemps } from "@/components/inedit/RapportFin"
import { formatDureeEcoulee } from "@/lib/duration"
import { formatPoints } from "@/lib/notation"
import { useAuth } from "@/context/AuthContext"
import { lienAbonnement } from "@/lib/retourAchat"
import { useSeo } from "@/lib/seo"
import { apiPour, cheminEpreuve, cheminRetour, type SourceEpreuve } from "@/lib/apiEpreuve"
import { coursListPath, epreuvesListPath } from "@/lib/countryPath"
import { tnu, uniteDe } from "@/lib/vocabulaire"
import { t, useI18n } from "@/lib/i18n"
import { capitaliserTheme, cn } from "@/lib/utils"

/** Barre « points obtenus / points possibles » : la couleur suit le taux, pas le libellé -
 * un thème à 30 % doit se voir sans qu'on lise les chiffres. */
function BarrePoints({ obtenus, possibles, label }: { obtenus: number; possibles: number; label: string }) {
  const taux = possibles > 0 ? obtenus / possibles : 0
  return (
    <div
      role="progressbar"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={possibles}
      aria-valuenow={obtenus}
      className="h-2 overflow-hidden rounded-full bg-secondary"
    >
      <div
        className={cn("h-full rounded-full transition-all", taux >= 0.7 ? "bg-success" : taux >= 0.5 ? "bg-primary" : "bg-warning")}
        style={{ width: `${Math.round(taux * 100)}%` }}
      />
    </div>
  )
}

const CLE_MODE: Record<TentativeInediteResult["mode"], "cm.reelles" | "rp.mode_papier" | "cm.libre"> = {
  examen: "cm.reelles",
  papier: "rp.mode_papier",
  libre: "cm.libre",
}

/** « aujourd'hui », « demain », « dans 3 jours » - jamais une date brute. */
function echeanceRelative(iso: string): string {
  const [annee, mois, jour] = iso.split("-").map(Number)
  const debutAujourdhui = new Date()
  debutAujourdhui.setHours(0, 0, 0, 0)
  const jours = Math.round((new Date(annee, mois - 1, jour).getTime() - debutAujourdhui.getTime()) / 86_400_000)
  if (jours <= 0) return t("rp.ech_aujourdhui")
  if (jours === 1) return t("seance.echeance_demain")
  return t("seance.echeance_jours", { n: jours })
}

export function InediteResultPage({ source = "inedit" }: { source?: SourceEpreuve }) {
  useI18n()

  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  useSeo({ title: source === "officielle" ? t("rp.seo_simulation") : t("rp.seo") })
  const [result, setResult] = useState<TentativeInediteResult | null>(null)
  const [error, setError] = useState("")

  useEffect(() => {
    if (!id) return
    // On regarde D'ABORD où en est la copie : `terminer` rend la copie si elle ne l'est pas
    // déjà, et cette page s'ouvre aussi depuis l'historique du navigateur ou une adresse
    // collée - une épreuve chronométrée en cours y était clôturée, notée zéro, sans que
    // l'élève l'ait décidé. Une copie encore en cours retourne à l'épreuve. (Charger une
    // copie dont le chrono est écoulé la verrouille, voir inedit.views._auto_complete_if_expired :
    // elle arrive alors ici déjà rendue.)
    const api = apiPour(source)
    const numero = Number(id)
    api.charger(numero)
      .then(async (copie) => {
        if (copie.submitted_at === null) {
          navigate(cheminEpreuve(source, numero), { replace: true })
          return
        }
        // Endpoint idempotent : copie déjà soumise, il se contente de retourner le résultat
        // déjà calculé (voir inedit.views.complete_tentative).
        setResult(await api.terminer(numero))
      })
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : t("rp.erreur"))
      })
  }, [id, source, navigate])

  if (error) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10 text-center">
        <p className="text-destructive">{error}</p>
        <Link
          to={result ? cheminRetour(source, result.country) : "/"}
          className="mt-3 inline-block text-sm text-primary hover:underline"
        >
          {t("ed.retour_catalogue")}
        </Link>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="mx-auto max-w-xl px-4 py-10">
        <Skeleton className="mb-4 h-8 w-48" />
        <Skeleton className="h-24 w-full" />
      </div>
    )
  }

  const surVingt = result.bareme === 20
  const unite = uniteDe(result.granularite)
  const exercice = result.granularite === "exercice"
  // Du plus fragile au plus solide : c'est ce qu'on veut retravailler qui doit sauter aux yeux.
  const themes = [...result.par_theme].sort((a, b) => {
    const tauxA = a.points_possibles ? (a.points_obtenus ?? 0) / a.points_possibles : 1
    const tauxB = b.points_possibles ? (b.points_obtenus ?? 0) / b.points_possibles : 1
    return tauxA - tauxB
  })
  // Une question qui porte plusieurs thèmes compte dans chacun : la somme des points par compétence peut alors
  // dépasser le barème de l'épreuve, ce que l'élève prendrait pour une erreur de calcul.
  const themesSeRecoupent =
    result.bareme !== null && themes.reduce((somme, theme) => somme + (theme.points_possibles ?? 0), 0) > result.bareme

  return (
    <div className="mx-auto max-w-xl animate-fade-up px-4 py-10">
      <div className="mb-8 text-center">
        <Trophy className="mx-auto mb-3 size-8 text-gold-text" />
        <h1 className="font-display text-3xl font-semibold">{t("rp.titre")}</h1>
        <p className="mt-1 text-sm text-muted-foreground">{result.epreuve_titre}</p>
        {/* Comment l'épreuve a été passée : une note d'entraînement ne se lit pas comme une note
            obtenue chronomètre en main. */}
        <Badge variant="outline" className="mt-3">
          {t(CLE_MODE[result.mode])}
        </Badge>

        {result.note !== null && result.bareme !== null && (
          <>
            <p className="mt-5 font-display text-6xl font-semibold tabular-nums" aria-label={t("rp.note_aria", { a: formatPoints(result.note), b: formatPoints(result.bareme) })}>
              {formatPoints(result.note)}
              <span className="text-2xl font-normal text-muted-foreground"> / {formatPoints(result.bareme)}</span>
            </p>
            {!surVingt && result.note_sur_20 !== null && (
              <p className="mt-1 text-sm text-muted-foreground">
                {t("rp.soit")} <strong className="tabular-nums">{formatPoints(result.note_sur_20)} / 20</strong>
              </p>
            )}
            <p className="mt-2 text-sm font-medium">
              {result.definitive ? t("rp.definitive") : t("rp.provisoire")}
              {result.score !== null && <span className="font-normal text-muted-foreground">{t("rp.du_bareme", { score: result.score })}</span>}
            </p>
          </>
        )}

        <p className="mt-3 text-sm text-muted-foreground">
          {tnu("rp.repondues", unite, result.questions_repondues, { total: result.total_questions })}
          {result.temps_total_secondes !== null && t("rp.temps_utilise", { duree: formatDureeEcoulee(result.temps_total_secondes) })}
        </p>
      </div>

      {result.questions_a_noter > 0 && (
        <div role="status" className="mb-6 rounded-xl border border-primary/30 bg-primary/5 px-4 py-3.5">
          <p className="flex items-start gap-2 text-sm">
            <ClipboardCheck className="mt-0.5 size-5 shrink-0 text-primary" />
            <span>
              <strong>{t("rp.provisoire_titre")}</strong> {tnu("rp.a_noter", unite, result.questions_a_noter)}
            </span>
          </p>
          <Button asChild className="mt-3 w-full" size="lg">
            <Link to={`${cheminEpreuve(source, result.id)}?noter=1`}>{t("rp.terminer_notation")}</Link>
          </Button>
        </div>
      )}

      {result.questions_non_traitees > 0 && (
        <p className="mb-6 flex items-start gap-2 text-sm text-muted-foreground">
          <Info className="mt-0.5 size-4 shrink-0" />
          <span>
            {tnu("rp.non_traitees", unite, result.questions_non_traitees)}
          </span>
        </p>
      )}

      <CartePertes pertes={result.pertes} unite={unite} />
      {result.temps_par_exercice && (
        <CarteTemps temps={result.temps_par_exercice} chronophage={result.exercice_chronophage} />
      )}
      {result.comparaison && <CartePosition comparaison={result.comparaison} />}

      {result.par_exercice.length > 1 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="font-display text-lg">{t("rp.par_exercice")}</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="flex flex-col gap-4">
              {result.par_exercice.map((exercice) => (
                <li key={exercice.numero_exercice}>
                  <div className="mb-1.5 flex items-center justify-between text-sm">
                    <span>
                      {t("ed.exercice_n", { n: exercice.numero_exercice })}
                      {exercice.compte === false && (
                        <Badge variant="outline" className="ml-2 text-xs font-normal">{t("ct.non_compte")}</Badge>
                      )}
                    </span>
                    <span className="tabular-nums text-muted-foreground">
                      {formatPoints(exercice.points_obtenus)} / {formatPoints(exercice.points_possibles)}
                    </span>
                  </div>
                  <BarrePoints
                    obtenus={exercice.points_obtenus ?? 0}
                    possibles={exercice.points_possibles ?? 0}
                    label={t("ed.exercice_n", { n: exercice.numero_exercice })}
                  />
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {themes.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="font-display text-lg">{t("rp.par_competence")}</CardTitle>
            <p className="text-xs text-muted-foreground">
              {t("rp.fragile_solide")}
              {themesSeRecoupent && ` ${t("rp.competences_recoupees")}`}
            </p>
          </CardHeader>
          <CardContent>
            <ul className="flex flex-col gap-4">
              {themes.map((theme) => (
                <li key={theme.theme}>
                  <div className="mb-1.5 flex items-start justify-between gap-3 text-sm">
                    <span>{capitaliserTheme(theme.theme)}</span>
                    <span className="shrink-0 tabular-nums text-muted-foreground">
                      {t("gn.pts", { a: formatPoints(theme.points_obtenus), b: formatPoints(theme.points_possibles) })}
                    </span>
                  </div>
                  <BarrePoints
                    obtenus={theme.points_obtenus ?? 0}
                    possibles={theme.points_possibles ?? 0}
                    label={capitaliserTheme(theme.theme)}
                  />
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {result.themes_a_reviser.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="font-display text-lg">{t("rp.reverras_titre")}</CardTitle>
            <p className="text-xs text-muted-foreground">
              {t("rp.reverras_texte")}
            </p>
          </CardHeader>
          <CardContent>
            <ul className="flex flex-col gap-2">
              {result.themes_a_reviser.map((theme) => (
                <li key={theme.theme} className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1 text-sm">
                  <span>{capitaliserTheme(theme.theme)}</span>
                  <span className="flex shrink-0 items-center gap-3 text-muted-foreground">
                    {echeanceRelative(theme.echeance)}
                    {/* Deux façons de s'y mettre tout de suite, sans attendre la séance de demain. */}
                    {result.cursus_id !== null && theme.a_quiz !== false && (
                      <Link
                        to={`/quiz?cursus=${result.cursus_id}&theme=${theme.theme_id}`}
                        className="font-medium text-primary underline-offset-2 hover:underline"
                      >
                        {t("qd.onglet_quiz")}
                      </Link>
                    )}
                    {theme.a_cours !== false && (
                      <Link
                        to={`${coursListPath(result.country.toLowerCase())}?theme=${theme.theme_id}`}
                        className="font-medium text-primary underline-offset-2 hover:underline"
                      >
                        {t("nav.cours")}
                      </Link>
                    )}
                  </span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {result.bareme_estime && (
        <p className="mb-6 flex items-start gap-2 text-xs text-muted-foreground">
          <Info className="mt-0.5 size-3.5 shrink-0" />
          {exercice
            ? t("ct.bareme_estime_exercice")
            : t("rp.bareme_estime_question")}
        </p>
      )}

      {/* Une copie rendue sans abonnement est forcément celle de l'épreuve offerte : c'est le
          moment où la valeur du produit vient d'être vécue, pas avant. Jamais pour un abonné. */}
      {source === "inedit" && user?.a_un_abonnement_actif === false && result.cursus_id !== null && (
        <div className="mb-6 rounded-xl border border-gold/40 bg-gold/5 px-4 py-3.5">
          <p className="text-sm">
            <strong>{t("rp.offerte_titre")}</strong> {t("rp.offerte_texte")}
          </p>
          <Button asChild className="mt-3 w-full" size="lg" variant="outline">
            <Link
              to={lienAbonnement(
                result.cursus_id,
                `${epreuvesListPath(result.country.toLowerCase())}?origine=INEDITE`,
              )}
            >
              {t("rp.debloquer_autres")}
            </Link>
          </Button>
        </div>
      )}

      <div className="flex flex-col gap-2">
        <Button asChild size="lg">
          <Link to={cheminEpreuve(source, result.id)}>{t("rp.revoir_copie")}</Link>
        </Button>
        <div className="flex flex-col gap-2 sm:flex-row">
          <Button asChild variant="outline" className="flex-1" size="lg">
            <Link to={cheminRetour(source, result.country)}>
              {source === "officielle" ? t("rp.voir_epreuves") : t("rp.voir_inedites")}
            </Link>
          </Button>
          <Button asChild variant="outline" className="flex-1" size="lg">
            <Link to="/parcours">{t("rp.voir_parcours")}</Link>
          </Button>
        </div>
      </div>
    </div>
  )
}
