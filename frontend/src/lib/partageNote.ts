/**
 * Partager une note avec un camarade (WhatsApp surtout) : le texte de la note, sa citation, et un lien vers la PAGE PUBLIQUE
 * d'où elle vient (la fiche du cours ou de l'épreuve, jamais le lecteur payant ni un quiz personnel).
 */

/** La page à ouvrir chez l'ami : la source sans section, sans paramètres, et sans « /lire » (le lecteur est réservé aux abonnés). */
export function cheminPublicDeLaSource(source?: string): string {
  if (!source) return "/"
  const chemin = source.split("#")[0].split("?")[0]
  // Un quiz ou son historique sont personnels : rien d'utile à ouvrir chez quelqu'un d'autre.
  if (chemin.includes("/quiz/") || chemin.includes("/historique/")) return "/"
  return chemin.replace(/\/lire$/, "") || "/"
}

/** WhatsApp met en gras avec une seule étoile : « **gras** » (Markdown) devient « *gras* », et les « $ » des formules disparaissent. */
function enTexteDeMessage(markdown: string): string {
  return markdown.replace(/\*\*(.+?)\*\*/gs, "*$1*").replace(/\$/g, "").trim()
}

export function texteDeNotePartagee(
  { matiere, note, citation }: { matiere: string; note: string; citation?: string },
  entete: string,
): string {
  const morceaux = [`${entete} · ${matiere}`]
  if (citation) morceaux.push(`« ${enTexteDeMessage(citation).slice(0, 240)} »`)
  if (note) morceaux.push(enTexteDeMessage(note))
  return morceaux.join("\n\n")
}
