import { t, type CleI18n } from "@/lib/i18n"

const NOMS: Record<number, CleI18n> = {
  30: "rythme.tranquille",
  50: "rythme.regulier",
  80: "rythme.intense",
}

/** « Régulier · 50 points » : le rythme dit comme l'élève le connaît, avec son nombre de points. */
export function libelleRythme(objectif: number): string {
  const nom = NOMS[objectif]
  return nom ? `${t(nom)} · ${t("rythme.points", { n: objectif })}` : t("rythme.points", { n: objectif })
}
