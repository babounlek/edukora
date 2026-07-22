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
