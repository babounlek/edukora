import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { Play, X } from "lucide-react"

import { getQuizSession } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import { lireQuizEnCours, oublierQuizEnCours, useCleQuizEnCours } from "@/lib/quizEnCours"

/**
 * « Reprendre mon quiz » : la séance commencée et pas terminée passe avant d'en lancer une autre.
 * Rien ne s'affiche s'il n'y en a pas, si elle est déjà rendue, ou si le serveur ne la connaît plus.
 */
export function ReprendreQuiz({ className, enveloppe = false }: { className?: string; enveloppe?: boolean }) {
  const cle = useCleQuizEnCours()
  // Relit le stockage quand l'élève abandonne (le stockage seul ne déclenche aucun rendu).
  const [, setVersion] = useState(0)
  const id = cle ? lireQuizEnCours(cle) : null

  const { data: session, error } = useQuery({
    queryKey: ["quiz-en-cours", id],
    queryFn: () => getQuizSession(id as number),
    enabled: id !== null,
    // Une séance finie dans un autre onglet ne doit plus être proposée.
    staleTime: 0,
    retry: false,
  })

  const introuvable = error instanceof ApiError && (error.status === 404 || error.status === 403)
  const terminee = Boolean(session?.completed_at)
  useEffect(() => {
    if (cle && id !== null && (terminee || introuvable)) oublierQuizEnCours(cle, id)
  }, [cle, id, terminee, introuvable])

  if (!cle || id === null || !session || terminee) return null

  const total = session.total_questions || session.questions.length
  const repondues = session.questions.filter((q) => q.reponse).length
  const aTerminer = repondues >= total
  const nom = session.mode === "DIAGNOSTIC" ? "Test de niveau" : "Quiz"

  const carte = (
    <div
      className={
        "flex items-center gap-2 rounded-2xl border border-primary/40 bg-primary/5 pr-2 transition-colors hover:border-primary " +
        (className ?? "")
      }
    >
      <Link
        to={`/quiz/session/${session.id}`}
        className="group flex min-h-14 min-w-0 flex-1 items-center gap-3 px-5 py-3.5"
      >
        <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary/15 text-primary">
          <Play className="size-4" aria-hidden="true" />
        </span>
        <span className="min-w-0 flex-1">
          <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">
            {nom} en cours · {repondues} / {total} répondues
          </span>
          <span className="block truncate text-sm font-medium">{session.cursus_display}</span>
        </span>
        <span className="shrink-0 text-sm font-medium text-primary">{aTerminer ? "Terminer" : "Reprendre"}</span>
      </Link>
      <button
        type="button"
        onClick={() => {
          oublierQuizEnCours(cle)
          setVersion((v) => v + 1)
        }}
        aria-label="Ne plus proposer de reprendre ce quiz"
        title="Ne plus proposer"
        className="flex size-11 shrink-0 items-center justify-center rounded-full text-muted-foreground hover:bg-accent hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none"
      >
        <X className="size-4" aria-hidden="true" />
      </button>
    </div>
  )

  // Même gabarit que la reprise d'une épreuve inédite sur l'accueil.
  return enveloppe ? <section className="mx-auto max-w-5xl px-4 pt-6 sm:px-6">{carte}</section> : carte
}
