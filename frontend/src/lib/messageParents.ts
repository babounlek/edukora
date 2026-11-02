import type { CampagneEnCours } from "@/api/types"
import { dateLimiteCampagne } from "@/lib/campagne"
import { t } from "@/lib/i18n"
import { SITE_NAME } from "@/lib/site"
import { PRIX_ABONNEMENT_FCFA } from "@/lib/tarifs"
import { formatAmount } from "@/lib/utils"

export interface ContexteMessageParents {
  /** L'examen préparé (« BEPC »), quand l'écran le sait avec certitude ; sinon « mon examen ». */
  examen?: string
  /** Ce que l'élève veut faire et ne peut pas : un morceau de phrase déjà traduit (« lire le corrigé de SVT BEPC 2025 »). */
  contenu?: string
  /** La campagne ouverte : son prix remplace le prix de référence, avec la date limite. */
  campagne?: CampagneEnCours | null
}

/**
 * Le message qu'un élève envoie à ses parents depuis un mur payant (sans le lien, ajouté au partage). Il est écrit pour quelqu'un
 * qui ne connaît pas le site et qui paie : ce que l'enfant veut, ce que l'abonnement ouvre, le montant en toutes lettres, le moyen
 * de paiement et l'absence de prélèvement. Rien n'est promis que /tarifs ne dise pas : le prix vient de la campagne ou de la constante
 * partagée, jamais d'un nombre recopié ici.
 */
export function messageParents({ examen, contenu, campagne }: ContexteMessageParents): string {
  const morceaux = [
    examen ? t("parents.intro_examen", { examen, site: SITE_NAME }) : t("parents.intro", { site: SITE_NAME }),
    contenu ? t("parents.besoin_contenu", { contenu }) : t("parents.besoin"),
    t("parents.donne"),
    campagne
      ? t("parents.prix_promo", {
          prix: formatAmount(campagne.prix),
          ref: formatAmount(campagne.prix_reference),
          date: dateLimiteCampagne(campagne.fin),
        })
      : t("parents.prix", { prix: formatAmount(PRIX_ABONNEMENT_FCFA) }),
    t("parents.paiement"),
    t("parents.fin"),
  ]
  return morceaux.join(" ")
}
