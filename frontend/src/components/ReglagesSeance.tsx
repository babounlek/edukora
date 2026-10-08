import { useState } from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { Bell, Volume2, Zap } from "lucide-react"

import { definirObjectifXp, getObjectifXp } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import { Button } from "@/components/ui/button"
import { trackEvent } from "@/lib/analytics"
import { activerPush, desactiverPush, etatPush } from "@/lib/push"
import { definirRetoursActifs, jouerRetour, retoursActifs } from "@/lib/retours"
import { cn } from "@/lib/utils"

const LIBELLES: Record<number, { nom: string; detail: string }> = {
  10: { nom: "Tranquille", detail: "10 points : environ 1 bonne réponse" },
  20: { nom: "Régulier", detail: "20 points : environ 2 bonnes réponses" },
  30: { nom: "Intense", detail: "30 points : environ 3 bonnes réponses" },
}

/**
 * Le rythme quotidien que l'élève se fixe (10, 20 ou 30 points d'XP) : un jour où il est
 * atteint compte pour la série, comme une séance du jour terminée. C'est l'élève qui le
 * choisit - jamais une exigence posée d'en haut - et il peut le changer à tout moment.
 */
export function ChoixRythme() {
  const queryClient = useQueryClient()
  const [enCours, setEnCours] = useState(false)
  const { data: etat } = useQuery({
    queryKey: ["objectif-xp"],
    queryFn: ({ signal }) => getObjectifXp(signal),
    staleTime: 60_000,
  })
  if (!etat) return null

  async function choisir(valeur: number) {
    if (enCours || valeur === etat?.objectif) return
    setEnCours(true)
    try {
      const nouvel = await definirObjectifXp(valeur)
      queryClient.setQueryData(["objectif-xp"], nouvel)
      // L'accueil et les écrans du jour relisent l'objectif sur le plan du jour.
      queryClient.invalidateQueries({ queryKey: ["plan-du-jour"] })
      trackEvent("objectif_xp_choisi", { objectif: valeur })
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Impossible d'enregistrer ton rythme. Réessaie.")
    } finally {
      setEnCours(false)
    }
  }

  return (
    <div>
      <p className="flex items-center gap-2 font-medium">
        <Zap className="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
        Ton rythme de chaque jour
      </p>
      <p className="mt-0.5 text-sm text-muted-foreground">
        Atteindre ton objectif de points compte pour ta série, même sans séance du jour. Les points se gagnent sur les
        bonnes réponses, surtout sur les thèmes à revoir.
      </p>
      <div role="radiogroup" aria-label="Objectif de points par jour" className="mt-3 grid grid-cols-3 gap-2">
        {etat.objectifs_possibles.map((valeur) => {
          const choisi = valeur === etat.objectif
          return (
            <button
              key={valeur}
              type="button"
              role="radio"
              aria-checked={choisi}
              disabled={enCours}
              title={LIBELLES[valeur]?.detail}
              onClick={() => choisir(valeur)}
              className={cn(
                "rounded-xl border-2 px-2 py-2.5 text-center transition-colors disabled:opacity-60",
                choisi ? "border-primary bg-primary/10" : "border-border hover:border-primary/40",
              )}
            >
              <span className="block text-sm font-semibold">{LIBELLES[valeur]?.nom ?? `${valeur} points`}</span>
              <span className="block text-xs tabular-nums text-muted-foreground">{valeur} points</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

const CLE_INVITE_PUSH = "edukora.push.invite"

function etatPushQuery() {
  return { queryKey: ["etat-push"], queryFn: etatPush, staleTime: 60_000 }
}

/** Active ou coupe les notifications de CET appareil. Masqué quand elles ne peuvent pas exister
 * (voir lib/push : navigateur sans push, push non configuré sur le serveur). */
export function InterrupteurPush() {
  const queryClient = useQueryClient()
  const [enCours, setEnCours] = useState(false)
  const { data: etat } = useQuery(etatPushQuery())
  if (!etat || etat === "indisponible") return null

  const actif = etat === "actif"

  async function basculer() {
    setEnCours(true)
    try {
      const suivant = actif ? (await desactiverPush(), "inactif" as const) : await activerPush()
      queryClient.setQueryData(["etat-push"], suivant)
      if (suivant === "refuse") {
        toast.error("Les notifications sont bloquées dans ton navigateur. Autorise-les dans ses réglages pour les activer.")
      }
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Impossible de modifier les notifications. Réessaie.")
    } finally {
      setEnCours(false)
    }
  }

  return (
    <div className="mt-4 flex items-center justify-between gap-4 border-t border-border pt-4">
      <div className="min-w-0">
        <p className="flex items-center gap-2 font-medium">
          <Bell className="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
          Un rappel sur cet appareil
        </p>
        <p className="mt-0.5 text-sm text-muted-foreground">
          Une notification par jour, à l'heure où tu révises d'habitude, seulement si tu n'as pas encore fait ta séance.
        </p>
        {etat === "refuse" && (
          <p className="mt-1 text-sm">Les notifications sont bloquées dans ton navigateur : autorise-les dans ses réglages.</p>
        )}
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={actif}
        aria-label="Un rappel sur cet appareil"
        disabled={enCours || etat === "refuse"}
        onClick={basculer}
        className={cn(
          "relative inline-flex h-7 w-12 shrink-0 items-center rounded-full border transition-colors disabled:opacity-60",
          actif ? "border-primary bg-primary" : "border-border bg-muted",
        )}
      >
        <span
          aria-hidden
          className={cn(
            "inline-block size-5 rounded-full bg-background shadow transition-transform",
            actif ? "translate-x-6" : "translate-x-1",
          )}
        />
      </button>
    </div>
  )
}

/**
 * L'invitation, une seule fois, au moment où elle a du sens : l'élève vient de finir un quiz et de
 * voir son objectif du jour. Écartée, elle ne revient plus ; le réglage reste dans le compte.
 * Jamais affichée à qui a déjà bloqué les notifications ou ne peut pas en recevoir.
 */
export function InvitePush({ className }: { className?: string }) {
  const queryClient = useQueryClient()
  const [ecartee, setEcartee] = useState(() => {
    try {
      return localStorage.getItem(CLE_INVITE_PUSH) === "1"
    } catch {
      return false
    }
  })
  const [enCours, setEnCours] = useState(false)
  const { data: etat } = useQuery({ ...etatPushQuery(), enabled: !ecartee })
  if (ecartee || etat !== "inactif") return null

  function ecarter() {
    try {
      localStorage.setItem(CLE_INVITE_PUSH, "1")
    } catch {
      // Stockage indisponible : l'invitation reviendra, sans conséquence.
    }
    setEcartee(true)
  }

  async function activer() {
    setEnCours(true)
    try {
      const suivant = await activerPush()
      queryClient.setQueryData(["etat-push"], suivant)
      if (suivant === "actif") toast.success("C'est fait : on te rappellera à ton heure habituelle.")
      if (suivant !== "inactif") ecarter()
    } catch {
      toast.error("Impossible d'activer les notifications. Réessaie plus tard.")
    } finally {
      setEnCours(false)
    }
  }

  return (
    <div className={cn("flex flex-col gap-3 rounded-2xl border border-border bg-card p-4 sm:flex-row sm:items-center", className)}>
      <Bell className="size-6 shrink-0 text-gold-text" aria-hidden="true" />
      <div className="min-w-0 flex-1">
        <p className="font-display font-semibold">Un rappel à ton heure habituelle ?</p>
        <p className="text-sm text-muted-foreground">
          Une notification par jour, seulement si ta séance n'est pas encore faite. Tu peux l'arrêter à tout moment.
        </p>
      </div>
      <div className="flex shrink-0 gap-2">
        <Button variant="ghost" size="sm" onClick={ecarter} disabled={enCours}>
          Non merci
        </Button>
        <Button size="sm" onClick={activer} disabled={enCours}>
          Activer
        </Button>
      </div>
    </div>
  )
}

/** Sons et vibrations de la séance : activés par défaut, propres à cet appareil. */
export function InterrupteurRetours() {
  const [actif, setActif] = useState(retoursActifs)

  function basculer() {
    const suivant = !actif
    definirRetoursActifs(suivant)
    setActif(suivant)
    // Un aperçu à l'activation : on entend tout de suite ce que fait le réglage.
    if (suivant) jouerRetour("juste")
  }

  return (
    <div className="flex items-center justify-between gap-4">
      <div className="min-w-0">
        <p className="flex items-center gap-2 font-medium">
          <Volume2 className="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
          Sons et vibrations
        </p>
        <p className="mt-0.5 text-sm text-muted-foreground">
          Un petit son et une vibration à chaque réponse. Ce réglage ne vaut que pour cet appareil.
        </p>
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={actif}
        aria-label="Sons et vibrations"
        onClick={basculer}
        className={cn(
          "relative inline-flex h-7 w-12 shrink-0 items-center rounded-full border transition-colors",
          actif ? "border-primary bg-primary" : "border-border bg-muted",
        )}
      >
        <span
          aria-hidden
          className={cn(
            "inline-block size-5 rounded-full bg-background shadow transition-transform",
            actif ? "translate-x-6" : "translate-x-1",
          )}
        />
      </button>
    </div>
  )
}
