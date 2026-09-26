import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, BookOpen, CalendarCheck, Check, Crown, ListChecks, type LucideIcon } from "lucide-react"

import { getPlanDuJour, getPriorites, startQuizSession } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import { Button } from "@/components/ui/button"
import { trackEvent } from "@/lib/analytics"

// Un diagnostic d'accueil : trois questions sur chacune des cinq matières qui pèsent le
// plus (voir quiz.services._selection_diagnostic_par_matiere).
const N_DIAGNOSTIC = 15
const DUREE_DIAGNOSTIC_MIN = 12

/**
 * L'écran juste après le paiement : la transition entre "j'ai payé" et "je commence".
 *
 * Une simple coche laissait l'élève devant un catalogue de plusieurs milliers d'épreuves
 * - le pire moment pour lui rendre la charge de choisir. On lui dit ce qu'il vient de
 * débloquer, puis on lui propose UNE chose : situer son niveau, ce qui alimente ses
 * priorités et sa première séance. Un élève qui a déjà un historique (renouvellement)
 * n'a rien à situer : il reprend directement sa séance.
 *
 * Le diagnostic reste facultatif ("Plus tard") : forcer un test à quelqu'un qui vient
 * de payer serait le contraire d'un accueil.
 */
export function BienvenueAbonne({
  cursusId, country, inclutInedit,
}: { cursusId: number; country: string; inclutInedit: boolean }) {
  const navigate = useNavigate()
  const [demarrage, setDemarrage] = useState(false)
  const [erreur, setErreur] = useState("")

  const { data: priorites, isLoading } = useQuery({
    queryKey: ["priorites", cursusId],
    queryFn: ({ signal }) => getPriorites(cursusId, signal),
    retry: false,
  })
  // Sans historique (ou sans réponse du serveur) : on propose le diagnostic. Le cas
  // d'un renouvellement est reconnu à ses réponses passées, jamais deviné.
  const renouvellement = Boolean(priorites?.a_deja_repondu)

  async function situerMonNiveau() {
    if (demarrage) return
    setDemarrage(true)
    setErreur("")
    try {
      // La séance du jour d'un nouvel élève EST ce calibrage : la demander d'abord la
      // crée, pour que le quiz s'y rattache et la valide en se terminant.
      await getPlanDuJour().catch(() => null)
      const session = await startQuizSession({ cursus: cursusId, mode: "DIAGNOSTIC", n: N_DIAGNOSTIC, seance: 1 })
      trackEvent("quiz_started", { cursus_id: cursusId, mode: "DIAGNOSTIC", source: "post_paiement" })
      navigate(`/quiz/session/${session.id}`)
    } catch (err) {
      setErreur(
        err instanceof ApiError
          ? err.message
          : "Impossible de démarrer le diagnostic pour l'instant. Tu peux commencer depuis ton espace.",
      )
      setDemarrage(false)
    }
  }

  return (
    <div className="flex flex-col items-center py-4 text-center">
      <span className="flex size-14 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg shadow-primary/25 ring-8 ring-primary/10">
        <Check className="size-7" strokeWidth={3} />
      </span>
      <h2 className="mt-5 font-display text-2xl font-semibold tracking-tight sm:text-3xl">
        {renouvellement ? "Ton accès est prolongé" : "Bienvenue, ton accès est ouvert"}
      </h2>
      <p className="mt-2 max-w-sm text-sm text-muted-foreground">
        {renouvellement
          ? "Ta progression est intacte : tu reprends exactement où tu t'étais arrêté."
          : "Voici ce que tu viens de débloquer."}
      </p>

      {!renouvellement && (
        <ul className="mt-5 flex w-full flex-col gap-2 text-left">
          <Debloque icone={BookOpen} texte="Tous les corrigés détaillés et les cours de méthode" />
          <Debloque icone={CalendarCheck} texte="Une séance du jour, choisie pour toi selon l'examen" />
          <Debloque icone={ListChecks} texte="Des quiz pour t'entraîner et suivre ta progression" />
          {inclutInedit && <Debloque icone={Crown} texte="Les épreuves inédites, chronométrées" />}
        </ul>
      )}

      <div className="mt-7 flex w-full flex-col items-center gap-3">
        {renouvellement ? (
          <Button asChild size="lg" className="h-12 rounded-full px-7 text-base shadow-lg shadow-primary/25">
            <Link to={`/${country}`}>
              Reprendre ma séance
              <ArrowRight className="size-4" />
            </Link>
          </Button>
        ) : (
          <>
            <Button
              size="lg"
              className="group h-12 rounded-full px-7 text-base shadow-lg shadow-primary/25 transition-all hover:-translate-y-0.5 hover:shadow-xl hover:shadow-primary/30"
              onClick={situerMonNiveau}
              disabled={demarrage || isLoading}
            >
              {demarrage ? "Je prépare tes questions…" : `Situer mon niveau · ${DUREE_DIAGNOSTIC_MIN} min`}
              {!demarrage && <ArrowRight className="size-4 transition-transform group-hover:translate-x-1" />}
            </Button>
            <p className="max-w-xs text-xs text-muted-foreground">
              {N_DIAGNOSTIC} questions sur tes matières principales. Ce n'est pas une note : ça sert à te proposer les
              bonnes séances.
            </p>
            <Link
              to={`/${country}`}
              className="text-xs text-muted-foreground underline underline-offset-4 hover:text-primary"
            >
              Plus tard, aller à mon espace
            </Link>
          </>
        )}
        {erreur && (
          <p role="alert" className="text-sm text-destructive">
            {erreur}
          </p>
        )}
      </div>
    </div>
  )
}

function Debloque({ icone: Icone, texte }: { icone: LucideIcon; texte: string }) {
  return (
    <li className="flex items-center gap-3 rounded-xl border border-border/70 bg-background/70 px-3.5 py-2.5 text-sm">
      <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
        <Icone className="size-4" />
      </span>
      {texte}
    </li>
  )
}
