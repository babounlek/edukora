import { cheminDansLangue, langueCourante } from "@/lib/i18n"

const STORAGE_KEY = "edukamer-referral-code"

/**
 * Capture le code depuis ?ref=CODE dans l'URL, dès qu'il apparaît sur n'importe
 * quelle page - un visiteur qui clique un lien de parrainage navigue souvent
 * plusieurs pages avant de s'inscrire, le code doit survivre à cette navigation
 * jusqu'à l'écran de connexion (voir consumeReferralCode).
 */
export function captureReferralCode() {
  const params = new URLSearchParams(window.location.search)
  const code = params.get("ref")
  if (code) localStorage.setItem(STORAGE_KEY, code.toUpperCase())
  const rev = params.get("rev")
  if (rev) memoriserCodeRevendeur(rev)
}

/**
 * Code d'un revendeur (lien `?rev=CODE`), gardé 30 jours : un parent clique le lien d'un répétiteur, puis
 * revient s'inscrire ou payer plus tard. Clé à part du code de parrainage, pour que l'un n'écrase pas l'autre.
 * Une valeur illisible, périmée ou qui n'a pas la forme d'un code est ignorée (voir CODE_REVENDEUR).
 */
const REVENDEUR_KEY = "edukamer-revendeur-code"
const REVENDEUR_VALIDITE_MS = 30 * 24 * 60 * 60 * 1000
const CODE_REVENDEUR = /^[A-Z0-9]{4,10}$/

export function memoriserCodeRevendeur(code: string) {
  const propre = code.trim().toUpperCase()
  if (!CODE_REVENDEUR.test(propre)) return
  try {
    localStorage.setItem(REVENDEUR_KEY, JSON.stringify({ code: propre, le: Date.now() }))
  } catch {
    // Stockage refusé (navigation privée) : le code est alors simplement perdu à la fermeture de la page.
  }
}

export function codeRevendeurMemorise(): string {
  try {
    const brut = localStorage.getItem(REVENDEUR_KEY)
    if (!brut) return ""
    const { code, le } = JSON.parse(brut) as { code?: string; le?: number }
    if (typeof code !== "string" || typeof le !== "number" || !CODE_REVENDEUR.test(code)) return ""
    return Date.now() - le <= REVENDEUR_VALIDITE_MS ? code : ""
  } catch {
    return ""
  }
}

export function oublierCodeRevendeur() {
  try {
    localStorage.removeItem(REVENDEUR_KEY)
  } catch {
    // Rien à oublier si le stockage est inaccessible.
  }
}

/** Le code à envoyer à l'inscription : celui d'un revendeur d'abord, sinon celui d'un parrain. */
export function consumeReferralCode(): string {
  return codeRevendeurMemorise() || (localStorage.getItem(STORAGE_KEY) ?? "")
}

export function clearReferralCode() {
  localStorage.removeItem(STORAGE_KEY)
  // Appareil partagé (cybercafé, téléphone prêté) : un code consommé par une connexion ne doit pas rattacher
  // la personne suivante.
  oublierCodeRevendeur()
}

/** Lien à partager par un revendeur, vers l'accueil dans la langue de l'interface. */
export function lienDeRevendeur(code: string): string {
  const accueil = cheminDansLangue("/", langueCourante())
  return `${window.location.origin}${accueil === "/" ? "/" : `${accueil}/`}?rev=${code}`
}

/**
 * Lien de parrainage vers l'accueil, dans la langue de l'interface : un élève qui parraine depuis la
 * version anglaise envoie un lien anglais à son ami (voir lib/i18n/prefixe.ts).
 */
export function lienDeParrainage(code: string): string {
  const accueil = cheminDansLangue("/", langueCourante())
  return `${window.location.origin}${accueil === "/" ? "/" : `${accueil}/`}?ref=${code}`
}
