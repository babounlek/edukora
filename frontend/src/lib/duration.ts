/** Formate un nombre de secondes en mm:ss (ou h:mm:ss au-delà d'une heure) - partagé
 * entre le chrono de mode examen (InediteTentativePage) et le temps utilisé affiché
 * sur la page de résultat (InediteResultPage). */
export function formatDuration(totalSeconds: number): string {
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60
  const mm = String(minutes).padStart(2, "0")
  const ss = String(seconds).padStart(2, "0")
  return hours > 0 ? `${hours}:${mm}:${ss}` : `${mm}:${ss}`
}
