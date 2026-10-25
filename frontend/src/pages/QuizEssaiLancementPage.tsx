import { useEffect, useState } from "react"
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom"

import { startQuizEssai } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import { Skeleton } from "@/components/ui/skeleton"
import { lireDefiDepuis, memoriserDefi } from "@/lib/defiEssai"
import { memoriserEssai } from "@/lib/quizEssai"
import { trackEvent } from "@/lib/analytics"
import { useSeo } from "@/lib/seo"
import { t, useI18n } from "@/lib/i18n"

/**
 * Le lien d'un quiz gratuit partagé (/quiz/essai/<cursus>/<matière>/<thème>) : lance cet essai-là et
 * ouvre le lecteur, sans passer par la liste. Un lien périmé (le thème n'est plus gratuit, un
 * identifiant inventé) ramène à la liste avec une phrase, jamais à une page blanche.
 */
export function QuizEssaiLancementPage() {
  useI18n()
  useSeo({ title: t("essai.seo_lancement") })
  const { cursus, subject, theme } = useParams<{ cursus: string; subject: string; theme: string }>()
  const navigate = useNavigate()
  const [recherche] = useSearchParams()
  const defi = lireDefiDepuis(recherche.toString())
  const [erreur, setErreur] = useState("")

  useEffect(() => {
    const ids = [cursus, subject, theme].map(Number)
    if (ids.some((n) => !Number.isInteger(n) || n <= 0)) {
      setErreur(t("essai.lien_invalide"))
      return
    }
    let annule = false
    // Le lien d'un défi (« ?defi=4-5 ») : le score à battre suit le visiteur jusqu'à son résultat ; un lien sans défi efface un défi d'avant.
    memoriserDefi(defi)
    startQuizEssai({ cursus: ids[0], subject: ids[1], theme: ids[2], n: 10 })
      .then((session) => {
        if (annule) return
        memoriserEssai(session)
        trackEvent("quiz_started", { cursus_id: ids[0], mode: "PRATIQUE", source: "essai_partage" })
        navigate("/quiz/essai", { replace: true })
      })
      .catch((err) => {
        if (annule) return
        setErreur(
          err instanceof ApiError && (err.status === 403 || err.status === 404)
            ? t("essai.plus_gratuit")
            : t("essai.lancement_erreur"),
        )
      })
    return () => {
      annule = true
    }
  }, [cursus, subject, theme, navigate, defi?.reussies, defi?.total])

  if (erreur) {
    return (
      <div className="mx-auto max-w-xl px-4 py-12 text-center">
        <p className="text-destructive">{erreur}</p>
        <Link to="/quiz" className="mt-3 inline-block text-sm font-medium text-primary underline-offset-4 hover:underline">
          {t("essai.voir_gratuits")}
        </Link>
      </div>
    )
  }
  return (
    <div className="mx-auto max-w-xl px-4 py-12">
      <Skeleton className="mb-3 h-6 w-2/3" />
      <Skeleton className="h-4 w-full" />
    </div>
  )
}
