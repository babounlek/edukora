import { useEffect, useRef, useState } from "react"
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom"

import { ApiError } from "@/api/client"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/context/AuthContext"
import { lireDefiDepuis } from "@/lib/defiEssai"
import { lancerQuizGratuit } from "@/lib/quizGratuit"
import { useSeo } from "@/lib/seo"
import { t, useI18n } from "@/lib/i18n"

/**
 * Le lien d'un quiz gratuit partagé (/quiz/essai/<cursus>/<matière>/<thème>) : lance ce quiz-là et
 * ouvre le lecteur, sans passer par la liste. Un lien périmé (le thème n'est plus gratuit, un
 * identifiant inventé) ramène à la liste avec une phrase, jamais à une page blanche.
 *
 * Une vraie séance pour tous (voir lib/quizGratuit) : un visiteur reçoit un compte invité, un connecté joue sur son profil
 * (ses points comptent), l'essai sans enregistrement ne sert plus que de repli.
 */
export function QuizEssaiLancementPage() {
  useI18n()
  useSeo({ title: t("essai.seo_lancement") })
  const { cursus, subject, theme } = useParams<{ cursus: string; subject: string; theme: string }>()
  const navigate = useNavigate()
  const [recherche] = useSearchParams()
  const { isAuthenticated, isLoading } = useAuth()
  const defi = lireDefiDepuis(recherche.toString())
  const [erreur, setErreur] = useState("")
  // Ce lien ne lance qu'UNE séance : le double passage des effets (mode strict) créerait sinon deux comptes invités et
  // deux séances. `monte` dit si la page est encore là quand la réponse arrive.
  const lance = useRef<string | null>(null)
  const monte = useRef(true)
  useEffect(() => {
    monte.current = true
    return () => {
      monte.current = false
    }
  }, [])

  useEffect(() => {
    // On attend de savoir si la personne est connectée : un connecté ne doit pas recevoir de compte invité.
    if (isLoading) return
    const ids = [cursus, subject, theme].map(Number)
    if (ids.some((n) => !Number.isInteger(n) || n <= 0)) {
      setErreur(t("essai.lien_invalide"))
      return
    }
    const cle = `${ids.join("-")}:${defi?.reussies ?? ""}-${defi?.total ?? ""}:${isAuthenticated}`
    if (lance.current === cle) return
    lance.current = cle
    // Le lien d'un défi (« ?defi=4-5 ») : le score à battre suit la séance jusqu'à son résultat ; un lien sans défi efface un défi d'avant.
    lancerQuizGratuit({
      cursus: ids[0], subject: ids[1], theme: ids[2], connecte: isAuthenticated, source: "essai_partage", defi,
    })
      .then((chemin) => {
        if (monte.current) navigate(chemin, { replace: true })
      })
      .catch((err) => {
        if (!monte.current) return
        setErreur(
          err instanceof ApiError && (err.status === 403 || err.status === 404)
            ? t("essai.plus_gratuit")
            : t("essai.lancement_erreur"),
        )
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cursus, subject, theme, navigate, isLoading, isAuthenticated, defi?.reussies, defi?.total])

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
