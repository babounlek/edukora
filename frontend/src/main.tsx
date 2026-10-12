import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { MutationCache, QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { toast } from 'sonner'
import 'katex/dist/katex.min.css'
import 'flag-icons/css/flag-icons.min.css'
import '@fontsource/work-sans/400.css'
import '@fontsource/work-sans/500.css'
import '@fontsource/work-sans/600.css'
import '@fontsource/work-sans/700.css'
import '@fontsource/fraunces/400.css'
import '@fontsource/fraunces/500-italic.css'
import '@fontsource/fraunces/600.css'
import '@fontsource/fraunces/700.css'
import './index.css'
import App from './App.tsx'
import { captureReferralCode } from '@/lib/referral'
import { initialiserPwa } from '@/lib/pwa'
import { initSentry } from '@/lib/sentry'
import { ApiError } from '@/api/client'
import { ErrorBoundary } from '@/components/ErrorBoundary'

// Avant tout le reste : capte les erreurs de rendu les plus précoces possible (voir
// lib/sentry.ts - inerte tant que VITE_SENTRY_DSN n'est pas renseigné au build).
initSentry()

// Un lien de parrainage est toujours cliqué depuis l'extérieur (WhatsApp, réseaux
// sociaux) donc toujours un chargement de page complet, jamais une navigation
// interne à l'app - un appel unique ici suffit, pas besoin de suivre les
// changements de route.
captureReferralCode()

// staleTime > 0 par défaut : le catalogue/les fiches épreuve ne changent pas d'une
// minute à l'autre pour un même visiteur - sans ça, TanStack Query revalide par
// défaut à chaque montage de composant (retour en arrière, changement d'onglet...),
// ce qui annule une bonne part du gain de cache par rapport au fetch manuel
// précédent. refetchOnWindowFocus désactivé pour la même raison : utile pour un
// dashboard qui affiche des données qui bougent, pas pour du contenu pédagogique.
//
// retry : le défaut de TanStack (3 reprises, avec attente croissante) fait attendre environ 7 s
// avant d'afficher une erreur 404 ou 403, qu'aucune reprise ne corrigera. On ne rejoue donc
// que les pannes possiblement passagères (réseau, délai dépassé, erreur serveur), deux fois.
const queryClient = new QueryClient({
  mutationCache: new MutationCache({
    // Filet pour les gestes qui n'ont pas leur propre message : sans lui, un clic qui échoue
    // (« J'ai fini », choix de durée...) ne produit aucun retour. Les mutations qui gèrent
    // déjà leur erreur (onError) restent seules maîtresses de leur message.
    onError: (error, _variables, _context, mutation) => {
      if (mutation.options.onError) return
      if (error instanceof DOMException && error.name === 'AbortError') return
      toast.error("Ça n'a pas fonctionné", { description: error.message, id: 'erreur-action' })
    },
  }),
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      refetchOnWindowFocus: false,
      retry: (nombre, error) => !(error instanceof ApiError && error.status < 500) && nombre < 2,
    },
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {/* Filet racine : celui d'App.tsx ne couvre que les routes, une erreur dans l'en-tête, le pied
        de page ou un fournisseur de contexte laissait sinon un écran blanc sans recours. */}
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </ErrorBoundary>
  </StrictMode>,
)

// Service worker (lecture hors connexion) : voir lib/pwa.ts, qui gère aussi le nettoyage
// des anciens workers quand la PWA est coupée (VITE_DISABLE_PWA=1, mode économie de données).
initialiserPwa()
