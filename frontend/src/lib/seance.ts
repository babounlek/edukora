import type { QueryClient } from "@tanstack/react-query"

import { marquerEtapeOuverte } from "@/api/endpoints"
import type { EtapeSeance, PlanDuJour } from "@/api/types"
import { coursReaderPath, epreuveReaderPath } from "@/lib/countryPath"

/**
 * Où mène une étape. Le quiz part vers QuizStartPage avec son thème prérempli
 * (paramètres déjà supportés, voir QuizStartPage) plutôt que de créer la session ici :
 * une session créée par un clic qui n'aboutit pas laisserait une session vide en base.
 */
export function lienEtape(etape: EtapeSeance, country: string, plan: PlanDuJour): string {
  if (etape.type === "cours") return coursReaderPath(etape.slug)
  if (etape.type === "exercice") return epreuveReaderPath(country, etape.lesson_slug)
  const params = new URLSearchParams()
  if (plan.cursus) params.set("cursus", String(plan.cursus.id))
  if (plan.seance?.theme) params.set("theme", String(plan.seance.theme.id))
  // Fait remonter au serveur que ce quiz est l'étape finale de la séance : c'est lui
  // qui la clôt et en garde le score, l'élève n'a plus à déclarer ce qu'il vient de
  // faire sous les yeux de l'application.
  if (plan.seance) params.set("seance", String(plan.seance.id))
  // Le nombre de questions annoncé par l'étape, sinon la séance promet "5 questions"
  // et en sert 10 (le défaut de QuizStartPage) : un budget de 25 minutes qui déborde
  // dès la première séance, c'est la promesse du plan qui tombe.
  params.set("n", String(etape.n))
  const query = params.toString()
  return query ? `/quiz?${query}` : "/quiz"
}

/**
 * Coche l'étape tout de suite, sans attendre le serveur : l'élève quitte la page à ce
 * clic, et à son retour l'accueil doit déjà refléter ce qu'il vient de faire.
 * Fire-and-forget : un échec réseau ne doit jamais empêcher d'ouvrir l'étape. Le quiz
 * n'est pas concerné, il se lit sur sa session côté serveur.
 */
export function ouvrirEtapeDeSeance(queryClient: QueryClient, etape: EtapeSeance) {
  if (etape.type === "quiz") return
  queryClient.setQueryData<PlanDuJour>(["plan-du-jour"], (plan) =>
    plan?.seance
      ? {
          ...plan,
          seance: {
            ...plan.seance,
            etapes: plan.seance.etapes.map((e) => (e.cle === etape.cle ? { ...e, ouverte: true } : e)),
          },
        }
      : plan,
  )
  marquerEtapeOuverte(etape.cle).catch(() => {})
}
