import type { QueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import type { EtatXp } from "@/api/types"
import { jouerRetour } from "@/lib/retours"
import { t } from "@/lib/i18n"

/**
 * Dit à l'élève ce que son geste vient de lui rapporter (une section de cours comprise, un exercice fait) : « J'ai
 * compris » et « Je l'ai fait » ne rapportaient rien à l'écran (test élève Guyguy), alors que le même geste dans un quiz fait
 * défiler des points. Sans effet quand rien n'est gagné - déjà compté, ou plafond du jour atteint : on ne promet jamais ce qui
 * n'est pas crédité.
 */
export function annoncerGain(queryClient: QueryClient, gagne: number | undefined, jour?: EtatXp) {
  if (!gagne || gagne <= 0) return
  toast.success(t("gl.partage_points", { n: gagne }), {
    description: jour ? (jour.atteint ? t("ligne.objectif_atteint") : t("ligne.points", { xp: jour.xp, objectif: jour.objectif })) : undefined,
  })
  jouerRetour("juste")
  // La ligne d'objectif de l'accueil lit le plan du jour.
  queryClient.invalidateQueries({ queryKey: ["plan-du-jour"] })
}
