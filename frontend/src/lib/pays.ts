import type { Country } from "@/api/types"
import { langueCourante, localeCourante } from "@/lib/i18n"

/**
 * Nom d'un pays dans la langue de l'interface : « Cameroun » en français, « Cameroon » en anglais. Le serveur ne
 * connaît qu'un libellé (le français) ; en français on le garde tel quel, source de vérité (un pays peut y porter un
 * nom d'usage particulier), et dans une autre langue on demande le nom au navigateur (Intl.DisplayNames, noms de
 * régions ISO 3166) plutôt que d'entretenir une table que chaque nouveau pays obligerait à compléter.
 * Si le navigateur ne sait pas (code inconnu, API absente), on retombe sur le libellé du serveur.
 */
const noms = new Map<string, Intl.DisplayNames | null>()

function nomsDeRegions(locale: string): Intl.DisplayNames | null {
  if (!noms.has(locale)) {
    try {
      noms.set(locale, new Intl.DisplayNames([locale], { type: "region" }))
    } catch {
      noms.set(locale, null)
    }
  }
  return noms.get(locale) ?? null
}

export function libellePays(code: string, libelleServeur: string): string {
  if (langueCourante() === "fr") return libelleServeur
  try {
    const nom = nomsDeRegions(localeCourante())?.of(code.toUpperCase())
    // `of` renvoie le code lui-même quand il ne connaît pas la région : ce n'est pas un nom.
    return nom && nom.toUpperCase() !== code.toUpperCase() ? nom : libelleServeur
  } catch {
    return libelleServeur
  }
}

/** Le nom du pays courant (code minuscule de l'URL) parmi `countries`, dans la langue de l'interface ; undefined si inconnu. */
export function nomPays(countries: Pick<Country, "code" | "label">[], code: string | undefined): string | undefined {
  const pays = countries.find((c) => c.code.toLowerCase() === code)
  return pays ? libellePays(pays.code, pays.label) : undefined
}
