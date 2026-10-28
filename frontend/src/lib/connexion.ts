type InfoConnexion = { saveData?: boolean; effectiveType?: string }

/**
 * Vrai quand le navigateur annonce le mode « économie de données » ou une connexion lente (2G/3G).
 * Sert à ne pas lancer de téléchargement qui n'a pas été demandé (pré-chargement « de confort ») :
 * l'élève paie ses octets. `navigator.connection` n'existe pas partout (absent de Safari et de
 * Firefox) : sans l'information, on garde le comportement normal.
 */
export function connexionEconome(): boolean {
  if (typeof navigator === "undefined") return false
  const connexion = (navigator as Navigator & { connection?: InfoConnexion }).connection
  if (!connexion) return false
  return Boolean(connexion.saveData) || ["slow-2g", "2g", "3g"].includes(connexion.effectiveType ?? "")
}
