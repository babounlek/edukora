import { Component, type ErrorInfo, type ReactNode } from "react"
import { AlertTriangle, RefreshCw } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Sentry } from "@/lib/sentry"

// Messages observés selon le navigateur quand un chunk lazy (voir App.tsx, React.lazy)
// ne charge plus après un déploiement : l'onglet reste ouvert avec l'ancien
// index.html/manifeste de chunks, dont les noms de fichiers (hash de contenu) ne
// correspondent plus à rien sur le serveur. Ce n'est jamais une erreur applicative -
// recharger la page suffit toujours à la résoudre puisque ça retélécharge le nouveau
// index.html avec les bons chemins.
const CHUNK_LOAD_FAILURE_RE =
  /failed to fetch dynamically imported module|error loading dynamically imported module|importing a module script failed/i

// Clé sessionStorage plutôt qu'un simple booléen en mémoire : un rechargement complet
// de la page (window.location.reload()) réinitialise tout l'état React, la seule façon
// de savoir "on a déjà tenté un rechargement automatique pour CETTE navigation" après
// coup est un stockage qui survit au reload lui-même.
const CHUNK_RELOAD_ATTEMPTED_KEY = "edukamer_chunk_reload_attempted"

interface Props {
  children: ReactNode
}

interface State {
  error: Error | null
}

/**
 * Filet de sécurité au-dessus des routes lazy (voir App.tsx) : sans lui, un chunk qui
 * échoue à charger - ou n'importe quelle autre erreur de rendu imprévue - laisse un
 * écran blanc sans aucune échappatoire pour l'utilisateur. Une erreur de chunk se
 * corrige d'elle-même par un simple rechargement (tenté une fois automatiquement,
 * silencieusement) ; toute autre erreur affiche un message avec un bouton de secours,
 * plutôt que de laisser deviner si l'app a juste planté ou s'il faut réessayer.
 */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Erreur applicative interceptée par ErrorBoundary :", error, info.componentStack)
    // Un chunk introuvable après déploiement est filtré côté init (voir lib/sentry.ts,
    // ignoreErrors) - pas besoin de le re-exclure ici, une seule source de vérité pour
    // ce qui est du bruit attendu.
    Sentry.captureException(error, { contexts: { react: { componentStack: info.componentStack } } })
  }

  // Les deux hooks sont nécessaires, pas juste componentDidUpdate : quand l'erreur
  // survient dès le tout premier montage du boundary (ex. le tout premier chunk
  // lazy visité échoue sur un réseau capricieux, pas seulement après un déploiement)
  // React inclut l'état d'erreur directement dans ce premier commit - componentDidMount
  // se déclenche alors, jamais componentDidUpdate, qui ne réagit qu'aux montées de
  // version ultérieures. Sans componentDidMount ici, ce cas précis restait bloqué sur
  // un écran vide (voir isChunkLoadFailure -> render() retourne null) sans jamais
  // déclencher le rechargement automatique censé le résoudre.
  componentDidMount() {
    this.maybeAutoReload()
  }

  componentDidUpdate() {
    this.maybeAutoReload()
  }

  maybeAutoReload() {
    if (!this.state.error || !this.isChunkLoadFailure()) return
    if (sessionStorage.getItem(CHUNK_RELOAD_ATTEMPTED_KEY)) return

    sessionStorage.setItem(CHUNK_RELOAD_ATTEMPTED_KEY, "1")
    window.location.reload()
  }

  isChunkLoadFailure() {
    return CHUNK_LOAD_FAILURE_RE.test(this.state.error?.message ?? "")
  }

  handleReload = () => {
    sessionStorage.removeItem(CHUNK_RELOAD_ATTEMPTED_KEY)
    window.location.reload()
  }

  render() {
    if (!this.state.error) return this.props.children

    // Rechargement automatique en cours (voir componentDidUpdate) : rien d'utile à
    // montrer, la page va se recharger dans l'instant qui suit.
    if (this.isChunkLoadFailure() && !sessionStorage.getItem(CHUNK_RELOAD_ATTEMPTED_KEY)) {
      return null
    }

    const isStillChunkFailure = this.isChunkLoadFailure()

    return (
      <div className="mx-auto flex min-h-[60vh] max-w-md flex-col items-center justify-center gap-3 px-4 text-center">
        <AlertTriangle className="size-8 text-warning" />
        <p className="font-display text-lg font-medium">
          {isStillChunkFailure ? "Une nouvelle version de l'app est disponible" : "Une erreur inattendue est survenue"}
        </p>
        <p className="text-sm text-muted-foreground">
          {isStillChunkFailure
            ? "Le rechargement automatique n'a pas suffi - réessaie manuellement."
            : "Recharge la page pour continuer. Si le problème persiste, réessaie un peu plus tard."}
        </p>
        <Button onClick={this.handleReload} size="lg">
          <RefreshCw />
          Recharger la page
        </Button>
      </div>
    )
  }
}
