import { useEffect, useState } from "react"
import { Download, X } from "lucide-react"

import { Button } from "@/components/ui/button"
import { SITE_NAME } from "@/lib/site"

const VISIT_COUNT_KEY = "edukamer_visit_count"
const DISMISSED_KEY = "edukamer_install_prompt_dismissed"
// "deuxième visite" (voir l'audit UX, reco 4.1) : jamais au tout premier
// chargement, où personne ne sait encore si le site vaut la peine d'être installé.
const MIN_VISITS_BEFORE_PROMPT = 2

/** Non standard (jamais dans lib.dom.d.ts) - Chrome/Edge/Android seulement, voir isIos(). */
interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>
}

function isStandalone(): boolean {
  // navigator.standalone : uniquement Safari iOS, jamais dans lib.dom.d.ts non plus.
  return (
    window.matchMedia("(display-mode: standalone)").matches ||
    (navigator as Navigator & { standalone?: boolean }).standalone === true
  )
}

function isIos(): boolean {
  // iOS Safari n'expose jamais beforeinstallprompt - la seule voie y est manuelle
  // (Partager -> Sur l'écran d'accueil), jamais un bouton "Installer" en un clic.
  return /iphone|ipad|ipod/i.test(navigator.userAgent)
}

function bumpVisitCount(): number {
  try {
    const count = (Number(localStorage.getItem(VISIT_COUNT_KEY)) || 0) + 1
    localStorage.setItem(VISIT_COUNT_KEY, String(count))
    return count
  } catch {
    return 0 // navigation privée - jamais éligible plutôt que de planter
  }
}

function markDismissed() {
  try {
    localStorage.setItem(DISMISSED_KEY, "1")
  } catch {
    // stockage indisponible - la bannière réapparaîtra simplement au prochain chargement
  }
}

function wasDismissed(): boolean {
  try {
    return localStorage.getItem(DISMISSED_KEY) === "1"
  } catch {
    return false
  }
}

/**
 * Bannière discrète (jamais un plein écran comme OnboardingModal) suggérant
 * d'installer la PWA - le levier de rétention le moins coûteux disponible
 * aujourd'hui, en l'absence de toute notification (voir l'audit UX, reco 4.1).
 * Déclenchée à partir de la 2e visite, jamais au premier chargement : sans
 * beforeinstallprompt (Chrome/Edge/Android) ET sans être sur iOS (Safari, qui n'émet
 * jamais cet évènement mais reste installable via Partager -> Sur l'écran d'accueil),
 * ce navigateur n'offre aucune voie d'installation - la bannière ne s'affiche jamais.
 */
export function InstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null)
  const [dismissed, setDismissed] = useState(wasDismissed)
  const [eligible, setEligible] = useState(false)

  useEffect(() => {
    if (isStandalone()) return
    setEligible(bumpVisitCount() >= MIN_VISITS_BEFORE_PROMPT)
  }, [])

  useEffect(() => {
    function handleBeforeInstallPrompt(event: Event) {
      // Empêche le mini-infobar natif du navigateur : on décide nous-mêmes du moment
      // (voir `eligible` ci-dessus), pas le navigateur dès que ses propres critères
      // internes sont réunis - souvent dès le tout premier chargement.
      event.preventDefault()
      setDeferredPrompt(event as BeforeInstallPromptEvent)
    }
    function handleAppInstalled() {
      markDismissed()
      setDismissed(true)
    }
    window.addEventListener("beforeinstallprompt", handleBeforeInstallPrompt)
    window.addEventListener("appinstalled", handleAppInstalled)
    return () => {
      window.removeEventListener("beforeinstallprompt", handleBeforeInstallPrompt)
      window.removeEventListener("appinstalled", handleAppInstalled)
    }
  }, [])

  const ios = isIos()
  const canShow = eligible && !dismissed && !isStandalone() && (deferredPrompt !== null || ios)

  if (!canShow) return null

  function close() {
    markDismissed()
    setDismissed(true)
  }

  async function handleInstallClick() {
    if (!deferredPrompt) return
    await deferredPrompt.prompt()
    await deferredPrompt.userChoice
    // Dans les deux cas (accepté ou refusé), le navigateur ne réémettra pas
    // beforeinstallprompt pour cette invite déjà consommée - la refermer évite un
    // bouton "Installer" mort, plutôt que de réessayer une action qui ne peut plus aboutir.
    setDeferredPrompt(null)
    close()
  }

  return (
    <div className="fixed inset-x-0 bottom-0 z-40 border-t border-border bg-background/95 backdrop-blur-sm">
      <div className="mx-auto flex max-w-5xl items-center gap-3 px-4 py-3 sm:px-6">
        <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
          <Download className="size-4.5" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium">Installe {SITE_NAME}</p>
          <p className="truncate text-xs text-muted-foreground">
            {ios
              ? "Appuie sur Partager, puis \"Sur l'écran d'accueil\"."
              : "Accède-y en un tap, même hors ligne."}
          </p>
        </div>
        {!ios && (
          <Button size="sm" onClick={handleInstallClick} className="shrink-0">
            Installer
          </Button>
        )}
        <Button
          variant="ghost"
          size="icon"
          className="size-8 shrink-0 tap-target-44"
          aria-label="Fermer"
          onClick={close}
        >
          <X className="size-4" />
        </Button>
      </div>
    </div>
  )
}
