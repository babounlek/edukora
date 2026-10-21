import type { ComparaisonCandidats, PertesParCause, TempsExercice } from "@/api/types"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { formatPoints, libellePoints } from "@/lib/notation"
import { cn } from "@/lib/utils"
import { t, useI18n, type CleI18n } from "@/lib/i18n"
import type { Unite } from "@/lib/vocabulaire"

// Les libellés de cause viennent du serveur, en français : on les traduit d'après le CODE de cause, selon la langue
// de l'interface (test élève Gogo : « Questions non traitées » sur un bilan en anglais). Un code inconnu garde le
// libellé du serveur.
const CLES_CAUSES: Record<string, CleI18n> = {
  NON_TRAITEE: "rf.cause_NON_TRAITEE",
  TEMPS: "rf.cause_TEMPS",
  CONNAISSANCE: "rf.cause_CONNAISSANCE",
  METHODE: "rf.cause_METHODE",
  CALCUL: "rf.cause_CALCUL",
  INATTENTION: "rf.cause_INATTENTION",
  NON_PRECISEE: "rf.cause_NON_PRECISEE",
}

function libelleCause(cause: string, libelleServeur: string, unite: Unite): string {
  if (cause === "NON_TRAITEE" && unite === "exercice") return t("rf.cause_NON_TRAITEE_exercice")
  const cle = CLES_CAUSES[cause]
  return cle ? t(cle) : libelleServeur
}

/** « 42 min », « 1 h 05 » - un temps de travail, jamais des secondes brutes. */
function formatMinutes(secondes: number): string {
  const minutes = Math.round(secondes / 60)
  if (minutes < 60) return `${minutes} min`
  return `${Math.floor(minutes / 60)} h ${String(minutes % 60).padStart(2, "0")}`
}

/**
 * « Où sont passés tes points » : ce que la note seule ne dit pas. Les points perdus par
 * manque de temps, par erreur de calcul ou par ignorance ne se rattrapent pas de la même
 * façon - c'est cette répartition, plus que le total, qui dit quoi travailler.
 */
export function CartePertes({ pertes, unite = "question" }: { pertes: PertesParCause; unite?: Unite }) {
  useI18n()
  if (pertes.causes.length === 0) {
    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="font-display text-lg">{t("rf.pertes_titre")}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">{t("rf.aucune_perte")}</p>
        </CardContent>
      </Card>
    )
  }
  const nonPrecisees = pertes.causes.find((c) => c.cause === "NON_PRECISEE")
  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="font-display text-lg">{t("rf.pertes_titre")}</CardTitle>
        <p className="text-xs text-muted-foreground">{t("rf.perdu", { points: libellePoints(pertes.total_perdu) })}</p>
      </CardHeader>
      <CardContent>
        <ul className="flex flex-col gap-4">
          {pertes.causes.map((cause) => (
            <li key={cause.cause}>
              <div className="mb-1.5 flex items-center justify-between gap-3 text-sm">
                <span>{libelleCause(cause.cause, cause.libelle, unite)}</span>
                <span className="shrink-0 tabular-nums text-muted-foreground">
                  {t("gn.pts_court", { p: formatPoints(cause.points) })} · {t("oujensuis.pct", { pct: cause.part })}
                </span>
              </div>
              <div
                role="progressbar"
                aria-label={libelleCause(cause.cause, cause.libelle, unite)}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={cause.part}
                className="h-2 overflow-hidden rounded-full bg-secondary"
              >
                <div className="h-full rounded-full bg-primary" style={{ width: `${cause.part}%` }} />
              </div>
            </li>
          ))}
        </ul>
        {nonPrecisees && nonPrecisees.part >= 30 && (
          <p className="mt-4 text-xs text-muted-foreground">
            {t("rf.sans_cause")}
          </p>
        )}
      </CardContent>
    </Card>
  )
}

/**
 * « Ton temps » : le temps passé sur chaque exercice face aux points qu'il rapportait. Une
 * estimation (elle vient des moments où les questions ont été cochées), présentée comme telle.
 */
export function CarteTemps({ temps, chronophage }: { temps: TempsExercice[]; chronophage: string | null }) {
  useI18n()
  const pire = chronophage ? temps.find((t) => t.numero_exercice === chronophage) : null
  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="font-display text-lg">{t("rf.temps_titre")}</CardTitle>
        <p className="text-xs text-muted-foreground">{t("rf.temps_estime")}</p>
      </CardHeader>
      <CardContent>
        <ul className="flex flex-col gap-4">
          {temps.map((ligne) => (
            <li key={ligne.numero_exercice}>
              <div className="mb-1.5 flex items-center justify-between gap-3 text-sm">
                <span className={cn(ligne.numero_exercice === chronophage && "font-semibold")}>
                  {t("ed.exercice_n", { n: ligne.numero_exercice })}
                </span>
                <span className="shrink-0 tabular-nums text-muted-foreground">
                  {t("rf.pct_temps", { d: formatMinutes(ligne.secondes), p: ligne.part_du_temps })}
                </span>
              </div>
              {/* Deux barres superposées : le temps consommé, et - en repère - la part des points. */}
              <div className="relative h-2 overflow-hidden rounded-full bg-secondary" aria-hidden="true">
                <div className="h-full rounded-full bg-primary/80" style={{ width: `${ligne.part_du_temps}%` }} />
                <div
                  className="absolute inset-y-0 w-0.5 bg-foreground/70"
                  style={{ left: `${Math.min(ligne.part_des_points, 99)}%` }}
                />
              </div>
              <p className="mt-1 text-xs text-muted-foreground">{t("rf.vaut", { p: ligne.part_des_points })}</p>
            </li>
          ))}
        </ul>
        {pire && (
          <p className="mt-4 rounded-lg bg-warning/10 px-3 py-2 text-sm">
            {t("rf.chronophage", { n: pire.numero_exercice, t: pire.part_du_temps, p: pire.part_des_points })}
          </p>
        )}
      </CardContent>
    </Card>
  )
}

/** « Ta position » : parmi les autres candidats de la même épreuve en conditions réelles. */
export function CartePosition({ comparaison }: { comparaison: ComparaisonCandidats }) {
  useI18n()
  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="font-display text-lg">{t("rf.position_titre")}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm">
          {t("rf.mieux_avant")} <strong className="tabular-nums">{t("oujensuis.pct", { pct: comparaison.percentile })}</strong>{" "}
          {t("rf.mieux_apres")}
        </p>
        <p className="mt-1 text-xs text-muted-foreground">
          {t("rf.effectif", { n: comparaison.effectif, moy: formatPoints(comparaison.moyenne) })}
        </p>
      </CardContent>
    </Card>
  )
}
