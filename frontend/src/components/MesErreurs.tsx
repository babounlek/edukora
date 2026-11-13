import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, Loader2, RotateCcw } from "lucide-react"

import { getErreurs } from "@/api/endpoints"
import { Button } from "@/components/ui/button"
import { cleErreurs, useRefaireErreurs, type EchecRefaire } from "@/lib/erreurs"
import { cn } from "@/lib/utils"
import { t, tn, useI18n } from "@/lib/i18n"

/** L'échec d'un lancement, dit près du bouton ; « abonnement requis » mène aux prix plutôt qu'à un nouvel essai. */
export function EchecRefaireErreurs({ echec, className }: { echec: EchecRefaire | null; className?: string }) {
  useI18n()
  if (!echec) return null
  return (
    <p role="alert" className={cn("mt-3 text-sm text-destructive", className)}>
      {echec.message}
      {echec.abonnement && (
        <>
          {" "}
          <Link to="/tarifs" className="font-medium underline underline-offset-4">
            {t("ft.voir_prix")}
          </Link>
        </>
      )}
    </p>
  )
}

/**
 * Sur l'accueil : « 12 erreurs à corriger », et le bouton qui ouvre tout de suite un quiz fait des plus
 * anciennes. Le libellé mène à la page « Mes erreurs » pour qui veut voir où elles sont.
 *
 * Rien sans erreur : la ligne n'existe que quand elle a quelque chose à proposer. Le nombre vient de
 * l'accueil lui-même (voir quiz.views.accueil_view), aucune requête de plus.
 */
export function LigneErreurs({ total, cursusId }: { total: number; cursusId: number }) {
  useI18n()
  const { lancer, enCours, echec } = useRefaireErreurs(cursusId)
  if (total <= 0) return null
  return (
    <section className="mx-auto max-w-5xl px-4 pt-6 sm:px-6" aria-label={t("erreurs.titre")}>
      <div className="flex items-center gap-3 rounded-2xl border border-border bg-card px-5 py-3">
        <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-warning/15 text-warning-foreground dark:text-warning">
          <RotateCcw className="size-4" aria-hidden="true" />
        </span>
        <Link to="/erreurs" className="group min-w-0 flex-1">
          <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">{t("erreurs.titre")}</span>
          <span className="block truncate text-sm font-medium underline-offset-4 group-hover:underline">
            {tn("erreurs.ligne", total)}
          </span>
        </Link>
        <Button
          variant="outline"
          className="min-h-11 shrink-0 rounded-full"
          disabled={enCours !== null}
          onClick={() => lancer()}
        >
          {enCours !== null ? <Loader2 className="animate-spin" /> : null}
          {enCours !== null ? t("quiz.preparation") : t("erreurs.refaire_matiere")}
          {enCours === null && <ArrowRight className="size-4" />}
        </Button>
      </div>
      <EchecRefaireErreurs echec={echec} className="px-1" />
    </section>
  )
}

/**
 * Dans « Ma progression » : la banque d'erreurs en une carte, avec le bouton pour en refaire un paquet
 * et le lien vers le détail par matière. Se tait sans erreur, et tant que la banque n'est pas lue (une
 * carte qui apparaît puis disparaît ferait sauter la page).
 */
export function CarteErreurs({ cursusId, className }: { cursusId: number; className?: string }) {
  useI18n()
  const { data } = useQuery({
    queryKey: cleErreurs(cursusId),
    queryFn: ({ signal }) => getErreurs(cursusId, signal),
    retry: false,
  })
  const { lancer, enCours, echec } = useRefaireErreurs(cursusId)
  if (!data || data.total <= 0) return null
  return (
    <section
      aria-label={t("erreurs.titre")}
      className={cn("rounded-3xl border border-border bg-card p-5 shadow-sm sm:p-6", className)}
    >
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex min-w-0 items-center gap-3">
          <span className="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-warning/15 text-warning-foreground dark:text-warning">
            <RotateCcw className="size-5" aria-hidden="true" />
          </span>
          <div className="min-w-0">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">{t("erreurs.titre")}</p>
            <p className="mt-0.5 font-display text-lg font-semibold leading-snug">{tn("erreurs.total", data.total)}</p>
          </div>
        </div>
        <div className="flex shrink-0 flex-wrap items-center gap-x-4 gap-y-2">
          <Button className="min-h-11 rounded-full" disabled={enCours !== null} onClick={() => lancer()}>
            {enCours !== null ? <Loader2 className="animate-spin" /> : <RotateCcw />}
            {enCours !== null ? t("quiz.preparation") : tn("erreurs.refaire", data.paquet)}
          </Button>
          <Link to="/erreurs" className="text-sm font-medium text-primary underline-offset-4 hover:underline">
            {t("erreurs.voir")}
          </Link>
        </div>
      </div>
      <EchecRefaireErreurs echec={echec} />
    </section>
  )
}
