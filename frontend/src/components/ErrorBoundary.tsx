import { Component, type ErrorInfo, type ReactNode } from "react"
import { useLocation } from "react-router-dom"
import { AlertTriangle, RefreshCw } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Sentry } from "@/lib/sentry"
import { t } from "@/lib/i18n"

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
  /**
   * Efface l'erreur dès que l'adresse (pathname) change. Réservé à un filet posé SOUS le routeur (celui des routes,
   * voir App.tsx) : sans cela, une page en erreur bloquait toutes les suivantes, l'en-tête et les onglets ne menaient
   * plus nulle part et seul « Recharger la page » débloquait l'élève.
   */
  reinitialiserSurNavigation?: boolean
}

interface LimiteProps {
  children: ReactNode
  /** Une valeur qui, en changeant, efface l'erreur (ici l'adresse de la page). */
  cleReinitialisation?: string
}

interface State {
  error: Error | null
  /** La clé de réinitialisation du dernier rendu, pour voir qu'elle a changé (voir getDerivedStateFromProps). */
  cle?: string
}

/**
 * Filet de sécurité au-dessus des routes lazy (voir App.tsx) : sans lui, un chunk qui
 * échoue à charger - ou n'importe quelle autre erreur de rendu imprévue - laisse un
 * écran blanc sans aucune échappatoire pour l'utilisateur. Une erreur de chunk se
 * corrige d'elle-même par un simple rechargement (tenté une fois automatiquement,
 * silencieusement) ; toute autre erreur affiche un message avec un bouton de secours,
 * plutôt que de laisser deviner si l'app a juste planté ou s'il faut réessayer.
 */
export function ErrorBoundary({ children, reinitialiserSurNavigation = false }: Props) {
  // Deux composants plutôt qu'un hook conditionnel : useLocation n'existe que sous un routeur, et le filet de
  // main.tsx, posé au-dessus de toute l'app, n'en a pas.
  if (reinitialiserSurNavigation) return <LimiteSurNavigation>{children}</LimiteSurNavigation>
  return <LimiteErreur>{children}</LimiteErreur>
}

function LimiteSurNavigation({ children }: { children: ReactNode }) {
  const { pathname } = useLocation()
  return <LimiteErreur cleReinitialisation={pathname}>{children}</LimiteErreur>
}

class LimiteErreur extends Component<LimiteProps, State> {
  state: State = { error: null }

  // L'élève a changé de page : l'erreur de la page précédente est retirée AVANT le rendu, la nouvelle page se rend
  // directement. Quand c'est la page d'arrivée elle-même qui plante, l'erreur arrive après ce calcul (dans le même
  // rendu, la clé est déjà à jour) : elle reste affichée, sans être effacée puis relancée une seconde fois.
  // Un chunk introuvable garde son propre garde : déjà rechargé une fois (CHUNK_RELOAD_ATTEMPTED_KEY), un nouvel
  // échec sur la page suivante affiche le message manuel au lieu de recharger en boucle.
  static getDerivedStateFromProps(props: LimiteProps, state: State): Partial<State> | null {
    if (props.cleReinitialisation === state.cle) return null
    return { cle: props.cleReinitialisation, error: null }
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
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
          {isStillChunkFailure ? t("gl.eb_nouvelle") : t("gl.eb_erreur")}
        </p>
        <p className="text-sm text-muted-foreground">
          {isStillChunkFailure
            ? t("gl.eb_echec_reload")
            : t("gl.eb_reload_texte")}
        </p>
        <Button onClick={this.handleReload} size="lg">
          <RefreshCw />
          {t("gl.eb_bouton")}
        </Button>
      </div>
    )
  }
}
