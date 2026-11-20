// Les jalons déjà montrés à l'élève sur CET appareil, par profil : de quoi fêter un jalon au moment où il arrive, une seule
// fois. Le serveur ne stocke pas les jalons (ils se relisent sur des faits d'étude, voir quiz.reussites) et ne sait donc pas
// lequel vient d'être franchi ; la différence se fait ici. Simple confort : sans stockage, rien n'est fêté, rien ne casse.

const PREFIXE = "edukora:jalons-vus:"

// Sur un appareil qui n'a encore rien retenu, un compte ancien arrive avec tous ses jalons d'un coup : on ne les fête pas
// en rafale. Jusqu'à ce nombre, c'est un élève qui débute, et ses premiers jalons se fêtent.
const PREMIERS_JALONS_FETES = 2

function lire(profilId: number): string[] | null {
  try {
    const brut = window.localStorage.getItem(PREFIXE + profilId)
    if (brut === null) return null
    const liste: unknown = JSON.parse(brut)
    return Array.isArray(liste) ? liste.filter((c): c is string => typeof c === "string") : null
  } catch {
    return null
  }
}

function ecrire(profilId: number, codes: string[]): boolean {
  try {
    window.localStorage.setItem(PREFIXE + profilId, JSON.stringify(codes))
    return true
  } catch {
    return false
  }
}

/** Retient ces jalons comme déjà vus, sans rien fêter (la page « Ma progression » les montre tous). */
export function marquerJalonsVus(profilId: number, obtenus: string[]) {
  ecrire(profilId, [...new Set([...(lire(profilId) ?? []), ...obtenus])])
}

/** Les jalons obtenus que cet appareil n'a encore jamais montrés - et les retient : le second appel ne rend plus rien. */
export function nouveauxJalons(profilId: number, obtenus: string[]): string[] {
  const vus = lire(profilId)
  const nouveaux = vus === null ? (obtenus.length <= PREMIERS_JALONS_FETES ? obtenus : []) : obtenus.filter((c) => !vus.includes(c))
  // Stockage refusé : on ne fête rien, sinon le même jalon reviendrait à chaque quiz.
  if (!ecrire(profilId, [...new Set([...(vus ?? []), ...obtenus])])) return []
  return nouveaux
}
