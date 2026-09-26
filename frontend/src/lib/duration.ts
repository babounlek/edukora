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

/** « 2 h », « 1 h 30 », « 45 min » - la durée d'une épreuve en langage courant. */
export function formatDureeMinutes(minutes: number): string {
  const heures = Math.floor(minutes / 60)
  const reste = minutes % 60
  if (heures === 0) return `${reste} min`
  return reste === 0 ? `${heures} h` : `${heures} h ${String(reste).padStart(2, "0")}`
}
