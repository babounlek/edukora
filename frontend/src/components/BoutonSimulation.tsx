import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { toast } from "sonner"
import { Loader2, Timer } from "lucide-react"

import { startSimulation } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import { Button } from "@/components/ui/button"
import { trackEvent } from "@/lib/analytics"

/**
 * « Passer cette épreuve en conditions d'examen » : ouvre une simulation de l'annale - chrono,
 * corrigé masqué jusqu'à la fin, note sur le barème réel, rapport de fin. Le choix du mode
 * (conditions réelles, papier, entraînement libre) se fait sur l'écran de briefing qui suit.
 */
export function BoutonSimulation({ epreuveId }: { epreuveId: number }) {
  const navigate = useNavigate()
  const [enCours, setEnCours] = useState(false)

  async function lancer() {
    setEnCours(true)
    try {
      const simulation = await startSimulation(epreuveId)
      trackEvent("simulation_demarree", { epreuve_id: epreuveId })
      navigate(`/simulation/${simulation.id}`)
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Impossible de lancer la simulation. Réessaie.")
      setEnCours(false)
    }
  }

  return (
    <Button variant="outline" size="lg" className="h-12 rounded-full" disabled={enCours} onClick={lancer}>
      {enCours ? <Loader2 className="animate-spin" /> : <Timer />}
      Passer en conditions d'examen
    </Button>
  )
}
