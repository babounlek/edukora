import { useQuery } from "@tanstack/react-query"
import { ArrowRight, CalendarCheck, Flame, Sparkles, Target, TrendingUp, type LucideIcon } from "lucide-react"

import { getBilanPeriode } from "@/api/endpoints"
import type { BilanMatiere, BilanPeriode } from "@/api/types"
import { Ecrin } from "@/components/Progression"
import { capitaliserTheme, cn } from "@/lib/utils"
import { localeCourante, t, tn, useI18n } from "@/lib/i18n"

/**
 * "Ton bilan" : ce que l'élève a réellement fait sur les 30 derniers jours de son
 * abonnement - séances, questions, progression, thèmes consolidés.
 *
 * C'est l'argument du renouvellement, et il n'en a que la valeur du vrai : rien n'est
 * inventé ni arrondi vers le haut. Sans activité (voir `a_de_l_activite`), le bloc
 * disparaît plutôt que d'afficher trois zéros - qui rappelleraient à l'élève qu'il n'a
 * rien fait au lieu de lui donner envie de reprendre. Une baisse de taux n'est jamais
 * affichée en négatif : on montre le chiffre, sans le commenter.
 */
export function BilanDePeriode({ cursusId, className }: { cursusId: number; className?: string }) {
  useI18n()
  const { data: bilan } = useQuery({
    queryKey: ["bilan-periode", cursusId],
    queryFn: ({ signal }) => getBilanPeriode(cursusId, signal),
    // Un 404 (jamais abonné) est une réponse, pas une panne à retenter.
    retry: false,
  })

  if (!bilan || !bilan.a_de_l_activite) return null

  const gain = gainDeTaux(bilan)

  return (
    <div className={cn("@container", className)}>
      <Ecrin variante="sobre" className="sm:p-6">
        <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
          <TrendingUp className="size-3.5" />
          {t("bilan.titre")}
        </p>
        <h2 className="mt-2 font-display text-2xl font-semibold leading-tight tracking-tight text-balance sm:text-3xl">
          {titre(bilan)}
        </h2>
        <p className="mt-1 text-sm text-muted-foreground">
          {t("bilan.periode", { debut: jourMois(bilan.debut), fin: jourMois(bilan.fin) })}
          {!bilan.abonnement_actif && t("bilan.conservee")}
        </p>

        <dl className="mt-5 grid grid-cols-2 gap-3 @xl:grid-cols-4">
          <Chiffre icone={CalendarCheck} valeur={bilan.seances} unite={tn("bilan.seances", bilan.seances)} />
          <Chiffre
            icone={Target}
            valeur={bilan.questions}
            unite={tn("bilan.questions", bilan.questions)}
          />
          <Chiffre
            icone={Sparkles}
            valeur={bilan.taux_reussite === null ? "–" : t("oujensuis.pct", { pct: bilan.taux_reussite })}
            unite={t("bilan.reussite")}
            note={gain !== null ? tn("bilan.gain", gain) : undefined}
          />
          {bilan.meilleure_serie >= 2 ? (
            <Chiffre icone={Flame} valeur={bilan.meilleure_serie} unite={t("bilan.serie")} />
          ) : (
            <Chiffre icone={CalendarCheck} valeur={bilan.jours_actifs} unite={tn("bilan.jours", bilan.jours_actifs)} />
          )}
        </dl>

        {bilan.themes_consolides_total > 0 && (
          <div className="mt-6">
            <h3 className="text-sm font-semibold">
              {tn("bilan.consolides", bilan.themes_consolides_total)}
            </h3>
            <ul className="mt-2 flex flex-wrap gap-2">
              {bilan.themes_consolides.map((theme) => (
                <li
                  key={`${theme.subject_label}-${theme.theme}`}
                  className="rounded-full border border-primary/25 bg-primary/[0.07] px-3 py-1 text-xs font-medium text-primary"
                >
                  {capitaliserTheme(theme.theme)}
                  <span className="text-muted-foreground"> · {theme.subject_label}</span>
                </li>
              ))}
              {bilan.themes_consolides_total > bilan.themes_consolides.length && (
                <li className="px-1 py-1 text-xs text-muted-foreground">
                  {tn("depuis.autres", bilan.themes_consolides_total - bilan.themes_consolides.length)}
                </li>
              )}
            </ul>
          </div>
        )}

        {bilan.matieres.length > 0 && (
          <div className="mt-6">
            <h3 className="text-sm font-semibold">{t("bilan.par_matiere")}</h3>
            <ul className="mt-2 flex flex-col divide-y divide-border/60">
              {bilan.matieres.map((matiere) => (
                <LigneMatiere key={matiere.subject_id} matiere={matiere} />
              ))}
            </ul>
          </div>
        )}
      </Ecrin>
    </div>
  )
}

/** Points de réussite gagnés par rapport à avant la période - jamais une baisse : le
 * chiffre brut reste affiché, sans être commenté en négatif. Il faut un socle
 * comparable des deux côtés, sinon "+40 points" sur 2 réponses ne voudrait rien dire. */
function gainDeTaux(bilan: BilanPeriode): number | null {
  if (bilan.taux_reussite === null || bilan.taux_avant === null || bilan.questions < 5) return null
  const gain = bilan.taux_reussite - bilan.taux_avant
  return gain > 0 ? gain : null
}

/** Le titre dit la chose la plus flatteuse qui soit VRAIE, dans cet ordre. */
function titre(bilan: BilanPeriode): string {
  if (bilan.themes_consolides_total > 0) {
    const n = bilan.themes_consolides_total
    return tn("bilan.titre_themes", n)
  }
  if (bilan.seances > 0) return tn("bilan.titre_seances", bilan.seances)
  return tn("bilan.titre_questions", bilan.questions)
}

function Chiffre({
  icone: Icone, valeur, unite, note,
}: { icone: LucideIcon; valeur: number | string; unite: string; note?: string }) {
  return (
    // Libellé (dt) avant la valeur (dd) dans le DOM, comme l'exige une liste de définitions ; l'ordre
    // visuel (icône, chiffre, libellé) est rétabli avec `order`.
    <div className="flex flex-col rounded-2xl border border-border/70 bg-background/70 p-3.5">
      <Icone className="order-1 size-4 text-primary" aria-hidden="true" />
      <dt className="order-3 mt-1.5 text-xs leading-snug text-muted-foreground">{unite}</dt>
      <dd className="order-2 mt-2 font-display text-2xl font-semibold tabular-nums leading-none">{valeur}</dd>
      {note && <p className="order-4 mt-1 text-xs font-semibold text-success">{note}</p>}
    </div>
  )
}

function LigneMatiere({ matiere }: { matiere: BilanMatiere }) {
  const { taux_avant: avant, taux_periode: periode } = matiere
  // La flèche n'apparaît que pour une progression : "avant → maintenant" quand ça monte,
  // le seul taux quand ça stagne ou baisse.
  const enHausse = avant !== null && periode !== null && periode > avant
  return (
    <li className="flex items-center justify-between gap-3 py-2.5 text-sm">
      <span className="min-w-0">
        <span className="block truncate font-medium">{matiere.subject_label}</span>
        <span className="text-xs text-muted-foreground">
          {tn("quiz.n_questions", matiere.questions)}
        </span>
      </span>
      {periode !== null && (
        <span className="flex shrink-0 items-center gap-1.5 font-display font-semibold tabular-nums">
          {enHausse && (
            <>
              <span className="text-xs font-normal text-muted-foreground">{t("oujensuis.pct", { pct: avant })}</span>
              <ArrowRight className="size-3.5 text-success" />
            </>
          )}
          <span className={enHausse ? "text-success" : undefined}>{t("oujensuis.pct", { pct: periode })}</span>
        </span>
      )}
    </li>
  )
}

/** "27 août" à partir de la date AAAA-MM-JJ de l'API, sans passer par un fuseau. */
function jourMois(dateIso: string): string {
  const [annee, mois, jour] = dateIso.split("-").map(Number)
  return new Date(annee, mois - 1, jour).toLocaleDateString(localeCourante(), { day: "numeric", month: "long" })
}
