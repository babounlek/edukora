/**
 * La mise en forme d'une note : du Markdown, que le moteur de NoteTexte sait déjà rendre. Sur téléphone personne ne tape « ** »
 * à la main ; ces fonctions posent les signes autour de la sélection d'un champ de texte.
 */

export type Format = "gras" | "italique" | "liste" | "formule"

export interface Edition {
  texte: string
  /** Sélection à rétablir dans le champ après la mise en forme. */
  debut: number
  fin: number
}

const ENTOURAGES: Record<"gras" | "italique" | "formule", [string, string]> = {
  gras: ["**", "**"],
  italique: ["*", "*"],
  formule: ["$", "$"],
}

/** Applique `format` à la sélection [debut, fin) de `texte` ; sans sélection, pose les signes avec le curseur au milieu. */
export function appliquerFormat(texte: string, debut: number, fin: number, format: Format): Edition {
  if (format === "liste") {
    // Un « - » en tête de chaque ligne touchée par la sélection ; un second appui le retire.
    const debutLigne = texte.lastIndexOf("\n", debut - 1) + 1
    const finBrute = texte.indexOf("\n", fin)
    const finLigne = finBrute === -1 ? texte.length : finBrute
    const lignes = texte.slice(debutLigne, finLigne).split("\n")
    const deja = lignes.every((l) => l.startsWith("- "))
    const neuves = lignes.map((l) => (deja ? l.slice(2) : `- ${l}`))
    const bloc = neuves.join("\n")
    return { texte: texte.slice(0, debutLigne) + bloc + texte.slice(finLigne), debut: debutLigne, fin: debutLigne + bloc.length }
  }
  const [avant, apres] = ENTOURAGES[format]
  const selection = texte.slice(debut, fin)
  // Déjà entouré : un second appui retire les signes.
  if (
    selection.length >= avant.length + apres.length &&
    selection.startsWith(avant) &&
    selection.endsWith(apres) &&
    !(format === "italique" && selection.startsWith("**"))
  ) {
    const interieur = selection.slice(avant.length, selection.length - apres.length)
    return { texte: texte.slice(0, debut) + interieur + texte.slice(fin), debut, fin: debut + interieur.length }
  }
  const nouveau = texte.slice(0, debut) + avant + selection + apres + texte.slice(fin)
  return selection
    ? { texte: nouveau, debut: debut + avant.length, fin: fin + avant.length }
    : { texte: nouveau, debut: debut + avant.length, fin: debut + avant.length }
}
