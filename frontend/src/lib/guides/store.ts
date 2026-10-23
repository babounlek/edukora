import type { DonneesGuides, MemoireGuide, StatutGuide } from "./types"

/**
 * La mémoire des guides : quels guides cet élève a terminés ou écartés, à quelle version,
 * et ses préférences d'affichage.
 *
 * Tout passe par ce module - aucun autre fichier ne touche à la clé de stockage. Il est
 * écrit pour ne JAMAIS lever d'exception : stockage absent (navigation privée), plein,
 * bloqué par le navigateur, ou contenu altéré à la main. Dans tous ces cas on retombe sur
 * une copie en mémoire pour la durée de la page, et l'élève voit simplement le comportement
 * d'un premier passage.
 *
 * Local à l'appareil et au navigateur : rien n'est synchronisé entre les appareils d'un même
 * élève (pas de champ de préférences côté compte, et en créer un n'était pas justifié pour
 * des conseils de prise en main). Un élève qui change de téléphone revoit donc le tutoriel.
 */

const PREFIXE = "edukora:guides:"

/** Repli quand localStorage est inutilisable : vit le temps de la page. */
const memoire = new Map<string, string>()

function vide(): DonneesGuides {
  return { v: 1, guides: {}, prefs: { aidesAuto: true } }
}

function lireBrut(cle: string): string | null {
  try {
    return localStorage.getItem(cle) ?? memoire.get(cle) ?? null
  } catch {
    return memoire.get(cle) ?? null
  }
}

function ecrireBrut(cle: string, valeur: string) {
  try {
    localStorage.setItem(cle, valeur)
    memoire.delete(cle)
  } catch {
    // Stockage indisponible ou plein : la copie en mémoire suffit pour cette page.
    memoire.set(cle, valeur)
  }
}

function estMemoire(valeur: unknown): valeur is MemoireGuide {
  if (typeof valeur !== "object" || valeur === null) return false
  const v = valeur as Record<string, unknown>
  return (
    typeof v.version === "number" && Number.isFinite(v.version)
    && (v.statut === "termine" || v.statut === "ignore")
  )
}

/** Relit et assainit : une donnée invalide est écartée entrée par entrée, jamais tout le reste avec elle. */
function analyser(brut: string | null): DonneesGuides {
  const donnees = vide()
  if (!brut) return donnees
  try {
    const lu: unknown = JSON.parse(brut)
    if (typeof lu !== "object" || lu === null) return donnees
    const objet = lu as Record<string, unknown>
    if (objet.v !== 1) return donnees
    if (typeof objet.guides === "object" && objet.guides !== null) {
      for (const [id, valeur] of Object.entries(objet.guides)) {
        if (estMemoire(valeur)) {
          donnees.guides[id] = { version: valeur.version, statut: valeur.statut, date: Number(valeur.date) || 0 }
        }
      }
    }
    const prefs = objet.prefs as Record<string, unknown> | undefined
    if (prefs && typeof prefs.aidesAuto === "boolean") donnees.prefs.aidesAuto = prefs.aidesAuto
  } catch {
    // JSON illisible : on repart d'une mémoire vide.
  }
  return donnees
}

export function cleDeLIdentite(identite: string): string {
  return `${PREFIXE}${identite}`
}

export function lireDonnees(identite: string): DonneesGuides {
  return analyser(lireBrut(cleDeLIdentite(identite)))
}

function ecrireDonnees(identite: string, donnees: DonneesGuides) {
  ecrireBrut(cleDeLIdentite(identite), JSON.stringify(donnees))
}

/**
 * Ce guide doit-il (re)devenir proposable ? Oui s'il n'a jamais été vu, ou si la version
 * mémorisée est plus ancienne que la version courante de sa définition.
 */
export function estAJour(donnees: DonneesGuides, id: string, version: number): boolean {
  const vu = donnees.guides[id]
  return Boolean(vu) && vu.version >= version
}

export function memoriser(identite: string, id: string, version: number, statut: StatutGuide) {
  const donnees = lireDonnees(identite)
  donnees.guides[id] = { version, statut, date: Date.now() }
  ecrireDonnees(identite, donnees)
}

export function definirAidesAuto(identite: string, actif: boolean) {
  const donnees = lireDonnees(identite)
  donnees.prefs.aidesAuto = actif
  ecrireDonnees(identite, donnees)
}

/** Oublie ce que l'élève a vu (pas ses préférences) : « tout revoir depuis le début ». */
export function toutOublier(identite: string) {
  const donnees = lireDonnees(identite)
  donnees.guides = {}
  ecrireDonnees(identite, donnees)
}

/**
 * Un visiteur anonyme qui se connecte ne doit pas revoir ce qu'il vient de fermer : on
 * reporte sa mémoire sur le compte, SANS jamais écraser ce que le compte a déjà (le compte
 * est plus précis que ce qui traîne dans un navigateur partagé). Sans effet si le compte
 * n'a rien d'écrit à compléter ou si l'anonyme n'a rien vu.
 */
export function reporterAnonymeSur(identiteCompte: string, identiteAnonyme = "anonyme") {
  if (identiteCompte === identiteAnonyme) return
  const anonyme = lireDonnees(identiteAnonyme)
  const ids = Object.keys(anonyme.guides)
  if (ids.length === 0) return
  const compte = lireDonnees(identiteCompte)
  let modifie = false
  for (const id of ids) {
    const deja = compte.guides[id]
    if (!deja || deja.version < anonyme.guides[id].version) {
      compte.guides[id] = anonyme.guides[id]
      modifie = true
    }
  }
  if (modifie) ecrireDonnees(identiteCompte, compte)
}

/** Pour les tests : repart d'un état propre, mémoire de repli comprise. */
export function reinitialiserStockage() {
  memoire.clear()
  try {
    for (const cle of Object.keys(localStorage)) {
      if (cle.startsWith(PREFIXE)) localStorage.removeItem(cle)
    }
  } catch {
    // rien à nettoyer
  }
}
