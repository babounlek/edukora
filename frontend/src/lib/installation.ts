import { useSyncExternalStore } from "react"

// Installer EduKora sur l'écran d'accueil du téléphone (audit 14, F8). Le navigateur (Chrome et les navigateurs Android
// qui en dérivent) annonce qu'il PEUT installer par l'évènement `beforeinstallprompt` ; il n'accepte d'ouvrir sa fenêtre
// que sur un geste de l'élève, et une seule fois par évènement. On garde donc l'évènement dès qu'il arrive (il part tôt,
// bien avant le premier quiz) pour le rejouer au bon moment : après un quiz, quand l'élève a vu à quoi sert le site.
//
// Rien ici n'est indispensable : sans cet évènement (iOS, navigateur déjà installé, économie de données qui coupe le
// service worker - voir lib/pwa), l'invitation ne s'affiche simplement jamais.

interface EvenementInstallation extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>
}

const CLE_ECARTEE = "edukora:invite-installation"

let evenement: EvenementInstallation | null = null
const abonnes = new Set<() => void>()

function prevenir() {
  abonnes.forEach((abonne) => abonne())
}

/** À appeler une fois, au démarrage (voir main.tsx) : l'évènement n'est émis qu'une fois par chargement de page. */
export function ecouterInstallation() {
  if (typeof window === "undefined") return
  window.addEventListener("beforeinstallprompt", (e) => {
    // Sans cela, Chrome affiche sa propre bannière au moment qu'il choisit, souvent avant que l'élève ait rien vu.
    e.preventDefault()
    evenement = e as EvenementInstallation
    prevenir()
  })
  window.addEventListener("appinstalled", () => {
    evenement = null
    ecarterInstallation()
    prevenir()
  })
}

function dejaInstallee(): boolean {
  try {
    return window.matchMedia("(display-mode: standalone)").matches
  } catch {
    return false
  }
}

function ecartee(): boolean {
  try {
    return localStorage.getItem(CLE_ECARTEE) === "1"
  } catch {
    return false
  }
}

/** L'élève a répondu (installé, ou « Plus tard ») : on ne lui repose pas la question sur cet appareil. */
export function ecarterInstallation() {
  try {
    localStorage.setItem(CLE_ECARTEE, "1")
  } catch {
    // Stockage indisponible : l'invitation reviendra, sans conséquence.
  }
  prevenir()
}

function installationPossible(): boolean {
  return evenement !== null && !ecartee() && !dejaInstallee()
}

/** Vrai quand le navigateur peut installer l'application maintenant et que l'élève n'a pas encore répondu. */
export function useInstallationPossible(): boolean {
  return useSyncExternalStore(
    (abonne) => {
      abonnes.add(abonne)
      return () => abonnes.delete(abonne)
    },
    installationPossible,
    () => false,
  )
}

/**
 * Ouvre la fenêtre d'installation du navigateur. À appeler depuis un clic. Renvoie ce que l'élève a choisi, ou
 * "indisponible" quand le navigateur n'a plus rien à proposer. L'évènement ne sert qu'une fois : il est oublié ensuite.
 */
export async function proposerInstallation(): Promise<"accepted" | "dismissed" | "indisponible"> {
  const e = evenement
  if (!e) return "indisponible"
  evenement = null
  try {
    await e.prompt()
    const { outcome } = await e.userChoice
    // Refusée dans la fenêtre du navigateur : c'est une réponse, comme « Plus tard ».
    ecarterInstallation()
    return outcome
  } catch {
    prevenir()
    return "indisponible"
  }
}
