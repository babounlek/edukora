import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { Loader2, Timer } from "lucide-react"

import { listMySimulations, startSimulation } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import { Button } from "@/components/ui/button"
import { trackEvent } from "@/lib/analytics"
import { formatNote } from "@/lib/notation"
import { t, useI18n } from "@/lib/i18n"

/**
 * « Passer cette épreuve en conditions d'examen » : ouvre une simulation de l'annale - chrono,
 * corrigé masqué jusqu'à la fin, note sur le barème réel, rapport de fin. Le choix du mode
 * (conditions réelles, papier, entraînement libre) se fait sur l'écran de briefing qui suit.
 *
 * Le serveur rend la copie déjà ouverte quand il y en a une (chrono en cours, ou copie encore
 * vierge) au lieu d'en créer une de plus : voir simulations.views.start_simulation. La dernière
 * note obtenue sur cette épreuve tient dans une pastille du bouton : sans elle, rien sur la fiche
 * ne disait que l'élève l'avait déjà passée.
 */
export function BoutonSimulation({ epreuveId }: { epreuveId: number }) {
  useI18n()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [enCours, setEnCours] = useState(false)

  // Un échec de cette liste ne doit rien casser : le bouton reste utilisable, sans pastille.
  const { data: simulations } = useQuery({ queryKey: ["mes-simulations"], queryFn: listMySimulations, retry: false })
  // La liste arrive de la plus récente à la plus ancienne (voir simulations.views.mes_simulations).
  const derniere = simulations?.find(
    (s) => s.epreuve === epreuveId && s.submitted_at !== null && s.note_obtenue !== null && s.bareme_snapshot !== null,
  )

  async function lancer() {
    setEnCours(true)
    try {
      const simulation = await startSimulation(epreuveId)
      trackEvent("simulation_demarree", { epreuve_id: epreuveId })
      queryClient.invalidateQueries({ queryKey: ["mes-simulations"] })
      navigate(`/simulation/${simulation.id}`)
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : t("simulation.erreur"))
      setEnCours(false)
    }
  }

  return (
    <Button variant="outline" size="lg" className="h-12 rounded-full" disabled={enCours} onClick={lancer}>
      {enCours ? <Loader2 className="animate-spin" /> : <Timer />}
      {t("simulation.bouton")}
      {derniere && (
        <span className="rounded-full bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground">
          {t("simulation.derniere_note", { note: formatNote(derniere.note_obtenue, derniere.bareme_snapshot) })}
        </span>
      )}
    </Button>
  )
}
