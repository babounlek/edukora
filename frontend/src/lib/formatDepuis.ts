/**
 * "mardi", "le 12 septembre" : la distance à la dernière visite, en mots. Moins d'une
 * semaine, le nom du jour suffit ; au-delà, la date - "il y a 23 jours" ferait le
 * compte à sa place et sonnerait comme un reproche.
 */
export function formatDepuis(dateIso: string, aujourdhui = new Date()): string {
  const [annee, mois, jour] = dateIso.split("-").map(Number)
  const date = new Date(annee, mois - 1, jour)
  const ref = new Date(aujourdhui.getFullYear(), aujourdhui.getMonth(), aujourdhui.getDate())
  const jours = Math.round((ref.getTime() - date.getTime()) / 86400000)
  if (jours <= 0) return "ce matin"
  if (jours === 1) return "hier"
  if (jours < 7) return new Intl.DateTimeFormat("fr-FR", { weekday: "long" }).format(date)
  return `le ${new Intl.DateTimeFormat("fr-FR", { day: "numeric", month: "long" }).format(date)}`
}

