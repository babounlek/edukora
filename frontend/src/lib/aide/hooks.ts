import { useQuery } from "@tanstack/react-query"

import { getAideArticle, getCodeAssistance, listAideArticles, listMyManualPayments } from "@/api/endpoints"
import { useAuth } from "@/context/AuthContext"
import { langueCourante, useI18n } from "@/lib/i18n"

/** La liste (sans corps) des articles, dans la langue de l'interface. Elle sert à chercher sans réseau une fois chargée. */
export function useArticlesAide(actif = true) {
  useI18n()
  const langue = langueCourante()
  return useQuery({
    queryKey: ["aide", "articles", langue],
    queryFn: () => listAideArticles(langue),
    enabled: actif,
    staleTime: 10 * 60_000,
  })
}

export function useArticleAide(slug: string | undefined) {
  useI18n()
  const langue = langueCourante()
  return useQuery({
    queryKey: ["aide", "article", slug, langue],
    queryFn: () => getAideArticle(slug as string, langue),
    enabled: !!slug,
    staleTime: 10 * 60_000,
    retry: false,
  })
}

/** Le code d'assistance, seulement pour un compte connecté (null sinon, ou pendant le chargement). */
export function useCodeAssistance(): string | null {
  const { isAuthenticated } = useAuth()
  const { data } = useQuery({
    queryKey: ["aide", "mon-code"],
    queryFn: getCodeAssistance,
    enabled: isAuthenticated,
    staleTime: Infinity,
    retry: false,
  })
  return isAuthenticated ? (data?.code ?? null) : null
}

/** Le paiement manuel le plus récent du compte connecté (null s'il n'en a pas ou hors connexion) : l'aide en montre l'état. */
export function useDernierPaiement() {
  const { isAuthenticated } = useAuth()
  return useQuery({
    queryKey: ["aide", "dernier-paiement"],
    queryFn: async () => {
      const paiements = await listMyManualPayments()
      return [...paiements].sort((a, b) => b.created_at.localeCompare(a.created_at))[0] ?? null
    },
    enabled: isAuthenticated,
    staleTime: 60_000,
    retry: false,
  })
}
