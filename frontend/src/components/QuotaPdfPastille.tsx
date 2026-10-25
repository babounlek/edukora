import { Check } from "lucide-react"

import { QuotaPdfInfo } from "@/components/QuotaPdfInfo"
import { messageRestants } from "@/lib/quotaPdf"
import { useQuotaPdf } from "@/lib/useQuotaPdf"
import { t, tn, useI18n } from "@/lib/i18n"
import { cn } from "@/lib/utils"

/**
 * Le compteur de téléchargements PDF d'un bouton, en pastille DANS le bouton (« 2 restants », « Déjà téléchargé »),
 * au lieu d'une note de deux lignes dessous qui décale la rangée d'actions. Le serveur décide de tout : tant que le
 * compteur n'est pas là (chargement, réseau coupé) ou si les quotas sont suspendus, il n'y a ni pastille ni phrase.
 *
 * `phrase` : le texte complet, pour l'infobulle du bouton (`title`) ; `epuise` : le quota est atteint, la pastille
 * s'efface et `<QuotaPdfEpuise>` dit pourquoi, sous la rangée.
 */
export function useQuotaPdfBouton(doc: string) {
  const quota = useQuotaPdf(doc)
  const dejaPris = Boolean(quota?.gratuits.includes(doc))
  const epuise = Boolean(quota) && (quota?.restant ?? 0) <= 0 && !dejaPris
  const phrase = !quota || epuise ? undefined : dejaPris ? t("qpdf.deja") : messageRestants(quota.restant)
  return { quota, dejaPris, epuise, phrase }
}

export type EtatQuotaPdfBouton = ReturnType<typeof useQuotaPdfBouton>

/** À poser à la fin des enfants du `<Button>`. */
export function PastilleQuotaPdf({ etat }: { etat: EtatQuotaPdfBouton }) {
  useI18n()
  const { quota, dejaPris, epuise } = etat
  if (!quota || epuise) return null
  return (
    <span
      className={cn(
        "ml-0.5 inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium",
        dejaPris ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground",
      )}
    >
      {dejaPris ? (
        <>
          <Check className="size-3" strokeWidth={3} aria-hidden="true" />
          {t("qpdf.pastille_deja")}
        </>
      ) : (
        tn("qpdf.pastille_restants", quota.restant)
      )}
    </span>
  )
}

/** À poser à côté du bouton : la phrase complète pour les lecteurs d'écran, ou le message d'un quota épuisé. */
export function QuotaPdfComplement({ doc, etat }: { doc: string; etat: EtatQuotaPdfBouton }) {
  if (etat.epuise) return <QuotaPdfInfo doc={doc} className="text-xs" />
  if (!etat.phrase) return null
  return <span className="sr-only" role="status" aria-live="polite">{etat.phrase}</span>
}
