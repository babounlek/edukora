import { Link } from "react-router-dom"
import { ArrowRight, CheckCircle2, Loader2, Trophy } from "lucide-react"

import type { QuizResult } from "@/api/types"
import { Button } from "@/components/ui/button"
import { useRefaireErreurs } from "@/lib/erreurs"
import { cn } from "@/lib/utils"
import { t, tn, useI18n } from "@/lib/i18n"

/**
 * Ce que le quiz vient de retirer de « Mes erreurs » : « 3 erreurs corrigées, il t'en reste 7 », avec de quoi enchaîner
 * sur les suivantes ; et la fête quand la liste est vide. Jusqu'ici une erreur corrigée sortait de la banque sans un mot :
 * l'élève ne voyait sa liste baisser qu'en retournant sur « Mes erreurs ». Rien à l'écran quand le quiz n'a rien corrigé.
 *
 * `acces` : l'élève peut-il lancer un quiz sur cet examen (abonné) ? Sinon le bouton serait refusé : on renvoie à la liste.
 */
export function BilanErreurs({
  bilan, cursus, acces, className,
}: {
  bilan: QuizResult["erreurs"]
  cursus: number
  acces: boolean
  className?: string
}) {
  useI18n()
  const { lancer, enCours, echec } = useRefaireErreurs(cursus)
  if (!bilan || bilan.corrigees <= 0) return null
  const restantes = bilan.restantes ?? 0
  const vide = restantes === 0

  return (
    <section
      role="status"
      className={cn(
        "animate-quiz-bravo rounded-2xl border px-4 py-3.5",
        vide ? "border-gold/50 bg-gold/15" : "border-success/40 bg-success/5",
        className,
      )}
    >
      <div className="flex items-start gap-3">
        {vide ? (
          <Trophy className="mt-0.5 size-6 shrink-0 text-gold-text" aria-hidden="true" />
        ) : (
          <CheckCircle2 className="mt-0.5 size-6 shrink-0 text-success" aria-hidden="true" />
        )}
        <div className="min-w-0 flex-1">
          <p className="font-display text-lg font-semibold">{tn("erreurs.corrigees", bilan.corrigees)}</p>
          <p className="text-sm text-muted-foreground">{vide ? t("erreurs.liste_vide") : tn("erreurs.restantes", restantes)}</p>
        </div>
      </div>
      {!vide && (
        <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2">
          {acces && (
            <Button type="button" className="min-h-11 rounded-full" disabled={enCours !== null} onClick={() => lancer()}>
              {enCours !== null ? <Loader2 className="size-4 animate-spin" aria-hidden="true" /> : <ArrowRight className="size-4" aria-hidden="true" />}
              {t("erreurs.suivantes")}
            </Button>
          )}
          <Link to="/erreurs" className="text-sm font-medium text-primary underline-offset-2 hover:underline">
            {t("erreurs.voir")}
          </Link>
        </div>
      )}
      {echec && (
        <p role="alert" className="mt-2 text-sm text-destructive">
          {echec.message}
        </p>
      )}
    </section>
  )
}
