import { useEffect, useRef, useState } from "react"

const GSI_SCRIPT_SRC = "https://accounts.google.com/gsi/client"
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined

interface GoogleCredentialResponse {
  credential: string
}

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string
            callback: (response: GoogleCredentialResponse) => void
            cancel_on_tap_outside?: boolean
          }) => void
          renderButton: (parent: HTMLElement, options: Record<string, unknown>) => void
        }
      }
    }
  }
}

/**
 * Charge le script une seule fois pour toute la session, même si le composant est
 * monté puis démonté plusieurs fois (aller-retour entre connexion et compte) : deux
 * balises concurrentes réinitialiseraient la librairie Google en plein rendu.
 */
let scriptPromise: Promise<void> | null = null

function loadGoogleScript(): Promise<void> {
  if (scriptPromise) return scriptPromise
  scriptPromise = new Promise((resolve, reject) => {
    if (window.google?.accounts?.id) {
      resolve()
      return
    }
    const script = document.createElement("script")
    script.src = GSI_SCRIPT_SRC
    script.async = true
    script.defer = true
    script.onload = () => resolve()
    script.onerror = () => {
      // La promesse est remise à zéro pour qu'une prochaine tentative recharge
      // vraiment le script - sans ça, une coupure réseau passagère désactiverait
      // la connexion Google jusqu'au rechargement complet de la page.
      scriptPromise = null
      reject(new Error("Script Google indisponible"))
    }
    document.head.appendChild(script)
  })
  return scriptPromise
}

interface GoogleSignInButtonProps {
  onCredential: (credential: string) => void
  disabled?: boolean
  /**
   * Affiche un séparateur « ou » au-dessus du bouton. Vrai sur l'écran de connexion,
   * où Google est une ALTERNATIVE au formulaire téléphone. Faux ailleurs - sur la page
   * compte, le bouton sert à RATTACHER une méthode supplémentaire, et un « ou » y
   * laisserait croire à un choix exclusif entre le numéro et Google.
   */
  withSeparator?: boolean
}

/**
 * Bouton officiel « Continuer avec Google ». Rendu par Google lui-même plutôt que
 * redessiné à la main : les conditions d'utilisation de Sign in with Google imposent
 * son apparence, et c'est aussi ce que les élèves reconnaissent au premier coup d'œil.
 *
 * Ne rend rien du tout si VITE_GOOGLE_CLIENT_ID n'est pas configuré - un bouton qui
 * échouerait au clic serait pire que pas de bouton, et le backend répond de toute
 * façon 503 dans ce cas (voir users.google).
 */
export function GoogleSignInButton({ onCredential, disabled, withSeparator }: GoogleSignInButtonProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [indisponible, setIndisponible] = useState(false)
  // Référence plutôt qu'état : le callback est passé à Google une seule fois, à
  // l'initialisation, et doit toujours appeler la version la plus récente du
  // gestionnaire sans pour autant réinitialiser la librairie à chaque rendu.
  const onCredentialRef = useRef(onCredential)
  onCredentialRef.current = onCredential

  useEffect(() => {
    if (!GOOGLE_CLIENT_ID) {
      setIndisponible(true)
      return
    }
    let annule = false

    loadGoogleScript()
      .then(() => {
        if (annule || !containerRef.current || !window.google) return
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: (response) => onCredentialRef.current(response.credential),
          cancel_on_tap_outside: true,
        })
        window.google.accounts.id.renderButton(containerRef.current, {
          type: "standard",
          theme: "outline",
          size: "large",
          text: "continue_with",
          shape: "pill",
          locale: "fr",
          width: containerRef.current.offsetWidth || undefined,
        })
      })
      .catch(() => {
        if (!annule) setIndisponible(true)
      })

    return () => {
      annule = true
    }
  }, [])

  // Le séparateur appartient au composant, pas à la page : sans ça, un « OU »
  // resterait affiché tout seul sous le formulaire partout où la connexion Google
  // n'est pas configurée - c'est-à-dire par défaut.
  if (indisponible) return null

  return (
    <>
      {withSeparator && (
        <div className="my-4 flex items-center gap-3">
          <span className="h-px flex-1 bg-border" />
          <span className="text-xs uppercase tracking-wide text-muted-foreground">ou</span>
          <span className="h-px flex-1 bg-border" />
        </div>
      )}
      <div
        ref={containerRef}
        className="flex justify-center [&>div]:w-full"
        aria-busy={disabled}
        style={disabled ? { pointerEvents: "none", opacity: 0.6 } : undefined}
      />
    </>
  )
}
