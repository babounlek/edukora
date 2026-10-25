// Le défi entre camarades : « j'ai fait 4/5, fais mieux ». Rien côté serveur - le score à battre voyage dans le lien
// (?defi=4-5), le visiteur qui l'ouvre le garde le temps de sa visite (sessionStorage) et le compare à son propre résultat.
// Un score dans un lien est invérifiable, et c'est voulu : c'est un jeu entre amis, il ne donne ni point ni avantage.
// Aucun nom, aucune donnée personnelle : « un camarade ».
const CLE = "edukora:defi-essai"

export interface Defi {
  reussies: number
  total: number
}

/** Le paramètre à mettre dans le lien qu'on partage. */
export function parametresDefi(reussies: number, total: number): Record<string, string> {
  return { defi: `${reussies}-${total}` }
}

/** Le défi d'un lien (« ?defi=4-5 »), ou null s'il est absent ou invraisemblable (le lien vient de n'importe qui). */
export function lireDefiDepuis(recherche: string): Defi | null {
  const valeur = new URLSearchParams(recherche).get("defi")
  const m = valeur ? /^(\d{1,2})-(\d{1,2})$/.exec(valeur) : null
  if (!m) return null
  const reussies = Number(m[1])
  const total = Number(m[2])
  return total >= 1 && total <= 30 && reussies <= total ? { reussies, total } : null
}

export function memoriserDefi(defi: Defi | null) {
  try {
    if (defi) sessionStorage.setItem(CLE, JSON.stringify(defi))
    else sessionStorage.removeItem(CLE)
  } catch {
    // Stockage indisponible : le défi ne vit alors que le temps de la page, sans gravité.
  }
}

export function lireDefiMemorise(): Defi | null {
  try {
    const brut = sessionStorage.getItem(CLE)
    if (!brut) return null
    // Relu par la même validation que celle d'un lien : un stockage altéré ne passe pas.
    const { reussies, total } = JSON.parse(brut) as Defi
    return lireDefiDepuis(`defi=${reussies}-${total}`)
  } catch {
    return null
  }
}

export type IssueDefi = "gagne" | "egalite" | "perdu"

/** Comparaison en proportion : un quiz de 5 et un de 10 questions restent comparables. */
export function comparerDefi(defi: Defi, reussies: number, total: number): IssueDefi {
  const moi = reussies * defi.total
  const lui = defi.reussies * total
  return moi > lui ? "gagne" : moi === lui ? "egalite" : "perdu"
}
