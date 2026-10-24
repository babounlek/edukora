import { t, tn } from "@/lib/i18n"

/**
 * Les erreurs d'envoi d'un code de connexion (SMS ou e-mail) arrivent du serveur avec un code machine et, quand
 * on le sait, le nombre de secondes à attendre (voir backend/users/erreurs_envoi.py). La phrase s'écrit ICI, dans la
 * langue de la page : le serveur ne la connaît pas, et répondait en français sur une page anglaise, sans durée
 * (test élève 2026-10-24).
 */
export const CODE_RENVOI_TROP_TOT = "code_renvoi_trop_tot"
export const CODE_TROP_DE_DEMANDES = "code_trop_de_demandes"
export const CODE_ENVOI_INDISPONIBLE = "envoi_indisponible"

/** « 45 secondes », « 3 minutes », « 1 heure » : l'unité la plus lisible pour la durée donnée. */
export function dureeAttente(secondes: number): string {
  const s = Math.max(1, Math.ceil(secondes))
  if (s < 90) return tn("envoi.secondes", s)
  const minutes = Math.ceil(s / 60)
  if (minutes < 90) return tn("envoi.minutes", minutes)
  return tn("envoi.heures", Math.ceil(minutes / 60))
}

/** La phrase d'une erreur d'envoi de code, ou null si le code machine n'en est pas une. */
export function messageEnvoiCode(code: string | null, retryAfter: number | null): string | null {
  const avecDuree = retryAfter !== null && retryAfter > 0
  switch (code) {
    case CODE_RENVOI_TROP_TOT:
      return avecDuree ? t("envoi.renvoi_trop_tot", { duree: dureeAttente(retryAfter) }) : t("envoi.renvoi_trop_tot_sans")
    case CODE_TROP_DE_DEMANDES:
      return avecDuree ? t("envoi.trop_de_demandes", { duree: dureeAttente(retryAfter) }) : t("envoi.trop_de_demandes_sans")
    case CODE_ENVOI_INDISPONIBLE:
      return avecDuree ? t("envoi.indisponible", { duree: dureeAttente(retryAfter) }) : t("envoi.indisponible_sans")
    default:
      return null
  }
}
