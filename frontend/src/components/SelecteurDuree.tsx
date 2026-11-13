import type { Plan } from "@/api/types"
import { dateLimiteCampagne, nomCampagne } from "@/lib/campagne"
import { tn, t, useI18n } from "@/lib/i18n"
import { dateFinAcces, formaterDateLongue, prixTotal, prixTotalReference } from "@/lib/tarifs"
import { cn, formatAmount } from "@/lib/utils"

/**
 * Le choix de la durée, en deux morceaux que la page Tarifs sépare (les puces dans l'étape « combien de mois »,
 * le total dans le récapitulatif collé à côté) et que le tunnel d'abonnement empile (`SelecteurDuree`) :
 *
 * - `ChoixDuree` : 1 à N mois, plus le raccourci « Jusqu'à l'examen » qui prend tous les mois qui restent.
 * - `RecapDuree` : le total écrit en toutes lettres - « 5 mois × 2 000 FCFA par mois » - avec le jour où l'accès prend
 *   fin. Rien ne se calcule dans la tête de l'élève, rien ne se renouvelle tout seul.
 *
 * Le dernier mois proposé (`mois_max`) couvre la fin de l'examen. Le total est `mois × prix du mois` : le serveur applique
 * la campagne au prix du mois, puis multiplie (voir Plan.tarif) - le montant affiché est donc celui qu'il facture, à
 * l'unité près. Le prix est le même pour tous les enfants d'une famille.
 */

interface ChoixDureeProps {
  /** Un plan vendu au mois : son prix (`effective_price`) est celui d'UN mois, `mois_max` borne le choix. */
  plan: Plan
  /** Le nombre de mois retenu (déjà ramené à 1..mois_max, voir `moisValides`). */
  mois: number
  onChoisir: (mois: number) => void
  /** Faux quand l'appelant porte déjà le titre de l'étape (« 2 · Pour combien de mois ? ») : le groupe garde son nom accessible. */
  afficherTitre?: boolean
  className?: string
}

export function ChoixDuree({ plan, mois, onChoisir, afficherTitre = true, className }: ChoixDureeProps) {
  useI18n()
  const maximum = Math.max(plan.mois_max, 1)
  const options = Array.from({ length: maximum }, (_, i) => i + 1)

  if (maximum <= 1) {
    return <p className={cn("text-sm text-muted-foreground", className)}>{t("sb.un_seul_mois")}</p>
  }

  return (
    <div className={cn("flex flex-col gap-2", className)}>
      {afficherTitre && <p className="text-sm font-semibold">{t("sb.duree_titre")}</p>}
      <div role="radiogroup" aria-label={t("sb.duree_titre")} className="grid grid-cols-[repeat(auto-fill,minmax(4rem,1fr))] gap-2">
        {options.map((n) => (
          <button
            key={n}
            type="button"
            role="radio"
            aria-checked={n === mois}
            onClick={() => onChoisir(n)}
            className={cn(
              "flex min-h-14 flex-col items-center justify-center rounded-xl border-2 px-1 py-1.5 transition-all",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2",
              n === mois ? "border-primary bg-accent ring-1 ring-primary" : "border-input hover:border-primary/50",
            )}
          >
            <span className="font-display text-lg font-semibold leading-none">{n}</span>
            <span className="mt-0.5 text-[11px] leading-none text-muted-foreground">{tn("sb.unite_mois", n)}</span>
          </button>
        ))}
      </div>
      {maximum > 3 && (
        <button
          type="button"
          onClick={() => onChoisir(maximum)}
          aria-pressed={mois === maximum}
          className={cn(
            "min-h-11 rounded-xl border px-3 text-sm font-medium transition-colors",
            mois === maximum
              ? "border-primary bg-primary text-primary-foreground"
              : "border-input text-foreground hover:border-primary/50",
          )}
        >
          {tn("sb.jusqua_examen", maximum)}
        </button>
      )}
    </div>
  )
}

interface RecapDureeProps {
  plan: Plan
  mois: number
  /** La date de fin de l'accès actuel de l'enfant, s'il en a un en cours : les nouveaux mois s'ajoutent à sa suite. */
  accesActuelJusqua?: Date | null
  className?: string
}

export function RecapDuree({ plan, mois, accesActuelJusqua, className }: RecapDureeProps) {
  useI18n()
  const maximum = Math.max(plan.mois_max, 1)
  const total = prixTotal(plan, mois)
  const totalSansCampagne = prixTotalReference(plan, mois)
  // Un abonné qui prolonge : les mois s'ajoutent à la fin de son accès en cours (côté serveur, Subscription.extend),
  // pas à aujourd'hui - la date annoncée doit être celle qu'il aura vraiment.
  const prolonge = accesActuelJusqua != null && accesActuelJusqua.getTime() > Date.now()
  const finAcces = formaterDateLongue(dateFinAcces(mois, prolonge ? accesActuelJusqua : new Date()))

  return (
    <div className={cn("flex flex-col gap-3", className)}>
      <div aria-live="polite" className="rounded-xl border-2 border-primary bg-accent px-4 py-3.5 ring-1 ring-primary">
        <div className="flex items-baseline justify-between gap-3">
          <span className="shrink-0 text-sm text-muted-foreground">{t("sb.total")}</span>
          <span className="whitespace-nowrap font-display text-2xl font-semibold text-primary">
            {formatAmount(total)} FCFA
          </span>
        </div>
        {plan.campagne && (
          <p className="text-right text-xs text-muted-foreground">
            {t("sb.au_lieu_de", { prix: formatAmount(totalSansCampagne) })}
          </p>
        )}
        <p className="mt-1 text-sm">{tn("sb.total_calcul", mois, { prix: formatAmount(plan.effective_price) })}</p>
        <p className="mt-0.5 text-sm text-muted-foreground">
          {t(prolonge ? "sb.acces_prolonge_jusqu_au" : "sb.acces_jusqu_au", { date: finAcces })}
        </p>
        {mois === maximum && maximum > 1 && (
          <p className="mt-0.5 text-xs font-medium text-success">{t("sb.couvre_examen")}</p>
        )}
        {plan.campagne && (
          <p className="mt-1.5 text-xs font-medium text-success">
            {t("sb.camp_ligne_mois", {
              nom: nomCampagne(plan.campagne),
              pct: plan.campagne.pourcentage,
              a: formatAmount(plan.prix_reference),
              b: formatAmount(plan.effective_price),
              date: dateLimiteCampagne(plan.campagne.fin),
            })}
          </p>
        )}
      </div>
      <p className="text-xs text-muted-foreground">{t("sb.sans_renouvellement")}</p>
    </div>
  )
}

interface SelecteurDureeProps extends ChoixDureeProps {
  accesActuelJusqua?: Date | null
}

/** Les deux morceaux empilés : le tunnel d'abonnement, où l'élève choisit puis lit son total au même endroit. */
export function SelecteurDuree({ plan, mois, onChoisir, accesActuelJusqua, className }: SelecteurDureeProps) {
  return (
    <div className={cn("flex flex-col gap-4", className)}>
      <ChoixDuree plan={plan} mois={mois} onChoisir={onChoisir} />
      <RecapDuree plan={plan} mois={mois} accesActuelJusqua={accesActuelJusqua} />
    </div>
  )
}
