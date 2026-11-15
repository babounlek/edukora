import { useEffect, useState } from "react"
import { toast } from "sonner"
import { CheckCircle2, Download, Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  activerLeHorsLigne, espaceUtilise, estThemeDisponibleHorsLigne, nombreElementsDuPaquet, retirerTheme, tailleLisible, telechargerTheme,
  useEnLigne, type PaquetTheme,
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
  const [espace, setEspace] = useState<number | null>(null)
  const total = nombreElementsDuPaquet(paquet)

  useEffect(() => {
    let vivant = true
    estThemeDisponibleHorsLigne(paquet).then((ok) => vivant && setDisponible(ok))
    return () => {
      vivant = false
    }
  }, [paquet])

  // La place occupée sur l'appareil, dite seulement quand un thème y est gardé : c'est là que l'élève se demande ce que ça pèse.
  useEffect(() => {
    if (!disponible) return
    let vivant = true
    espaceUtilise().then((e) => vivant && setEspace(e ? e.usage : null))
    return () => {
      vivant = false
    }
  }, [disponible])

  if (typeof caches === "undefined" || !("serviceWorker" in navigator)) return null

  async function retirer() {
    await retirerTheme(paquet)
    setDisponible(false)
    setEspace(null)
    toast.success(t("theme.hors_ligne_retire"))
  }

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
      <span className="inline-flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
        <span className="inline-flex items-center gap-1.5 text-success">
          <CheckCircle2 className="size-4" aria-hidden="true" />
          {t("theme.hors_ligne_dispo")}
        </span>
        <button type="button" onClick={retirer} className="min-h-11 text-xs font-medium text-muted-foreground underline-offset-2 hover:underline sm:min-h-0">
          {t("theme.hors_ligne_retirer")}
        </button>
        {espace !== null && (
          <span className="text-xs text-muted-foreground">{t("theme.hors_ligne_espace", { taille: tailleLisible(espace) })}</span>
        )}
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
