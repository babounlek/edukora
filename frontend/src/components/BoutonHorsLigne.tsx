import { useCallback, useEffect, useState } from "react"
import { toast } from "sonner"
import { CheckCircle2, Download, Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  estDisponibleHorsLigne, telechargerPourLireHorsLigne, useEnLigne, type TypeContenu,
} from "@/lib/pwa"

/**
 * « Lire sans réseau » : indique si ce document est déjà lisible hors connexion et permet
 * de le préparer. Lire un document suffit à le rendre disponible (le service worker garde
 * la réponse) - le bouton sert à l'avoir AVANT de perdre le réseau, pas à ouvrir une
 * seconde fois ce qu'on lit déjà.
 */
export function BoutonHorsLigne({ type, slug }: { type: TypeContenu; slug: string }) {
  const enLigne = useEnLigne()
  const [disponible, setDisponible] = useState<boolean | null>(null)
  const [enCours, setEnCours] = useState(false)

  const verifier = useCallback(() => {
    estDisponibleHorsLigne(type, slug).then(setDisponible)
  }, [type, slug])

  useEffect(() => {
    // Un délai : la page vient de charger le contenu, le cache s'écrit juste après la réponse.
    const t = setTimeout(verifier, 800)
    return () => clearTimeout(t)
  }, [verifier])

  // Pas de service worker (navigateur ancien, économie de données) : rien à proposer.
  if (typeof caches === "undefined" || !("serviceWorker" in navigator)) return null

  async function telecharger() {
    setEnCours(true)
    try {
      await telechargerPourLireHorsLigne(type, slug)
      await new Promise((resolve) => setTimeout(resolve, 300))
      const ok = await estDisponibleHorsLigne(type, slug)
      setDisponible(ok)
      if (ok) toast.success("Disponible hors connexion")
      else toast.error("Impossible de le garder hors connexion sur cet appareil.")
    } catch {
      toast.error("Téléchargement impossible pour le moment. Réessaie avec du réseau.")
    } finally {
      setEnCours(false)
    }
  }

  if (disponible) {
    return (
      <span className="inline-flex items-center gap-1.5 text-sm text-success">
        <CheckCircle2 className="size-4" aria-hidden="true" />
        Disponible hors connexion
      </span>
    )
  }
  if (!enLigne || disponible === null) return null

  return (
    <Button variant="outline" size="sm" className="rounded-full" disabled={enCours} onClick={telecharger}>
      {enCours ? <Loader2 className="animate-spin" /> : <Download />}
      {enCours ? "Téléchargement..." : "Lire sans réseau"}
    </Button>
  )
}
