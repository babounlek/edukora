// Retours sensoriels d'une séance : un son très court et une vibration, pour qu'une réponse
// "se sente" sans qu'on ait à lire. Aucun fichier audio : les notes sont synthétisées (Web
// Audio), donc rien à télécharger sur une connexion chère. Activés par défaut, désactivables
// dans le compte ; la préférence est propre à l'appareil (on peut réviser en classe avec le
// son coupé sans l'avoir coupé à la maison).
//
// Jamais au prix de la réponse : tout est enveloppé, un navigateur sans Web Audio ou sans
// vibration (iOS) ignore simplement l'appel.

export type Retour = "juste" | "faux" | "objectif" | "fin"

const CLE = "edukora.retours"

export function retoursActifs(): boolean {
  try {
    return localStorage.getItem(CLE) !== "0"
  } catch {
    return true
  }
}

export function definirRetoursActifs(actif: boolean) {
  try {
    localStorage.setItem(CLE, actif ? "1" : "0")
  } catch {
    // Stockage indisponible (navigation privée) : la préférence ne tient que pour cette page.
  }
}

// Notes en Hz ; durées en secondes. Volume bas : un retour, pas une alerte.
const NOTES: Record<Retour, { freq: number; debut: number; duree: number }[]> = {
  juste: [{ freq: 659, debut: 0, duree: 0.09 }, { freq: 880, debut: 0.09, duree: 0.14 }],
  faux: [{ freq: 220, debut: 0, duree: 0.16 }],
  objectif: [
    { freq: 523, debut: 0, duree: 0.1 }, { freq: 659, debut: 0.1, duree: 0.1 },
    { freq: 784, debut: 0.2, duree: 0.1 }, { freq: 1047, debut: 0.3, duree: 0.22 },
  ],
  fin: [{ freq: 587, debut: 0, duree: 0.1 }, { freq: 784, debut: 0.1, duree: 0.2 }],
}

const VIBRATIONS: Record<Retour, number | number[]> = {
  juste: 15,
  faux: 40,
  objectif: [20, 40, 20, 40, 60],
  fin: [20, 30, 40],
}

type FabriqueAudio = typeof AudioContext

let contexte: AudioContext | null = null

function audio(): AudioContext | null {
  if (contexte) return contexte
  const Fabrique: FabriqueAudio | undefined =
    typeof window === "undefined"
      ? undefined
      : window.AudioContext ?? (window as unknown as { webkitAudioContext?: FabriqueAudio }).webkitAudioContext
  if (!Fabrique) return null
  contexte = new Fabrique()
  return contexte
}

function jouerNotes(retour: Retour) {
  const ctx = audio()
  if (!ctx) return
  // Un contexte créé hors geste utilisateur démarre suspendu : on le réveille ici, appelé depuis
  // un clic de réponse.
  if (ctx.state === "suspended") void ctx.resume()
  const t0 = ctx.currentTime
  for (const note of NOTES[retour]) {
    const oscillateur = ctx.createOscillator()
    const gain = ctx.createGain()
    oscillateur.type = "sine"
    oscillateur.frequency.value = note.freq
    // Enveloppe courte, pour éviter le "clic" de début et de fin de note.
    gain.gain.setValueAtTime(0.0001, t0 + note.debut)
    gain.gain.exponentialRampToValueAtTime(0.07, t0 + note.debut + 0.015)
    gain.gain.exponentialRampToValueAtTime(0.0001, t0 + note.debut + note.duree)
    oscillateur.connect(gain).connect(ctx.destination)
    oscillateur.start(t0 + note.debut)
    oscillateur.stop(t0 + note.debut + note.duree + 0.02)
  }
}

export function jouerRetour(retour: Retour) {
  if (!retoursActifs()) return
  try {
    jouerNotes(retour)
  } catch {
    // Pas de son : la couleur et le texte du retour portent déjà l'information.
  }
  try {
    navigator.vibrate?.(VIBRATIONS[retour])
  } catch {
    // Vibration refusée ou absente.
  }
}
