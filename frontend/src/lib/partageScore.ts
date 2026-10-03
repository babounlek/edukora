// Partager son score : une carte image (dessinée ici, sans dépendance ni aller-retour serveur) et un
// message qui porte le lien de parrainage de l'élève. WhatsApp est le canal de partage naturel de
// ces élèves : sur un téléphone qui sait partager un fichier (Web Share), la carte part avec le
// message ; sinon un lien wa.me avec le texte seul - toujours un chemin qui marche.

export interface DonneesPartage {
  score: number
  total: number
  xp: number
  serie: number
  nomSite: string
  lien: string
}

export function textePartage({ score, total, xp, serie, nomSite, lien }: DonneesPartage): string {
  const details = [xp > 0 ? `+${xp} XP` : "", serie >= 2 ? `${serie} jours de suite` : ""].filter(Boolean)
  return (
    `J'ai eu ${score}/${total} à mon quiz sur ${nomSite}` +
    (details.length ? ` (${details.join(", ")})` : "") +
    `. Tu fais mieux ? ${lien}`
  )
}

const TAILLE = 1080

/** La carte en PNG, ou null quand le navigateur ne sait pas dessiner (jsdom, navigateur ancien). */
export async function carteEnImage(donnees: DonneesPartage): Promise<Blob | null> {
  const canvas = document.createElement("canvas")
  canvas.width = TAILLE
  canvas.height = TAILLE
  const ctx = canvas.getContext("2d")
  if (!ctx) return null

  // Aplat de la couleur de marque : sobre, lisible même une fois recompressé par une messagerie.
  ctx.fillStyle = "#0a6e4e"
  ctx.fillRect(0, 0, TAILLE, TAILLE)
  ctx.fillStyle = "rgba(255,255,255,0.08)"
  ctx.beginPath()
  ctx.arc(TAILLE - 120, 140, 360, 0, Math.PI * 2)
  ctx.fill()

  ctx.textAlign = "center"
  ctx.fillStyle = "#ffffff"
  ctx.font = "500 52px system-ui, sans-serif"
  ctx.fillText("Mon quiz du jour", TAILLE / 2, 250)

  ctx.font = "700 340px Georgia, serif"
  // La barre oblique descend sous la ligne de base : on remonte le score et on descend les lignes
  // du dessous pour qu'elles ne se touchent jamais.
  ctx.fillText(`${donnees.score}/${donnees.total}`, TAILLE / 2, 560)

  ctx.font = "600 64px system-ui, sans-serif"
  ctx.fillStyle = "#f5c84b"
  const lignes = [donnees.xp > 0 ? `+${donnees.xp} XP` : "", donnees.serie >= 2 ? `Série de ${donnees.serie} jours` : ""].filter(Boolean)
  lignes.forEach((ligne, i) => ctx.fillText(ligne, TAILLE / 2, 745 + i * 78))

  ctx.fillStyle = "#ffffff"
  ctx.font = "700 72px Georgia, serif"
  ctx.fillText(donnees.nomSite, TAILLE / 2, 960)
  ctx.font = "400 40px system-ui, sans-serif"
  ctx.fillStyle = "rgba(255,255,255,0.8)"
  ctx.fillText("Révise ton examen, un jour après l'autre", TAILLE / 2, 1020)

  return new Promise((resolve) => canvas.toBlob((blob) => resolve(blob), "image/png"))
}

export type ResultatPartage = "partage" | "lien" | "annule"

/**
 * Ouvre le partage du téléphone avec la carte et le texte ; à défaut, WhatsApp avec le texte seul.
 * "annule" quand l'élève ferme le panneau de partage - ce n'est pas une erreur, rien à signaler.
 */
export async function partagerScore(donnees: DonneesPartage): Promise<ResultatPartage> {
  const texte = textePartage(donnees)
  try {
    if (typeof navigator.share === "function") {
      const image = await carteEnImage(donnees)
      const fichier = image ? new File([image], "mon-score.png", { type: "image/png" }) : null
      if (fichier && navigator.canShare?.({ files: [fichier] })) {
        await navigator.share({ files: [fichier], text: texte })
      } else {
        await navigator.share({ text: texte })
      }
      return "partage"
    }
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") return "annule"
    // Tout autre échec du partage natif : on retombe sur le lien WhatsApp.
  }
  window.open(`https://wa.me/?text=${encodeURIComponent(texte)}`, "_blank", "noopener,noreferrer")
  return "lien"
}
