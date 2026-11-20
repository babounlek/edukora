import { useEffect, useRef, useState } from "react"
import { useQueryClient } from "@tanstack/react-query"
import { Check, Eye, RotateCcw, Zap } from "lucide-react"

import type { CarteRevision, EtatXp } from "@/api/types"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { Button } from "@/components/ui/button"
import { MascotteDessin } from "@/components/MascotteDessin"
import { MASCOTTE_ACTIVE } from "@/lib/mascotte"
import { libellePoints } from "@/lib/notation"
import { jouerRetour } from "@/lib/retours"
import { t, useI18n } from "@/lib/i18n"

/** Ce que le serveur dit avoir crédité pour cette revue (voir noterCarte) ; rien si la réponse n'en parle pas. */
function gainDeLaRevue(reponse: unknown): { gagne: number; jour?: EtatXp } {
  const r = (reponse ?? {}) as { xp_gagne?: unknown; xp_jour?: EtatXp }
  return { gagne: typeof r.xp_gagne === "number" && r.xp_gagne > 0 ? r.xp_gagne : 0, jour: r.xp_jour }
}

/** Les points gagnés depuis l'ouverture du paquet : la pastille rebondit à chaque point de plus (`key`). */
function PastillePoints({ points, className }: { points: number; className?: string }) {
  return (
    <span
      key={points}
      className={`animate-xp-pop inline-flex shrink-0 items-center gap-1 whitespace-nowrap rounded-full bg-gold/20 px-2.5 py-0.5 font-bold tabular-nums text-gold-text ${className ?? ""}`}
    >
      <Zap className="size-3.5" aria-hidden="true" />+{libellePoints(points)}
    </span>
  )
}

/**
 * Un paquet de cartes de révision (audit produit 2026-11-13, R18) : le recto d'abord, « Voir la réponse », puis « Je savais »
 * ou « À revoir ». La note de l'élève est envoyée carte par carte (`noter`), jamais en bloc à la fin : fermer l'onglet au
 * milieu ne perd rien. Une carte ratée revient demain, une carte sue plus tard (voir quiz.cartes).
 *
 * Une carte revue à son échéance rapporte un point (voir quiz.xp.XP_CARTE) : les points s'affichent au fil du paquet et à
 * la fin, tels que le serveur les a crédités - jamais un point promis qui n'aurait pas été compté (plafond du jour).
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
  const [points, setPoints] = useState(0)
  const [jour, setJour] = useState<EtatXp | null>(null)
  // « Je savais » d'affilée : la note monte d'un cran à chaque carte sue de suite, comme dans un quiz (voir lib/retours).
  const [suite, setSuite] = useState(0)
  const client = useQueryClient()
  const haut = useRef<HTMLDivElement>(null)
  const termine = index >= cartes.length

  // Après une carte, la suivante doit être sous les yeux : sinon l'écran restait au bas d'un verso de plusieurs écrans,
  // dans le pied de page. Rien à faire au premier rendu.
  useEffect(() => {
    if (index > 0) haut.current?.scrollIntoView({ block: "start", behavior: "smooth" })
  }, [index])
  useEffect(() => {
    if (!termine) return
    jouerRetour("fin")
    // La ligne d'objectif de l'accueil lit le plan du jour : elle doit compter les points de ce paquet.
    if (points > 0) client.invalidateQueries({ queryKey: ["plan-du-jour"] })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [termine])

  if (termine) {
    return (
      <div ref={haut} className="scroll-mt-20 rounded-2xl border border-success/40 bg-success/5 px-5 py-5 text-center" role="status">
        {MASCOTTE_ACTIVE && <MascotteDessin humeur="fete" saut={cartes.length} taille={64} className="mx-auto mb-2" />}
        <p className="font-display text-lg font-semibold">{t("cartes.fini")}</p>
        {points > 0 && (
          <p className="mt-2">
            <PastillePoints points={points} className="px-3 py-1 text-sm" />
          </p>
        )}
        {points > 0 && jour && (
          <p className="mt-1.5 text-xs font-medium text-muted-foreground">
            {jour.atteint ? t("ligne.objectif_atteint") : t("ligne.points", { xp: jour.xp, objectif: jour.objectif })}
          </p>
        )}
        <p className="mt-1 text-sm text-muted-foreground">{t("cartes.bilan", { sues, rates: cartes.length - sues })}</p>
      </div>
    )
  }

  const carte = cartes[index]
  async function repondre(savais: boolean) {
    setEnCours(true)
    setErreur(false)
    try {
      const { gagne, jour: etat } = gainDeLaRevue(await noter(carte, savais))
      if (gagne > 0) {
        setPoints((n) => n + gagne)
        if (etat) setJour(etat)
      }
      const derniere = index + 1 >= cartes.length
      // Une carte sue s'entend ; « À revoir » reste silencieux (ce n'est pas une faute). La dernière laisse la place au son de fin.
      if (savais && !derniere) jouerRetour("juste", { serie: suite + 1 })
      setSuite(savais ? suite + 1 : 0)
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
    <div ref={haut} className="scroll-mt-20">
      <div className="flex items-center justify-between gap-2 text-xs">
        <p className="min-w-0 font-medium text-muted-foreground">
          {t("cartes.progression", { i: index + 1, n: cartes.length })}
          {carte.cours ? ` · ${carte.cours.titre}` : ""}
        </p>
        {points > 0 && <PastillePoints points={points} />}
      </div>
      <div className="mt-2 rounded-2xl border border-border bg-card px-5 py-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-gold-text">
          {carte.type === "regle" ? t("cartes.regle") : t("cartes.erreur")}
        </p>
        <article className="prose prose-neutral mt-2 max-w-none dark:prose-invert">
          <EpreuveMarkdown markdown={carte.recto} />
        </article>
        {revele && (
          <article tabIndex={0} className="prose prose-neutral mt-4 max-h-[55vh] max-w-none overflow-y-auto border-t border-border pt-4 dark:prose-invert">
            <EpreuveMarkdown markdown={carte.verso} />
          </article>
        )}
      </div>

      <div className="sticky bottom-[var(--bottom-tab-bar,0px)] z-10 -mx-1 mt-3 flex flex-wrap gap-2 bg-background/95 px-1 py-2 backdrop-blur-sm">
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
