import { useEffect, useState } from "react"
import { toast } from "sonner"
import { CheckCircle2, Download, Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  activerLeHorsLigne, estThemeDisponibleHorsLigne, nombreElementsDuPaquet, telechargerTheme, useEnLigne, type PaquetTheme,
} from "@/lib/pwa"
import { t, tn, useI18n } from "@/lib/i18n"

/**
 * « Télécharger ce thème » (audit produit 2026-11-13, R21) : le cours du thème et ses exercices, gardés d'un coup pour un trajet
 * sans réseau. Contrairement à la lecture d'un seul document, il marche aussi en mode économie de données : l'élève le demande,
 * on ne le lui refuse plus. La taille n'est pas annoncée en octets (elle dépend du texte), mais le nombre d'éléments l'est.
 */
export function BoutonThemeHorsLigne({ paquet }: { paquet: PaquetTheme }) {
  useI18n()
  const enLigne = useEnLigne()
  const [disponible, setDisponible] = useState<boolean | null>(null)
  const [progres, setProgres] = useState<{ faits: number; total: number } | null>(null)
  const total = nombreElementsDuPaquet(paquet)

  useEffect(() => {
    let vivant = true
    estThemeDisponibleHorsLigne(paquet).then((ok) => vivant && setDisponible(ok))
    return () => {
      vivant = false
    }
  }, [paquet])

  if (typeof caches === "undefined" || !("serviceWorker" in navigator)) return null

  async function telecharger() {
    setProgres({ faits: 0, total })
    try {
      if (!(await activerLeHorsLigne())) {
        toast.error(t("theme.hors_ligne_impossible"))
        return
      }
      const echecs = await telechargerTheme(paquet, (faits, n) => setProgres({ faits, total: n }))
      if (echecs === 0) {
        setDisponible(true)
        toast.success(t("theme.hors_ligne_pret"))
      } else {
        toast.error(tn("theme.hors_ligne_partiel", echecs))
      }
    } catch {
      toast.error(t("ed.telechargement_erreur"))
    } finally {
      setProgres(null)
    }
  }

  if (disponible) {
    return (
      <span className="inline-flex items-center gap-1.5 text-sm text-success">
        <CheckCircle2 className="size-4" aria-hidden="true" />
        {t("theme.hors_ligne_dispo")}
      </span>
    )
  }
  if (!enLigne || total <= 1) return null // hors connexion, ou rien à garder que la liste elle-même

  return (
    <Button variant="outline" size="sm" className="rounded-full" disabled={progres !== null} onClick={telecharger}>
      {progres ? <Loader2 className="animate-spin" /> : <Download />}
      {progres ? t("theme.hors_ligne_progres", { faits: progres.faits, total: progres.total }) : tn("theme.hors_ligne_bouton", total)}
    </Button>
  )
}
