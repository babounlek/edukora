import { Link } from "react-router-dom"
import { ArrowRight, CalendarClock } from "lucide-react"

import type { Accueil } from "@/api/types"
import { BoutonParents } from "@/components/BoutonParents"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/context/AuthContext"
import { trackEvent } from "@/lib/analytics"
import { useCursusAbonnes } from "@/lib/changerCursusPrepare"
import { libelleCursus } from "@/lib/cursus"
import { maintenantServeur } from "@/lib/horlogeServeur"
import { langueCourante, localeCourante, t, tn, useI18n } from "@/lib/i18n"

/** À partir de combien de jours avant sa fin l'accès s'annonce sur l'accueil. */
export const JOURS_ANNONCE_FIN = 7

/** Jours pleins entre aujourd'hui et le jour où l'accès se termine, en dates locales : 0 le jour même. */
export function joursAvantFin(expiresAt: string, maintenant: number): number {
  const fin = new Date(expiresAt)
  const jour = (d: Date) => Date.UTC(d.getFullYear(), d.getMonth(), d.getDate())
  return Math.round((jour(fin) - jour(new Date(maintenant))) / 86_400_000)
}

/**
 * « Ton accès se termine le 13 décembre » : la fin de l'abonnement, annoncée sur l'accueil une semaine avant.
 *
 * L'abonnement se paie au mois, sans prélèvement : chaque fin de période est une décision à reprendre, et la date
 * n'était écrite que dans le menu du compte (audit des accueils, 2026-11-21, A1). L'élève la découvrait le lendemain,
 * devant une séance fermée.
 *
 * Sobre, jamais alarmante : ni rouge, ni compte à rebours, ni « plus que N jours ». Une date, ce que l'élève a
 * construit (des faits déjà à l'écran plus bas), et les deux gestes possibles : prolonger - le lien mène droit au bon
 * profil et au bon examen - ou le montrer à ses parents, qui sont souvent ceux qui paient. Le compte reçoit aussi un
 * e-mail trois jours avant et le jour même (voir relances.fin_abonnement côté serveur).
 *
 * Placée SOUS la carte de séance : elle ne repousse jamais « Commencer ».
 */
export function FinAccesProche({ accueil }: { accueil: Accueil }) {
  useI18n()
  const { user } = useAuth()
  const abonnements = useCursusAbonnes()
  const abonnement = abonnements.find(
    (sub) => sub.profil.id === user?.profil_actif?.id && sub.cursus.id === user?.cursus_prepare?.id,
  )
  if (!abonnement) return null
  const jours = joursAvantFin(abonnement.expires_at, maintenantServeur())
  if (jours < 0 || jours > JOURS_ANNONCE_FIN) return null

  const date = new Date(abonnement.expires_at).toLocaleDateString(localeCourante(), { day: "numeric", month: "long" })
  const somme = (cle: "en_revision" | "maitrises") => accueil.resume.reduce((total, matiere) => total + matiere[cle], 0)
  const maitrises = somme("maitrises")
  const enRevision = somme("en_revision")
  const construit = [
    maitrises > 0 ? tn("decouverte.attend_maitrises", maitrises) : null,
    enRevision > 0 ? tn("decouverte.attend_revision", enRevision) : null,
  ].filter((element): element is string => element !== null)

  return (
    <section className="mx-auto max-w-5xl px-4 pt-6 sm:px-6" aria-label={t("acces.fin_aria")}>
      <div className="flex flex-col gap-3 rounded-2xl border border-border bg-card px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          <p className="flex items-center gap-2 font-display font-medium">
            <CalendarClock className="size-4 shrink-0 text-primary" aria-hidden="true" />
            {jours === 0 ? t("acces.fin_aujourdhui") : t("acces.fin_le", { date })}
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            {construit.length > 0
              ? t("acces.fin_construit", {
                  liste: new Intl.ListFormat(langueCourante(), { style: "long", type: "conjunction" }).format(construit),
                })
              : t("acces.fin_texte")}
          </p>
        </div>
        <div className="flex shrink-0 flex-wrap items-center gap-2">
          <Button asChild size="sm" className="min-h-11">
            <Link
              to={`/abonnement?cursus=${abonnement.cursus.id}&profil=${abonnement.profil.id}`}
              onClick={() => trackEvent("accueil_bouton_clic", { cible: "prolonger" })}
            >
              {t("acces.prolonger")}
              <ArrowRight className="size-4" />
            </Link>
          </Button>
          {/* Le message tout prêt dit la date : « Pour continuer après le 13 décembre, il faut l'abonnement. » */}
          <BoutonParents
            examen={libelleCursus(abonnement.cursus)}
            contenu={t("acces.parents_contenu", { date })}
            size="sm"
            className="min-h-11"
          />
        </div>
      </div>
    </section>
  )
}
