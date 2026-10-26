import { cheminDansLangue, langueCourante } from "@/lib/i18n"

// Partager une page (épreuve, cours, épreuve inédite...) avec un camarade. Même logique que
// partageScore.ts, sans la carte image : l'aperçu du lien (titre, image) est fourni par le serveur
// aux robots de WhatsApp et consorts, voir backend/catalog/apercu_partage.py.

export interface DonneesPartageLien {
  /** Phrase d'accroche, sans le lien : « Regarde ce corrigé de Maths BAC C 2023 ». */
  texte: string
  /** Chemin de la page à partager (`/cm/epreuves/maths-bac-c-2023`), sans domaine ni paramètre. */
  chemin: string
  /** Code de parrainage de l'élève connecté : ajouté au lien pour que l'ami lui soit rattaché. */
  codeParrainage?: string
  /** Paramètres ajoutés au lien (le score à battre d'un défi, par exemple). */
  parametres?: Record<string, string>
}

export type ResultatPartageLien = "partage" | "annule" | "indisponible"
export type CanalPartage = "natif" | "whatsapp" | "copie"

/** Lien absolu de la page, avec le code de parrainage quand l'élève en a un. */
export function lienDePartage({ chemin, codeParrainage, parametres }: Pick<DonneesPartageLien, "chemin" | "codeParrainage" | "parametres">): string {
  // Dans la langue de l'interface : le lien d'une page anglaise s'ouvre en anglais chez l'ami
  // (préfixe /en, voir lib/i18n/prefixe.ts).
  const url = new URL(cheminDansLangue(chemin, langueCourante()), window.location.origin)
  for (const [cle, valeur] of Object.entries(parametres ?? {})) url.searchParams.set(cle, valeur)
  if (codeParrainage) url.searchParams.set("ref", codeParrainage)
  return url.toString()
}

export function messageDePartage(donnees: DonneesPartageLien): string {
  return `${donnees.texte} ${lienDePartage(donnees)}`
}

export function partageNatifDisponible(): boolean {
  return typeof navigator !== "undefined" && typeof navigator.share === "function"
}

/**
 * Le partage natif n'est proposé que sur un appareil tactile : sur ordinateur, Windows ouvre un
 * panneau capricieux (« Nous n'avons pas pu vous montrer tous les partages possibles ») alors que le
 * menu WhatsApp / copier le lien marche à tous les coups.
 */
export function partageNatifPrefere(): boolean {
  return partageNatifDisponible() && typeof window.matchMedia === "function" && window.matchMedia("(pointer: coarse)").matches
}

/** Le panneau de partage du téléphone. "indisponible" : rien à ouvrir ici, proposer WhatsApp / copier. */
export async function partagerNativement(donnees: DonneesPartageLien): Promise<ResultatPartageLien> {
  if (!partageNatifDisponible()) return "indisponible"
  try {
    // Le lien reste aussi dans le texte : WhatsApp ignore le champ `url` quand un texte est fourni.
    await navigator.share({ text: messageDePartage(donnees) })
    return "partage"
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") return "annule"
    return "indisponible"
  }
}

export function ouvrirWhatsApp(donnees: DonneesPartageLien) {
  window.open(`https://wa.me/?text=${encodeURIComponent(messageDePartage(donnees))}`, "_blank", "noopener,noreferrer")
}

/**
 * Copie le lien seul (pas le texte) ; false quand ni le presse-papiers moderne ni la copie historique ne marchent.
 * Le repli existe pour les navigateurs de téléphone anciens ou sans permission (WebView, page non sécurisée), où
 * l'API moderne échoue : l'élève voyait « Impossible de copier le lien » pour un geste qui marche autrement.
 */
export async function copierLienDePartage(donnees: DonneesPartageLien): Promise<boolean> {
  const lien = lienDePartage(donnees)
  try {
    await navigator.clipboard.writeText(lien)
    return true
  } catch {
    return copierParSelection(lien)
  }
}

function copierParSelection(texte: string): boolean {
  try {
    const zone = document.createElement("textarea")
    zone.value = texte
    zone.setAttribute("readonly", "")
    zone.style.position = "fixed"
    zone.style.opacity = "0"
    document.body.appendChild(zone)
    zone.select()
    const ok = document.execCommand("copy")
    document.body.removeChild(zone)
    return ok
  } catch {
    return false
  }
}
