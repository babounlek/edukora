import { creerCompteInvite, startQuizEssai, startQuizSession } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import { trackEvent } from "@/lib/analytics"
import { memoriserDefi, type Defi } from "@/lib/defiEssai"
import { aUnEssaiSansCompte } from "@/lib/invite"
import { memoriserEssai } from "@/lib/quizEssai"

/**
 * Lancer un quiz GRATUIT (un thème offert) et dire où aller. Une seule porte pour la liste des essais, le lien partagé et
 * « Refaire » :
 *
 * - un connecté joue une vraie séance (historique, reprise, points) : le thème est gratuit, ou son examen est abonné ;
 * - un visiteur reçoit d'abord un compte INVITÉ (voir lib/invite.ts) puis joue la même vraie séance, qu'il garde en
 *   créant son compte ;
 * - si l'invité ne peut pas être ouvert (plafond atteint, stockage ou réseau en panne) ou que son jeton est refusé, on
 *   retombe sur l'essai sans enregistrement (voir lib/quizEssai.ts) : le quiz se joue, comme avant.
 *
 * `defi` : le score à battre d'un lien de défi ; il suit CETTE séance et pas les suivantes (voir lib/defiEssai).
 */
export async function lancerQuizGratuit(
  p: { cursus: number; subject: number; theme: number; n?: number; connecte: boolean; source: string; defi?: Defi | null },
): Promise<string> {
  const n = p.n ?? 10

  async function essai(): Promise<string> {
    const session = await startQuizEssai({ cursus: p.cursus, subject: p.subject, theme: p.theme, n })
    memoriserEssai(session)
    memoriserDefi(p.defi ?? null)
    trackEvent("quiz_started", { cursus_id: p.cursus, mode: "PRATIQUE", source: p.source })
    return "/quiz/essai"
  }

  if (!p.connecte && !aUnEssaiSansCompte()) {
    try {
      await creerCompteInvite()
    } catch {
      return essai()
    }
  }

  try {
    const session = await startQuizSession({ cursus: p.cursus, subject: p.subject, theme: p.theme, mode: "PRATIQUE", n })
    memoriserDefi(p.defi ?? null, session.id)
    trackEvent("quiz_started", { cursus_id: p.cursus, mode: "PRATIQUE", source: p.source })
    return `/quiz/session/${session.id}`
  } catch (err) {
    // Jeton d'invité refusé (le client l'a déjà oublié) : l'essai reste possible. Tout autre refus (thème devenu payant...)
    // remonte tel quel, pour que l'écran le dise.
    if (!p.connecte && err instanceof ApiError && err.status === 401) return essai()
    throw err
  }
}
