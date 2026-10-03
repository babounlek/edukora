import { abonnerPush, desabonnerPush, getPushCle } from "@/api/endpoints"

// Notifications push du navigateur : le rappel du jour, à l'heure où l'élève travaille d'habitude
// (voir relances.push côté backend). Accepter la permission du navigateur EST le consentement.
//
// Quatre états, du plus simple au plus actionnable :
//  - "indisponible" : ni service worker ni PushManager (navigateur ancien, iPhone hors appli
//    installée), pas de worker enregistré (mode économie de données, serveur de dev), ou push
//    non configuré côté serveur : on n'affiche alors rien ;
//  - "refuse"       : l'élève a bloqué les notifications dans le navigateur - seul lui peut les
//    rouvrir, on le lui dit plutôt que de redemander ;
//  - "inactif"      : possible, pas encore activé ;
//  - "actif"        : cet appareil est abonné.

export type EtatPush = "indisponible" | "refuse" | "inactif" | "actif"

export function pushSupporte(): boolean {
  return (
    typeof window !== "undefined" && "serviceWorker" in navigator && "PushManager" in window && "Notification" in window
  )
}

/** Le worker enregistré, sans jamais attendre indéfiniment : `serviceWorker.ready` ne se résout
 * jamais quand aucun worker n'est enregistré (mode économie de données, serveur de dev). */
async function enregistrement(): Promise<ServiceWorkerRegistration | undefined> {
  return navigator.serviceWorker.getRegistration()
}

/** La clé publique VAPID (base64url) telle que `pushManager.subscribe` l'attend. */
export function cleEnOctets(cle: string): Uint8Array<ArrayBuffer> {
  const rembourrage = "=".repeat((4 - (cle.length % 4)) % 4)
  const base64 = (cle + rembourrage).replace(/-/g, "+").replace(/_/g, "/")
  const brut = atob(base64)
  const octets = new Uint8Array(new ArrayBuffer(brut.length))
  for (let i = 0; i < brut.length; i++) octets[i] = brut.charCodeAt(i)
  return octets
}

export async function etatPush(): Promise<EtatPush> {
  if (!pushSupporte()) return "indisponible"
  const reg = await enregistrement()
  if (!reg) return "indisponible"
  try {
    const { actif } = await getPushCle()
    if (!actif) return "indisponible"
  } catch {
    return "indisponible"
  }
  if (Notification.permission === "denied") return "refuse"
  const abonnement = await reg.pushManager.getSubscription()
  return abonnement && Notification.permission === "granted" ? "actif" : "inactif"
}

/** Demande la permission puis abonne cet appareil. Renvoie l'état obtenu : "refuse" si l'élève
 * décline (ou l'avait déjà fait), "indisponible" si quelque chose manque côté serveur. */
export async function activerPush(): Promise<EtatPush> {
  if (!pushSupporte()) return "indisponible"
  const reg = await enregistrement()
  if (!reg) return "indisponible"
  const { actif, cle } = await getPushCle()
  if (!actif) return "indisponible"

  const permission = await Notification.requestPermission()
  if (permission !== "granted") return permission === "denied" ? "refuse" : "inactif"

  const abonnement =
    (await reg.pushManager.getSubscription()) ??
    (await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: cleEnOctets(cle) }))
  const json = abonnement.toJSON()
  if (!json.endpoint || !json.keys?.p256dh || !json.keys?.auth) return "indisponible"
  await abonnerPush({ endpoint: json.endpoint, keys: { p256dh: json.keys.p256dh, auth: json.keys.auth } })
  return "actif"
}

/** Coupe les notifications de cet appareil : côté serveur d'abord (tant que la session est
 * ouverte), puis dans le navigateur. */
export async function desactiverPush(): Promise<void> {
  if (!pushSupporte()) return
  const abonnement = await (await enregistrement())?.pushManager.getSubscription()
  if (!abonnement) return
  await desabonnerPush(abonnement.endpoint).catch(() => {})
  await abonnement.unsubscribe()
}

/**
 * À la déconnexion : sur un téléphone partagé, le compte suivant ne doit pas recevoir les rappels
 * du précédent. Désabonne le NAVIGATEUR seulement (la session est déjà fermée, on ne peut plus
 * appeler le serveur) : le service push répond « disparu » au prochain envoi, et le serveur oublie
 * alors l'appareil (voir relances.push.envoyer_a_l_appareil).
 */
export async function oublierPushLocal(): Promise<void> {
  try {
    if (!pushSupporte()) return
    const abonnement = await (await enregistrement())?.pushManager.getSubscription()
    await abonnement?.unsubscribe()
  } catch {
    // Jamais au prix de la déconnexion.
  }
}
