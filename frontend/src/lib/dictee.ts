import { useCallback, useEffect, useRef, useState } from "react"

/**
 * La dictée vocale d'une note : la reconnaissance vocale du navigateur (Chrome et Edge sur téléphone et ordinateur, Safari
 * récent). Rien n'est envoyé par nous : c'est le navigateur qui transcrit, et il demande lui-même l'accès au micro. Les
 * formules ne se dictent pas (on les écrit ou on les tape avec le bouton Σ) ; c'est pour les phrases de cours.
 */

interface AlternativeDictee { transcript: string }
interface ResultatDictee { isFinal: boolean; 0: AlternativeDictee }
interface EvenementDictee { resultIndex: number; results: ArrayLike<ResultatDictee> }
interface ReconnaissanceVocale {
  lang: string
  continuous: boolean
  interimResults: boolean
  onresult: ((e: EvenementDictee) => void) | null
  onerror: ((e: { error: string }) => void) | null
  onend: (() => void) | null
  start: () => void
  stop: () => void
  abort: () => void
}
type FabriqueDictee = new () => ReconnaissanceVocale

function fabrique(): FabriqueDictee | null {
  if (typeof window === "undefined") return null
  const w = window as unknown as { SpeechRecognition?: FabriqueDictee; webkitSpeechRecognition?: FabriqueDictee }
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null
}

export function dicteeDisponible(): boolean {
  return fabrique() !== null
}

/** Le texte dicté, mis à la suite de ce qui est déjà écrit, avec une espace entre les deux. */
export function ajouterALaSuite(texte: string, dicte: string): string {
  const ajout = dicte.trim()
  if (!ajout) return texte
  if (!texte || /\s$/.test(texte)) return texte + ajout
  return `${texte} ${ajout}`
}

export type ErreurDictee = "refusee" | "reseau" | "autre"

export function useDictee({
  langue, onTexte, onErreur,
}: { langue: "fr" | "en"; onTexte: (dicte: string) => void; onErreur?: (e: ErreurDictee) => void }) {
  const [actif, setActif] = useState(false)
  const [provisoire, setProvisoire] = useState("")
  const reco = useRef<ReconnaissanceVocale | null>(null)
  const rappels = useRef({ onTexte, onErreur })
  rappels.current = { onTexte, onErreur }

  const arreter = useCallback(() => {
    reco.current?.stop()
  }, [])

  const demarrer = useCallback(() => {
    const Fabrique = fabrique()
    if (!Fabrique || reco.current) return
    const r = new Fabrique()
    r.lang = langue === "en" ? "en-GB" : "fr-FR"
    r.continuous = true
    r.interimResults = true
    r.onresult = (e) => {
      let reste = ""
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const res = e.results[i]
        if (res.isFinal) rappels.current.onTexte(res[0].transcript)
        else reste += res[0].transcript
      }
      setProvisoire(reste)
    }
    r.onerror = (e) => {
      if (e.error === "not-allowed" || e.error === "service-not-allowed") rappels.current.onErreur?.("refusee")
      else if (e.error === "network") rappels.current.onErreur?.("reseau")
      // « no-speech » et « aborted » : un silence ou un arrêt volontaire, rien à dire.
      else if (e.error !== "no-speech" && e.error !== "aborted") rappels.current.onErreur?.("autre")
    }
    r.onend = () => {
      reco.current = null
      setActif(false)
      setProvisoire("")
    }
    reco.current = r
    setActif(true)
    try {
      r.start()
    } catch {
      reco.current = null
      setActif(false)
    }
  }, [langue])

  // La dictée s'arrête avec la fenêtre : un micro resté ouvert à l'insu de l'élève serait pire qu'une dictée perdue.
  useEffect(() => () => reco.current?.abort(), [])

  return { actif, provisoire, demarrer, arreter, disponible: dicteeDisponible() }
}
