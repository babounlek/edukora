import { useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, Gift } from "lucide-react"

import { listQuizEssais, startQuizEssai } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { QuizEssai } from "@/api/types"
import { FiltreLigne, PastilleFiltre } from "@/components/FiltresCatalogue"
import { Button } from "@/components/ui/button"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { memoriserEssai } from "@/lib/quizEssai"
import { subjectIcon } from "@/lib/subjectIcon"
import { trackEvent } from "@/lib/analytics"
import { capitaliserTheme, cn } from "@/lib/utils"

/**
 * Les quiz gratuits, jouables SANS compte (voir quiz.essai côté backend) : un thème entier par
 * matière, au choix de l'examen préparé. Le visiteur voit tout de suite quoi essayer plutôt qu'un
 * mur « connecte-toi » - il goûte le quiz, puis voit ce qu'un abonnement ajoute (voir
 * QuizEssaiResultPage). Rien n'est affiché si aucun essai n'est ouvert.
 */
export function EssaisGratuitsQuiz({ cursusInitial }: { cursusInitial?: number | null }) {
  const navigate = useNavigate()
  const { data: essais } = useQuery({
    queryKey: ["quiz", "essais"],
    queryFn: ({ signal }) => listQuizEssais(signal),
    staleTime: 5 * 60_000,
  })
  const [choisi, setChoisi] = useState<number | null>(null)
  const [enCours, setEnCours] = useState<string | null>(null)
  const [erreur, setErreur] = useState("")

  const cursus = useMemo(() => {
    const vus = new Map<number, string>()
    for (const e of essais ?? []) if (!vus.has(e.cursus)) vus.set(e.cursus, e.cursus_display)
    return [...vus.entries()].map(([id, libelle]) => ({ id, libelle }))
  }, [essais])

  if (!essais || essais.length === 0) return null

  const actif = [choisi, cursusInitial].find((id) => id != null && cursus.some((c) => c.id === id)) ?? cursus[0].id
  const lignes = essais.filter((e) => e.cursus === actif)

  async function lancer(essai: QuizEssai) {
    const cle = `${essai.cursus}-${essai.subject}-${essai.theme}`
    if (enCours) return
    setEnCours(cle)
    setErreur("")
    try {
      const session = await startQuizEssai({ cursus: essai.cursus, subject: essai.subject, theme: essai.theme, n: 10 })
      memoriserEssai(session)
      trackEvent("quiz_started", { cursus_id: essai.cursus, mode: "PRATIQUE", source: "essai_anonyme" })
      navigate("/quiz/essai")
    } catch (err) {
      setErreur(err instanceof ApiError ? err.message : "Impossible de lancer cet essai. Réessaie dans un instant.")
      setEnCours(null)
    }
  }

  return (
    <section
      aria-labelledby="essais-gratuits-titre"
      className="mb-8 rounded-2xl border border-gold/40 bg-gradient-to-br from-gold/10 via-transparent to-transparent p-4 shadow-lg shadow-primary/5 sm:p-6"
    >
      <p id="essais-gratuits-titre" className="flex items-center gap-2 font-display text-lg font-semibold">
        <Gift className="size-5 text-gold-text" aria-hidden="true" />
        Essaie gratuitement, sans compte
      </p>
      <p className="text-sm text-muted-foreground">
        Un thème complet par matière, avec la correction de chaque question. Choisis ton examen, puis lance.
      </p>

      {cursus.length > 1 && (
        <FiltreLigne titre="Examen">
          {cursus.map((c) => (
            <PastilleFiltre key={c.id} actif={actif === c.id} onClick={() => setChoisi(c.id)}>
              {c.libelle}
            </PastilleFiltre>
          ))}
        </FiltreLigne>
      )}

      <ul className="mt-4 flex flex-col divide-y divide-border/60 overflow-hidden rounded-xl border border-border/70">
        {lignes.map((essai) => {
          const Icone = subjectIcon(essai.subject_code)
          const cle = `${essai.cursus}-${essai.subject}-${essai.theme}`
          return (
            <li key={cle} className="flex items-center justify-between gap-3 bg-card px-3.5 py-3">
              <span className="flex min-w-0 items-center gap-2.5">
                <span className={cn("flex size-8 shrink-0 items-center justify-center rounded-full", couleurMatiere(essai.subject_code).puce)}>
                  <Icone className="size-4" aria-hidden="true" />
                </span>
                <span className="min-w-0">
                  <span className="block truncate text-sm font-medium">{essai.subject_label}</span>
                  <span className="block truncate text-xs text-muted-foreground">
                    {capitaliserTheme(essai.theme_name)} · {essai.nb_questions} question{essai.nb_questions > 1 ? "s" : ""}
                  </span>
                </span>
              </span>
              <Button size="sm" disabled={enCours !== null} onClick={() => lancer(essai)} className="shrink-0 rounded-full">
                {enCours === cle ? "Préparation..." : "Essayer"}
                {enCours !== cle && <ArrowRight />}
              </Button>
            </li>
          )
        })}
      </ul>
      {erreur && (
        <p role="alert" className="mt-3 text-sm text-destructive">
          {erreur}
        </p>
      )}
    </section>
  )
}
