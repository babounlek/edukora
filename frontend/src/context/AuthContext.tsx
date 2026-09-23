import { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import { toast } from "sonner"

import { getMe, updateMe } from "@/api/endpoints"
import { clearAccessToken, logoutRequest, setAccessToken, SESSION_EXPIRED_EVENT } from "@/api/client"
import type { User } from "@/api/types"
import { lireCursusPrepareEnAttente, oublierCursusPrepareEnAttente } from "@/lib/cursusPrepare"

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (access: string, user: User) => void
  logout: () => void
  updateUser: (user: User) => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Pas de vérification préalable "a-t-on un access token" : il n'existe qu'en
  // mémoire (voir api/client.ts) et ne survit jamais à un rechargement de page. On
  // tente donc systématiquement getMe() au montage - sans token, le premier appel
  // répond 401, ce qui déclenche déjà le mécanisme de refresh intégré à apiRequest
  // (voir client.ts) : le cookie httpOnly du refresh token, lui, a bien survécu au
  // rechargement. Résultat silencieux dans les deux cas : reconnecté si le cookie
  // est encore valide, sinon simplement déconnecté (catch vide, rien à faire de plus
  // - clearAccessToken() a déjà été appelé par refreshAccessToken() en cas d'échec).
  useEffect(() => {
    getMe()
      .then(setUser)
      .catch(() => {})
      .finally(() => setIsLoading(false))
  }, [])

  // Émis par api/client.ts quand une requête strictement authentifiée échoue même
  // après tentative de rafraîchissement - le seul point d'entrée qui sait qu'une
  // session est réellement terminée, potentiellement depuis n'importe quelle page.
  // setUser(null) directement (pas d'appel à logout() plus bas) : accessToken a déjà
  // été effacé côté client.ts au moment du refresh raté, inutile de le refaire ; ne
  // reste que la synchronisation du state React, sinon Header/AccountPage
  // continueraient d'afficher un utilisateur connecté jusqu'au prochain rechargement.
  useEffect(() => {
    function handleSessionExpired() {
      setUser(null)
      toast.error("Session expirée", { description: "Reconnecte-toi pour continuer." })
    }
    window.addEventListener(SESSION_EXPIRED_EVENT, handleSessionExpired)
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, handleSessionExpired)
  }, [])

  // Un visiteur qui déclare son examen AVANT de se connecter (l'onboarding s'affiche
  // dès la première visite, bien avant toute inscription) ne doit pas avoir à le
  // redire une fois son compte créé : sa déclaration attendait en localStorage, on la
  // pousse ici, à la première session où il est connecté.
  //
  // Jamais par-dessus une déclaration déjà faite sur le compte (celle-ci est plus
  // récente que ce qui traîne dans le stockage d'un navigateur), et la valeur en
  // attente est oubliée dans tous les cas - y compris en cas d'échec : la reproposer
  // à chaque montage transformerait un aller-retour raté en boucle silencieuse.
  useEffect(() => {
    if (user === null) return
    const enAttente = lireCursusPrepareEnAttente()
    if (enAttente === null) return
    oublierCursusPrepareEnAttente()
    if (user.cursus_prepare !== null) return
    updateMe({ cursus_prepare: enAttente })
      .then(setUser)
      .catch(() => {})
  }, [user])

  function login(access: string, newUser: User) {
    setAccessToken(access)
    setUser(newUser)
  }

  function logout() {
    clearAccessToken()
    setUser(null)
    // Résultat jamais attendu (voir logoutRequest, best-effort) : l'utilisateur doit
    // se sentir déconnecté immédiatement, pas après un aller-retour réseau pour
    // effacer un cookie qu'il ne voit de toute façon jamais.
    void logoutRequest()
  }

  return (
    <AuthContext.Provider
      value={{ user, isLoading, isAuthenticated: user !== null, login, logout, updateUser: setUser }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}
