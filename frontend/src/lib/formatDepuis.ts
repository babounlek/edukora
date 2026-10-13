import { localeCourante, t } from "@/lib/i18n"

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
  if (jours <= 0) return t("depuis.ce_matin")
  if (jours === 1) return t("depuis.hier")
  if (jours < 7) return new Intl.DateTimeFormat(localeCourante(), { weekday: "long" }).format(date)
  return t("depuis.le", { date: new Intl.DateTimeFormat(localeCourante(), { day: "numeric", month: "long" }).format(date) })
}

