import { useState } from "react"
import { Check, Eye, RotateCcw } from "lucide-react"

import type { CarteRevision } from "@/api/types"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { Button } from "@/components/ui/button"
import { t, useI18n } from "@/lib/i18n"

/**
 * Un paquet de cartes de révision (audit produit 2026-11-13, R18) : le recto d'abord, « Voir la réponse », puis « Je savais »
 * ou « À revoir ». La note de l'élève est envoyée carte par carte (`noter`), jamais en bloc à la fin : fermer l'onglet au
 * milieu ne perd rien. Une carte ratée revient demain, une carte sue plus tard (voir quiz.cartes).
 */
export function PaquetDeCartes({
  cartes, noter, onTermine,
}: {
  cartes: CarteRevision[]
  noter: (carte: CarteRevision, savais: boolean) => Promise<unknown>
  onTermine?: () => void
}) {
  useI18n()
  const [index, setIndex] = useState(0)
  const [revele, setRevele] = useState(false)
  const [sues, setSues] = useState(0)
  const [enCours, setEnCours] = useState(false)
  const [erreur, setErreur] = useState(false)

  if (index >= cartes.length) {
    return (
      <div className="rounded-2xl border border-success/40 bg-success/5 px-5 py-5 text-center" role="status">
        <p className="font-display text-lg font-semibold">{t("cartes.fini")}</p>
        <p className="mt-1 text-sm text-muted-foreground">{t("cartes.bilan", { sues, rates: cartes.length - sues })}</p>
      </div>
    )
  }

  const carte = cartes[index]
  async function repondre(savais: boolean) {
    setEnCours(true)
    setErreur(false)
    try {
      await noter(carte, savais)
      setSues((n) => n + (savais ? 1 : 0))
      setRevele(false)
      setIndex((i) => i + 1)
      if (index + 1 >= cartes.length) onTermine?.()
    } catch {
      setErreur(true)
    } finally {
      setEnCours(false)
    }
  }

  return (
    <div>
      <p className="text-xs font-medium text-muted-foreground">
        {t("cartes.progression", { i: index + 1, n: cartes.length })}
        {carte.cours ? ` · ${carte.cours.titre}` : ""}
      </p>
      <div className="mt-2 rounded-2xl border border-border bg-card px-5 py-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-gold-text">
          {carte.type === "regle" ? t("cartes.regle") : t("cartes.erreur")}
        </p>
        <article className="prose prose-neutral mt-2 max-w-none dark:prose-invert">
          <EpreuveMarkdown markdown={carte.recto} />
        </article>
        {revele && (
          <article className="prose prose-neutral mt-4 max-w-none border-t border-border pt-4 dark:prose-invert">
            <EpreuveMarkdown markdown={carte.verso} />
          </article>
        )}
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {!revele ? (
          <Button type="button" className="min-h-11 rounded-full" onClick={() => setRevele(true)}>
            <Eye className="size-4" aria-hidden="true" />
            {t("cartes.voir")}
          </Button>
        ) : (
          <>
            <Button type="button" className="min-h-11 rounded-full" disabled={enCours} onClick={() => repondre(true)}>
              <Check className="size-4" aria-hidden="true" />
              {t("cartes.savais")}
            </Button>
            <Button type="button" variant="outline" className="min-h-11 rounded-full" disabled={enCours} onClick={() => repondre(false)}>
              <RotateCcw className="size-4" aria-hidden="true" />
              {t("cartes.revoir")}
            </Button>
          </>
        )}
      </div>
      {erreur && (
        <p role="alert" className="mt-2 text-sm text-destructive">
          {t("cartes.erreur_reseau")}
        </p>
      )}
    </div>
  )
}
