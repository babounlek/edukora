import { useEffect, useRef, useState } from "react"
import { Download, Loader2 } from "lucide-react"

import { downloadQuizCorrigePdf, downloadQuizSujetPdf, getQuizFichePdfStatus, requestQuizFichePdf } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { QuizFichePdfStatus } from "@/api/types"
import { Button } from "@/components/ui/button"

// Même intervalle que FichesPage.tsx (POLL_INTERVAL_MS), même raison : la génération
// tourne hors ligne (voir quiz.pdf, jamais dans le thread de la requête HTTP), il faut
// donc interroger le statut jusqu'à ce qu'elle soit prête.
const FICHE_PDF_POLL_INTERVAL_MS = 2500

/**
 * Boutons de téléchargement Fiche/Correction d'une QuizSession - partagés entre
 * QuizSessionPage (pendant le quiz) et QuizResultPage (une fois terminé) : le tirage des
 * questions est figé dès la création de la session (voir QuizSession/QuizQuestion), donc
 * les deux PDF ont exactement le même sens à tout moment de la session, pas seulement à
 * la fin. Statut initialisé depuis le serveur au montage (pas seulement après un clic) :
 * sans ça, arriver sur l'écran de résultat après avoir déjà généré les PDF pendant le
 * quiz obligerait à recliquer "Télécharger" pour rien.
 */
export function QuizFichePdfButtons({ sessionId }: { sessionId: number }) {
  const [statut, setStatut] = useState<QuizFichePdfStatus["statut"] | null>(null)
  const [error, setError] = useState("")
  const pollRef = useRef<number | null>(null)

  function poll() {
    if (pollRef.current) window.clearInterval(pollRef.current)
    pollRef.current = window.setInterval(async () => {
      try {
        const status = await getQuizFichePdfStatus(sessionId)
        if (status.statut !== "EN_COURS") {
          if (pollRef.current) window.clearInterval(pollRef.current)
          setStatut(status.statut)
        }
      } catch {
        // une erreur ponctuelle du réseau ne doit pas interrompre l'attente
      }
    }, FICHE_PDF_POLL_INTERVAL_MS)
  }

  useEffect(() => {
    getQuizFichePdfStatus(sessionId)
      .then((status) => {
        setStatut(status.statut)
        if (status.statut === "EN_COURS") poll()
      })
      .catch(() => {
        // pas grave : le bouton "Télécharger" reste disponible pour relancer
      })
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId])

  async function handleGenerer() {
    setError("")
    try {
      const status = await requestQuizFichePdf(sessionId)
      setStatut(status.statut)
      if (status.statut === "EN_COURS") poll()
    } catch (err) {
      setStatut(null)
      setError(err instanceof ApiError ? err.message : "Impossible de générer la fiche pour le moment.")
    }
  }

  async function handleTelechargerSujet() {
    try {
      await downloadQuizSujetPdf(sessionId)
    } catch {
      setError("Impossible d'ouvrir la fiche pour le moment.")
    }
  }

  async function handleTelechargerCorrige() {
    try {
      await downloadQuizCorrigePdf(sessionId)
    } catch {
      setError("Impossible d'ouvrir la correction pour le moment.")
    }
  }

  return (
    <div className="flex flex-col items-center gap-2 text-center">
      {statut === "PRETE" ? (
        <div className="flex flex-col gap-2 sm:flex-row">
          <Button variant="outline" size="sm" onClick={handleTelechargerSujet}>
            <Download className="mr-2 size-4" />
            1. Fiche
          </Button>
          <Button variant="outline" size="sm" onClick={handleTelechargerCorrige}>
            <Download className="mr-2 size-4" />
            2. Correction
          </Button>
        </div>
      ) : (
        <Button variant="outline" size="sm" onClick={handleGenerer} disabled={statut === "EN_COURS"}>
          {statut === "EN_COURS" ? (
            <>
              <Loader2 className="mr-2 size-4 animate-spin" />
              Préparation des fiches...
            </>
          ) : (
            <>
              <Download className="mr-2 size-4" />
              Télécharger la fiche PDF
            </>
          )}
        </Button>
      )}
      {statut === "ECHEC" && <p className="text-sm text-destructive">La génération a échoué, réessaie dans un instant.</p>}
      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  )
}
