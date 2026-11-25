import { Link } from "react-router-dom"
import { ArrowRight, Loader2, RotateCcw } from "lucide-react"

import { Button } from "@/components/ui/button"
import { useRefaireErreurs, type EchecRefaire } from "@/lib/erreurs"
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
export function LigneErreurs({
  total, cursusId, rangee = false,
}: { total: number; cursusId: number; rangee?: boolean }) {
  useI18n()
  const { lancer, enCours, echec } = useRefaireErreurs(cursusId)
  if (total <= 0) return null
  // `rangee` : une ligne du bloc « À continuer » de l'accueil (voir AccueilEleve), sans cadre ni marge à elle.
  const Cadre = rangee ? "div" : "section"
  return (
    <Cadre className={rangee ? undefined : "mx-auto max-w-5xl px-4 pt-6 sm:px-6"} aria-label={rangee ? undefined : t("erreurs.titre")}>
      <div className={rangee ? "flex items-center gap-3 px-5 py-3" : "flex items-center gap-3 rounded-2xl border border-border bg-card px-5 py-3"}>
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
      <EchecRefaireErreurs echec={echec} className={rangee ? "px-5 pb-3" : "px-1"} />
    </Cadre>
  )
}
