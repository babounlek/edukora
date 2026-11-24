const COTE_MAX = 1600
const QUALITE = 0.82

/**
 * Réduit une photo avant l'envoi : un cliché de téléphone fait 3 à 8 Mo, ce qui est trop sur une connexion mobile. On le
 * ramène à 1600 px de côté en JPEG (de l'ordre de 200 à 400 Ko). Le serveur refait la même vérification et la même
 * réduction : ceci n'est qu'un gain de données. En cas d'échec (navigateur ancien, format exotique), le fichier part tel quel.
 */
export async function reduireImage(fichier: File): Promise<Blob> {
  try {
    const bitmap = await createImageBitmap(fichier, { imageOrientation: "from-image" })
    const echelle = Math.min(1, COTE_MAX / Math.max(bitmap.width, bitmap.height))
    const canevas = document.createElement("canvas")
    canevas.width = Math.round(bitmap.width * echelle)
    canevas.height = Math.round(bitmap.height * echelle)
    const contexte = canevas.getContext("2d")
    if (!contexte) return fichier
    contexte.fillStyle = "#ffffff"
    contexte.fillRect(0, 0, canevas.width, canevas.height)
    contexte.drawImage(bitmap, 0, 0, canevas.width, canevas.height)
    bitmap.close()
    const blob = await new Promise<Blob | null>((resolve) => canevas.toBlob(resolve, "image/jpeg", QUALITE))
    return blob && blob.size < fichier.size ? blob : fichier
  } catch {
    return fichier
  }
}
