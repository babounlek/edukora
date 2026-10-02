import { useCallback, useEffect, useState } from "react"
import { Loader2, Lock, UserCircle } from "lucide-react"

import { ApiError } from "@/api/client"
import type { Profil } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { activerProfilProtege, useProfils } from "@/lib/changerProfilActif"
import { PinAnnule } from "@/lib/pinPrompts"
import { Button } from "@/components/ui/button"

// Au-delà, on repasse par « Qui étudie ? » : l'appareil est sans doute passé à quelqu'un
// d'autre. Assez long pour ne jamais gêner une séance, assez court pour protéger un profil
// laissé ouvert sur la table.
const INACTIVITE_MS = 10 * 60 * 1000
const CLE_ACTIVITE = "edukora:derniere-activite"

function lireDerniereActivite(): number {
  try {
    return Number(sessionStorage.getItem(CLE_ACTIVITE)) || Date.now()
  } catch {
    return Date.now()
  }
}

function noterActivite() {
  try {
    sessionStorage.setItem(CLE_ACTIVITE, String(Date.now()))
  } catch {
    // Stockage indisponible (navigation privée...) : le verrou fonctionne alors en mémoire seulement.
  }
}

/**
 * Verrouillage après inactivité : quand au moins un profil du compte est protégé par un
 * code, on repasse par « Qui étudie ? » après 10 minutes sans activité (ou à la réouverture
 * de l'onglet après ce délai). Choisir un profil protégé - y compris celui qui était
 * ouvert - redemande son code, vérifié côté serveur (voir activer_profil_view). Rien ne
 * s'active tant qu'aucun profil n'a de code : sans PIN, ce verrou ne gênerait personne
 * pour rien. Pas pour une session ouverte par l'enfant (un seul profil, le sien).
 */
export function VerrouInactivite() {
  const { user, isAuthenticated, login, logout } = useAuth()
  const profils = useProfils()
  const [verrouille, setVerrouille] = useState(false)
  const [chargement, setChargement] = useState<number | null>(null)
  const [erreur, setErreur] = useState<string | null>(null)

  const actif = isAuthenticated && !user?.session_restreinte && profils.length > 1 && profils.some((p) => p.pin_actif)

  const verifier = useCallback(() => {
    if (Date.now() - lireDerniereActivite() > INACTIVITE_MS) setVerrouille(true)
  }, [])

  useEffect(() => {
    if (!actif) {
      setVerrouille(false)
      return
    }
    noterActivite()
    function surActivite() {
      // Pas d'enregistrement pendant que l'écran de verrouillage est affiché : il faut
      // choisir un profil, pas simplement bouger la souris.
      setVerrouille((v) => {
        if (!v) noterActivite()
        return v
      })
    }
    function surVisibilite() {
      if (document.visibilityState === "visible") verifier()
    }
    const evenements: (keyof WindowEventMap)[] = ["pointerdown", "keydown", "scroll", "touchstart"]
    evenements.forEach((e) => window.addEventListener(e, surActivite, { passive: true }))
    document.addEventListener("visibilitychange", surVisibilite)
    const minuteur = window.setInterval(verifier, 30_000)
    verifier()
    return () => {
      evenements.forEach((e) => window.removeEventListener(e, surActivite))
      document.removeEventListener("visibilitychange", surVisibilite)
      window.clearInterval(minuteur)
    }
  }, [actif, verifier])

  async function choisir(profil: Profil) {
    setErreur(null)
    const dejaActif = profil.id === user?.profil_actif?.id
    // Le profil déjà ouvert et sans code : rien à vérifier, on déverrouille simplement.
    if (dejaActif && !profil.pin_actif) {
      noterActivite()
      setVerrouille(false)
      return
    }
    setChargement(profil.id)
    try {
      const reponse = await activerProfilProtege(profil.id, profil.prenom, undefined, dejaActif)
      noterActivite()
      login(reponse.access, reponse.user)
      if (dejaActif) {
        setVerrouille(false)
      } else {
        // Un autre enfant : toutes les données scopées par profil changent, comme pour
        // le sélecteur du menu (voir useChangerProfilActif).
        window.location.reload()
      }
    } catch (err) {
      if (!(err instanceof PinAnnule)) {
        setErreur(err instanceof ApiError ? err.message : "Impossible d'ouvrir ce profil.")
      }
    } finally {
      setChargement(null)
    }
  }

  if (!actif || !verrouille) return null

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Qui étudie ?"
      // z-40 : sous les fenêtres de saisie du code (z-50, voir ui/dialog), qui doivent s'afficher par-dessus.
      className="fixed inset-0 z-40 flex items-center justify-center overflow-y-auto bg-background px-4 py-10"
    >
      <div className="w-full max-w-sm">
        <div className="mb-6 text-center">
          <span className="mx-auto mb-3 flex size-11 items-center justify-center rounded-full bg-primary/10 text-primary">
            <Lock className="size-5" />
          </span>
          <h1 className="font-display text-2xl font-semibold tracking-tight">Qui étudie ?</h1>
          <p className="mt-1.5 text-sm text-muted-foreground">
            Après un moment d'inactivité, on vérifie qui est là. Choisis ton profil pour continuer.
          </p>
        </div>
        <div className="flex flex-col gap-2.5">
          {profils.map((profil) => (
            <button
              key={profil.id}
              type="button"
              onClick={() => choisir(profil)}
              disabled={chargement !== null}
              className="flex w-full items-center gap-3 rounded-xl border border-border bg-card px-4 py-3.5 text-left transition-colors hover:bg-accent disabled:opacity-60"
            >
              <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                <UserCircle className="size-5" />
              </span>
              <span className="flex-1 font-display text-base font-medium">{profil.prenom || "Profil sans nom"}</span>
              {profil.pin_actif && <Lock className="size-4 shrink-0 text-muted-foreground" aria-label="Protégé par un code" />}
              {chargement === profil.id && <Loader2 className="size-4 shrink-0 animate-spin text-muted-foreground" />}
            </button>
          ))}
        </div>
        {erreur && (
          <p role="alert" className="mt-3 text-center text-sm text-destructive">
            {erreur}
          </p>
        )}
        <div className="mt-5 text-center">
          <Button variant="ghost" size="sm" onClick={logout}>
            Se déconnecter
          </Button>
        </div>
      </div>
    </div>
  )
}
