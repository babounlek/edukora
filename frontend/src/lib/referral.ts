import { cheminDansLangue, langueCourante } from "@/lib/i18n"

const STORAGE_KEY = "edukamer-referral-code"

/**
 * Capture le code depuis ?ref=CODE dans l'URL, dès qu'il apparaît sur n'importe
 * quelle page - un visiteur qui clique un lien de parrainage navigue souvent
 * plusieurs pages avant de s'inscrire, le code doit survivre à cette navigation
 * jusqu'à l'écran de connexion (voir consumeReferralCode).
 */
export function captureReferralCode() {
  const code = new URLSearchParams(window.location.search).get("ref")
  if (code) localStorage.setItem(STORAGE_KEY, code.toUpperCase())
}

export function consumeReferralCode(): string {
  return localStorage.getItem(STORAGE_KEY) ?? ""
}

export function clearReferralCode() {
  localStorage.removeItem(STORAGE_KEY)
}

/**
 * Lien de parrainage vers l'accueil, dans la langue de l'interface : un élève qui parraine depuis la
 * version anglaise envoie un lien anglais à son ami (voir lib/i18n/prefixe.ts).
 */
export function lienDeParrainage(code: string): string {
  const accueil = cheminDansLangue("/", langueCourante())
  return `${window.location.origin}${accueil === "/" ? "/" : `${accueil}/`}?ref=${code}`
}
