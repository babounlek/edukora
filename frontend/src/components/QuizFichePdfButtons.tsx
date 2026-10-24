import { useEffect, useRef, useState } from "react"
import { Download, Loader2 } from "lucide-react"

import { downloadQuizCorrigePdf, downloadQuizSujetPdf, getQuizFichePdfStatus, requestQuizFichePdf } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { QuizFichePdfStatus } from "@/api/types"
import { Button } from "@/components/ui/button"
import { PastilleQuotaPdf, QuotaPdfComplement, useQuotaPdfBouton } from "@/components/QuotaPdfPastille"
import { t, useI18n } from "@/lib/i18n"

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
/**
 * Les deux boutons une fois les PDF prêts. Le compteur de chaque bouton est une pastille DANS le bouton (« 12 restants »),
 * comme sur les autres boutons de PDF : une note en dessous élargissait la barre du bas, déjà serrée entre « Quitter le
 * quiz » et ces boutons, et la décalait. Le message d'un quota épuisé, lui, a besoin de place : il passe sous la rangée,
 * une seule fois (les deux PDF partagent le même quota).
 */
function BoutonsPdfPrets({ sessionId, onSujet, onCorrige }: { sessionId: number; onSujet: () => void; onCorrige: () => void }) {
  const docSujet = `quiz:${sessionId}:sujet`
  const docCorrige = `quiz:${sessionId}:corrige`
  const etatSujet = useQuotaPdfBouton(docSujet)
  const etatCorrige = useQuotaPdfBouton(docCorrige)

  return (
    <>
      <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:justify-end">
        <Button variant="outline" size="sm" onClick={onSujet} title={etatSujet.phrase}>
          <Download className="mr-2 size-4" />
          {t("gl.qpdf_fiche")}
          <PastilleQuotaPdf etat={etatSujet} />
        </Button>
        <Button variant="outline" size="sm" onClick={onCorrige} title={etatCorrige.phrase}>
          <Download className="mr-2 size-4" />
          {t("gl.qpdf_correction")}
          <PastilleQuotaPdf etat={etatCorrige} />
        </Button>
      </div>
      {etatSujet.epuise ? (
        <QuotaPdfComplement doc={docSujet} etat={etatSujet} />
      ) : (
        <>
          <QuotaPdfComplement doc={docSujet} etat={etatSujet} />
          <QuotaPdfComplement doc={docCorrige} etat={etatCorrige} />
        </>
      )}
    </>
  )
}

export function QuizFichePdfButtons({ sessionId }: { sessionId: number }) {
  useI18n()
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
      setError(err instanceof ApiError ? err.message : t("gl.qpdf_generer"))
    }
  }

  async function handleTelechargerSujet() {
    try {
      await downloadQuizSujetPdf(sessionId)
    } catch {
      setError(t("gl.pdf_fiche"))
    }
  }

  async function handleTelechargerCorrige() {
    try {
      await downloadQuizCorrigePdf(sessionId)
    } catch {
      setError(t("gl.pdf_correction"))
    }
  }

  return (
    <div className="flex flex-col items-center gap-2 text-center">
      {statut === "PRETE" ? (
        <BoutonsPdfPrets sessionId={sessionId} onSujet={handleTelechargerSujet} onCorrige={handleTelechargerCorrige} />
      ) : (
        <Button variant="outline" size="sm" onClick={handleGenerer} disabled={statut === "EN_COURS"}>
          {statut === "EN_COURS" ? (
            <>
              <Loader2 className="mr-2 size-4 animate-spin" />
              {t("gl.qpdf_preparation")}
            </>
          ) : (
            <>
              <Download className="mr-2 size-4" />
              {t("gl.qpdf_telecharger")}
            </>
          )}
        </Button>
      )}
      {statut === "ECHEC" && <p className="text-sm text-destructive">{t("gl.qpdf_echec")}</p>}
      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  )
}
