const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8001"

const ACCESS_KEY = "edukamer_access"
const REFRESH_KEY = "edukamer_refresh"

export function getTokens() {
  return {
    access: localStorage.getItem(ACCESS_KEY),
    refresh: localStorage.getItem(REFRESH_KEY),
  }
}

export function setTokens(access: string, refresh: string) {
  localStorage.setItem(ACCESS_KEY, access)
  localStorage.setItem(REFRESH_KEY, refresh)
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
}

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

async function refreshAccessToken(): Promise<string | null> {
  const { refresh } = getTokens()
  if (!refresh) return null

  const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  })
  if (!response.ok) {
    clearTokens()
    return null
  }
  const data = await response.json()
  localStorage.setItem(ACCESS_KEY, data.access)
  return data.access as string
}

interface RequestOptions {
  method?: string
  body?: unknown
  /**
   * true (défaut) : token requis, tente un refresh puis échoue en ApiError si toujours 401.
   * false : n'attache jamais le token, même s'il existe (endpoint strictement anonyme).
   * "optional" : attache le token s'il existe (pour bénéficier de has_access etc.), mais
   * si la session est invalide/expirée, retombe silencieusement en anonyme plutôt que
   * de casser une page publique (catalogue, détail leçon...).
   */
  auth?: boolean | "optional"
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, auth = true } = options
  const sendToken = auth === true || auth === "optional"

  const doFetch = async (accessToken: string | null) => {
    const headers: Record<string, string> = { "Content-Type": "application/json" }
    if (sendToken && accessToken) headers["Authorization"] = `Bearer ${accessToken}`

    return fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  }

  let { access } = getTokens()
  let response = await doFetch(access)

  if (response.status === 401 && sendToken) {
    const refreshed = await refreshAccessToken()
    if (refreshed) {
      response = await doFetch(refreshed)
    } else if (auth === "optional") {
      response = await doFetch(null)
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
