const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8001"

// Access token gardé en mémoire uniquement, jamais en localStorage/sessionStorage :
// un stockage web reste lisible par n'importe quel script qui s'exécute sur la page
// (XSS), un simple attribut de module ne l'est que par ce module lui-même. Le
// refresh token (plus sensible, longue durée - voir SIMPLE_JWT côté backend) ne
// transite même plus par ce module : il vit dans un cookie httpOnly posé par
// otp_verify_view, jamais accessible à JavaScript, y compris à ce fichier.
//
// Conséquence assumée : un rechargement complet de page perd cet access token (il
// est revalidé au démarrage via un refresh silencieux - voir AuthContext, qui
// appelle refreshAccessToken() une fois au montage) - c'est le compromis normal du
// pattern "access en mémoire, refresh en cookie httpOnly", pas un oubli.
let accessToken: string | null = null

export function getAccessToken() {
  return accessToken
}

export function setAccessToken(token: string) {
  accessToken = token
}

export function clearAccessToken() {
  accessToken = null
}

// Événement DOM plutôt qu'un import direct de sonner/AuthContext ici : ce module n'a
// aucune dépendance React ni UI (utilisable tel quel hors composant), et un event
// bus léger laisse à AuthContext (voir son useEffect dédié) la responsabilité de
// décider quoi faire d'une session expirée - déconnecter l'utilisateur ET l'en
// informer sont deux préoccupations distinctes de "faire une requête API".
export const SESSION_EXPIRED_EVENT = "edukamer:session-expired"

class ApiError extends Error {
  status: number
  body: unknown

  constructor(status: number, body: unknown) {
    const message =
      typeof body === "object" && body !== null && "error" in body
        ? String((body as { error: unknown }).error)
        : `Erreur API (${status})`
    super(message)
    this.status = status
    this.body = body
  }
}

/**
 * Ne prend plus aucun paramètre : le refresh token n'est plus jamais détenu par ce
 * module (voir le commentaire sur `accessToken` ci-dessus), il voyage tout seul via
 * le cookie httpOnly - credentials: "include" est ce qui dit au navigateur de
 * l'attacher à cette requête (nécessaire dès que frontend et API vivent sur des
 * origines distinctes, ex. localhost:5173 -> localhost:8001 en dev), le serveur ne
 * lit rien d'autre pour authentifier cet appel.
 */
async function refreshAccessToken(): Promise<string | null> {
  const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
    method: "POST",
    credentials: "include",
  })
  if (!response.ok) {
    clearAccessToken()
    return null
  }
  const data = await response.json()
  setAccessToken(data.access)
  return data.access as string
}

/**
 * Best-effort : côté serveur, logout_view efface le cookie quoi qu'il arrive (voir sa
 * docstring, AllowAny) - un échec réseau ici ne doit jamais empêcher la déconnexion
 * locale (voir AuthContext.logout, qui appelle ceci sans attendre le résultat).
 */
export async function logoutRequest(): Promise<void> {
  try {
    await fetch(`${API_BASE_URL}/auth/logout/`, { method: "POST", credentials: "include" })
  } catch {
    // Cookie expirera de toute façon à son terme (30j, voir SIMPLE_JWT) si ce
    // round-trip échoue - la déconnexion locale (accessToken effacé, user à null)
    // reste effective immédiatement dans les deux cas.
  }
}

interface RequestOptions {
  method?: string
  body?: unknown
  /**
   * true (défaut) : token requis, tente un refresh puis échoue en ApiError si toujours 401.
   * false : n'attache jamais le token, même s'il existe (endpoint strictement anonyme).
   * "optional" : attache le token s'il existe (pour bénéficier de has_access etc.), mais
   * si la session est invalide/expirée, retombe silencieusement en anonyme plutôt que
   * de casser une page publique (catalogue, détail épreuve...).
   */
  auth?: boolean | "optional"
  /**
   * Passé par TanStack Query (voir api/queries.ts) pour annuler réellement la
   * requête réseau en vol quand une clé de query change avant sa résolution (ex.
   * filtre modifié pendant qu'une recherche précédente est encore en cours) - sans
   * ça, React Query ignore juste la réponse tardive côté state, mais le navigateur
   * continue de télécharger une réponse dont personne ne se sert. `fetch` lève une
   * AbortError native sur un signal annulé, que React Query sait déjà distinguer
   * d'une vraie erreur - rien à gérer de spécial ici.
   */
  signal?: AbortSignal
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, auth = true, signal } = options
  const sendToken = auth === true || auth === "optional"

  const isFormData = body instanceof FormData

  const doFetch = async (token: string | null) => {
    const headers: Record<string, string> = {}
    // FormData : ne jamais fixer Content-Type nous-même - le navigateur doit poser
    // le boundary multipart lui-même, un header explicite ici le corromprait.
    if (!isFormData) headers["Content-Type"] = "application/json"
    if (sendToken && token) headers["Authorization"] = `Bearer ${token}`

    return fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: isFormData ? (body as FormData) : body !== undefined ? JSON.stringify(body) : undefined,
      signal,
      // Nécessaire pour que le navigateur pose/relise le cookie httpOnly du refresh
      // token (voir SESSION_EXPIRED_EVENT plus haut) dès que frontend et API vivent
      // sur des origines distinctes (ex. localhost:5173 -> localhost:8001 en dev) -
      // sans ça, un Set-Cookie cross-origine sur la réponse de /auth/otp/verify/
      // serait silencieusement ignoré par le navigateur. Sans risque de fuite vers
      // des endpoints qui n'en ont pas besoin : le cookie est scopé path=/auth/
      // côté serveur (voir users.views.REFRESH_COOKIE_PATH), le navigateur ne
      // l'attache de toute façon qu'aux requêtes vers ce chemin.
      credentials: "include",
    })
  }

  let response = await doFetch(getAccessToken())

  if (response.status === 401 && sendToken) {
    const refreshed = await refreshAccessToken()
    if (refreshed) {
      response = await doFetch(refreshed)
      // Le refresh a réussi mais la requête rejouée avec le nouveau token 401
      // quand même (ex. compte supprimé entre-temps : le cookie httpOnly de
      // refresh est encore valide, mais JWTAuthentication ne trouve plus
      // l'utilisateur en base). Même repli en anonyme que si le refresh
      // avait échoué d'emblée - sinon une page publique (catalogue, détail
      // épreuve...) casse pour un visiteur qui devrait la voir en anonyme.
      if (response.status === 401 && auth === "optional") {
        response = await doFetch(null)
      }
    } else if (auth === "optional") {
      response = await doFetch(null)
    } else {
      // auth strict (pas "optional") et le refresh a lui-même échoué : la session
      // est réellement terminée, pas juste une page publique qui retombe en
      // anonyme. Le seul signal qu'a cette page pour le savoir avant que
      // l'ApiError 401 ne remonte, potentiellement affichée comme une erreur
      // générique par l'appelant plutôt que comme "reconnecte-toi".
      window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT))
    }
  }

  const contentType = response.headers.get("content-type") ?? ""
  const data = contentType.includes("application/json") ? await response.json() : null

  if (!response.ok) {
    throw new ApiError(response.status, data)
  }

  return data as T
}

export { API_BASE_URL, ApiError }
