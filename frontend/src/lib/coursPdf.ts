import { demanderCoursPdf } from "@/api/endpoints"

// Le serveur prépare le PDF à la première demande (quelques secondes) : on redemande jusqu'à ce qu'il soit prêt.
const PAUSE_MS = 2_500
const ESSAIS_MAX = 40

const attendre = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

/** Range le fichier dans les téléchargements de l'appareil. */
function enregistrer(blob: Blob, nom: string) {
  const url = URL.createObjectURL(blob)
  const lien = document.createElement("a")
  lien.href = url
  lien.download = nom
  document.body.appendChild(lien)
  lien.click()
  lien.remove()
  // Révocation différée : le navigateur doit avoir fini de lire l'URL objet.
  window.setTimeout(() => URL.revokeObjectURL(url), 60_000)
}

/**
 * Télécharge le PDF d'un cours. Lève une erreur si le serveur refuse ou ne l'a pas préparé à temps ; une coupure
 * réseau remonte telle quelle (NetworkError), pour que l'écran puisse la dire.
 */
export async function telechargerCoursPdf(slug: string): Promise<void> {
  for (let essai = 0; essai < ESSAIS_MAX; essai++) {
    const reponse = await demanderCoursPdf(slug)
    if (reponse instanceof Blob) {
      enregistrer(reponse, `${slug}.pdf`)
      return
    }
    await attendre(PAUSE_MS)
  }
  throw new Error("pdf_trop_long")
}
