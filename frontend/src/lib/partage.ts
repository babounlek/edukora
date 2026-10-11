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
}

export type ResultatPartageLien = "partage" | "annule" | "indisponible"
export type CanalPartage = "natif" | "whatsapp" | "copie"

/** Lien absolu de la page, avec le code de parrainage quand l'élève en a un. */
export function lienDePartage({ chemin, codeParrainage }: Pick<DonneesPartageLien, "chemin" | "codeParrainage">): string {
  const url = new URL(chemin, window.location.origin)
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

/** Copie le lien seul (pas le texte) ; false quand le navigateur refuse l'accès au presse-papiers. */
export async function copierLienDePartage(donnees: DonneesPartageLien): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(lienDePartage(donnees))
    return true
  } catch {
    return false
  }
}
