import { useSyncExternalStore } from "react"
import { toast } from "sonner"

import { API_BASE_URL } from "@/api/client"
import {
  cheminCours, cheminExerciceLecture, cheminLectureCours, cheminThemeExercices, getCours, getEpreuve,
  getExerciceLecture, readCours, readEpreuve,
} from "@/api/endpoints"
import type { ThemeExercicesResponse } from "@/api/types"
import { localeCourante, t } from "@/lib/i18n"

/** Cache Workbox des réponses d'API de lecture - même nom que dans vite.config.ts. */
export const CACHE_LECTURE = "lecture-hors-ligne"

export type TypeContenu = "epreuve" | "cours"

/** Chemins d'API qu'un lecteur charge pour afficher ce contenu (voir EpreuveReaderPage et
 * CoursReaderPage) : c'est très exactement ce qu'il faut avoir en cache pour le relire. */
function cheminsDeLecture(type: TypeContenu, slug: string): string[] {
  return type === "epreuve"
    ? [`/catalog/lessons/${slug}/`, `/access/read/${slug}/`]
    : [cheminCours(slug), cheminLectureCours(slug)]
}

/**
 * Le service worker est un plus, jamais un prérequis : sans lui (navigateur ancien,
 * mode économie de données, interrupteur VITE_DISABLE_PWA=1 au build, serveur de dev),
 * l'app se comporte exactement comme avant. Dans ces cas on désinstalle ce qui traîne :
 * un ancien worker resterait sinon actif indéfiniment sans qu'aucune nouvelle version
 * puisse le remplacer (incident qui avait fait retirer la PWA une première fois).
 */
function nettoyerLesAnciensWorkers() {
  navigator.serviceWorker.getRegistrations().then((registrations) => {
    registrations.forEach((registration) => registration.unregister())
  })
  caches?.keys().then((keys) => keys.forEach((key) => caches.delete(key)))
}

/** L'élève a demandé de garder du contenu pour lire sans réseau : le mode économie de données ne coupe alors plus le service
 * worker (R21). Posé par un geste explicite (« Télécharger ce thème »), jamais par défaut. */
const CLE_HORS_LIGNE_VOULU = "edukora-hors-ligne-voulu"

function horsLigneVoulu(): boolean {
  try {
    return localStorage.getItem(CLE_HORS_LIGNE_VOULU) === "1"
  } catch {
    return false
  }
}

function economieDeDonnees(): boolean {
  return Boolean((navigator as Navigator & { connection?: { saveData?: boolean } }).connection?.saveData)
}

export function initialiserPwa() {
  if (!("serviceWorker" in navigator)) return
  if (
    import.meta.env.DEV || import.meta.env.VITE_DISABLE_PWA === "1" || (economieDeDonnees() && !horsLigneVoulu())
  ) {
    nettoyerLesAnciensWorkers()
    return
  }

  // Après le chargement complet : les ~2 Mo de précache ne doivent jamais concurrencer le
  // premier affichage sur une connexion lente.
  window.addEventListener("load", demarrerLeWorker)
}

async function demarrerLeWorker() {
  {
    const { registerSW } = await import("virtual:pwa-register")
    const mettreAJour = registerSW({
      onNeedRefresh() {
        // Une action, pas un rechargement automatique : la mise à jour ne doit jamais
        // couper un examen chronométré ou une lecture en cours.
        toast(t("gl.pwa_nouvelle"), {
          id: "maj-app",
          description: t("gl.pwa_nouvelle_desc"),
          duration: Infinity,
          action: { label: t("gl.pwa_maj"), onClick: () => mettreAJour(true) },
        })
      },
      onOfflineReady() {
        toast.success(t("gl.pwa_pret"), {
          id: "hors-ligne-pret",
          description: t("gl.pwa_pret_desc"),
        })
      },
    })
  }
}

/**
 * En économie de données le worker est coupé au démarrage ; quand l'élève demande lui-même un téléchargement, on le garde
 * (et on le démarre tout de suite). Renvoie faux quand le navigateur ne peut pas : l'appelant dit alors qu'il n'y a pas de
 * lecture sans réseau possible ici, au lieu de promettre ce qu'il ne tiendra pas.
 */
export async function activerLeHorsLigne(): Promise<boolean> {
  if (typeof caches === "undefined" || !("serviceWorker" in navigator)) return false
  if (import.meta.env.DEV || import.meta.env.VITE_DISABLE_PWA === "1") return false
  try {
    localStorage.setItem(CLE_HORS_LIGNE_VOULU, "1")
  } catch {
    // Stockage refusé : le worker démarre quand même pour cette visite.
  }
  if (!(await navigator.serviceWorker.getRegistration())) await demarrerLeWorker()
  return true
}

function abonnerEnLigne(rappel: () => void) {
  window.addEventListener("online", rappel)
  window.addEventListener("offline", rappel)
  return () => {
    window.removeEventListener("online", rappel)
    window.removeEventListener("offline", rappel)
  }
}

export function useEnLigne(): boolean {
  return useSyncExternalStore(abonnerEnLigne, () => navigator.onLine, () => true)
}

/** À appeler à la déconnexion : sur un téléphone partagé, un corrigé lu hors connexion ne
 * doit pas rester lisible pour le compte suivant. */
export async function viderCacheHorsLigne() {
  try {
    await caches?.delete(CACHE_LECTURE)
  } catch {
    // Cache API absente ou refusée : rien à vider.
  }
}

/** Ce contenu est-il déjà lisible sans réseau ? */
export async function estDisponibleHorsLigne(type: TypeContenu, slug: string): Promise<boolean> {
  try {
    if (!("caches" in window)) return false
    const cache = await caches.open(CACHE_LECTURE)
    const trouves = await Promise.all(
      cheminsDeLecture(type, slug).map((chemin) => cache.match(`${API_BASE_URL}${chemin}`)),
    )
    return trouves.every(Boolean)
  } catch {
    return false
  }
}

/** Charge maintenant ce que le lecteur demandera : le service worker garde chaque réponse
 * au passage. Lecture = téléchargement ; ce geste sert à préparer un trajet sans réseau
 * sans avoir à ouvrir chaque document. */
export async function telechargerPourLireHorsLigne(type: TypeContenu, slug: string) {
  if (type === "epreuve") await Promise.all([getEpreuve(slug), readEpreuve(slug)])
  else await Promise.all([getCours(slug), readCours(slug)])
}

// --- Paquet « Télécharger ce thème » (audit produit 2026-11-13, R21) -----------------------------------------------------

/** Un thème gardé pour lire sans réseau : sa liste d'exercices, ses cours et chaque exercice lisible par l'élève. */
export interface PaquetTheme {
  cursusId: number
  tagId: number
  subject: string
  liste: ThemeExercicesResponse
}

/** Au plus ce nombre d'exercices par paquet : un thème très fréquent en compte des dizaines, et le téléchargement part sur le
 * forfait de l'élève. Les premiers de la liste, celle que la page lui montre, passent d'abord. */
export const EXERCICES_MAX_PAR_PAQUET = 30
const TELECHARGEMENTS_EN_PARALLELE = 4

interface ElementDePaquet {
  chemin: string
  charger: () => Promise<unknown>
}

function elementsDuPaquet({ cursusId, tagId, subject, liste }: PaquetTheme): ElementDePaquet[] {
  const elements: ElementDePaquet[] = [
    { chemin: cheminThemeExercices(cursusId, tagId, subject), charger: async () => liste },
  ]
  for (const cours of liste.cours) {
    elements.push({ chemin: cheminCours(cours.slug), charger: () => getCours(cours.slug) })
    elements.push({ chemin: cheminLectureCours(cours.slug), charger: () => readCours(cours.slug) })
  }
  // Un exercice verrouillé n'a que son énoncé public : rien qui vaille la peine d'être gardé.
  for (const exercice of liste.exercices.filter((e) => e.has_access).slice(0, EXERCICES_MAX_PAR_PAQUET)) {
    elements.push({
      chemin: cheminExerciceLecture(tagId, exercice.exercise_id),
      charger: () => getExerciceLecture(tagId, exercice.exercise_id),
    })
  }
  return elements
}

export function nombreElementsDuPaquet(paquet: PaquetTheme): number {
  return elementsDuPaquet(paquet).length
}

/**
 * Retire un thème gardé pour lire sans réseau (R21) : sa liste, ses cours et ses exercices. Un cours partagé avec un autre thème
 * part avec lui ; l'autre thème n'est alors plus dit disponible et se retélécharge d'un geste.
 */
export async function retirerTheme(paquet: PaquetTheme): Promise<void> {
  try {
    if (!("caches" in window)) return
    const cache = await caches.open(CACHE_LECTURE)
    await Promise.all(elementsDuPaquet(paquet).map((e) => cache.delete(`${API_BASE_URL}${e.chemin}`)))
  } catch {
    // Rien à retirer si le cache n'est pas lisible.
  }
}

/** La place que ce site occupe sur l'appareil, en octets, quand le navigateur sait la dire (sinon null). */
export async function espaceUtilise(): Promise<{ usage: number; quota: number } | null> {
  try {
    const estimation = await navigator.storage?.estimate?.()
    if (!estimation || typeof estimation.usage !== "number") return null
    return { usage: estimation.usage, quota: estimation.quota ?? 0 }
  } catch {
    return null
  }
}

/** « 12,4 Mo », « 830 Ko » (« 12.4 MB », « 830 KB » en anglais) : une taille lisible pour l'élève. */
export function tailleLisible(octets: number): string {
  const anglais = localeCourante().startsWith("en")
  if (octets >= 1024 * 1024) {
    const valeur = (octets / (1024 * 1024)).toFixed(1)
    return anglais ? `${valeur} MB` : `${valeur.replace(".", ",")} Mo`
  }
  return `${Math.max(1, Math.round(octets / 1024))} ${anglais ? "KB" : "Ko"}`
}

/** Ce thème est-il entièrement lisible sans réseau ? */
export async function estThemeDisponibleHorsLigne(paquet: PaquetTheme): Promise<boolean> {
  try {
    if (!("caches" in window)) return false
    const cache = await caches.open(CACHE_LECTURE)
    const trouves = await Promise.all(elementsDuPaquet(paquet).map((e) => cache.match(`${API_BASE_URL}${e.chemin}`)))
    return trouves.every(Boolean)
  } catch {
    return false
  }
}

/**
 * Garde le thème pour lire sans réseau. Chaque réponse est écrite dans le cache de lecture par ce code même, sans attendre
 * que le service worker la voie passer : il peut ne pas encore contrôler la page (premier démarrage, économie de données).
 * `onProgres(faits, total)` après chaque élément ; renvoie le nombre d'échecs (0 = paquet complet).
 */
export async function telechargerTheme(paquet: PaquetTheme, onProgres?: (faits: number, total: number) => void): Promise<number> {
  const elements = elementsDuPaquet(paquet)
  const cache = await caches.open(CACHE_LECTURE)
  let faits = 0
  let echecs = 0
  let suivant = 0
  async function travailler() {
    while (suivant < elements.length) {
      const element = elements[suivant++]
      try {
        const donnees = await element.charger()
        await cache.put(
          `${API_BASE_URL}${element.chemin}`,
          new Response(JSON.stringify(donnees), { headers: { "Content-Type": "application/json" } }),
        )
      } catch {
        echecs += 1
      }
      faits += 1
      onProgres?.(faits, elements.length)
    }
  }
  await Promise.all(Array.from({ length: Math.min(TELECHARGEMENTS_EN_PARALLELE, elements.length) }, travailler))
  return echecs
}
