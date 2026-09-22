import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
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
import { initSentry } from '@/lib/sentry'

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
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      refetchOnWindowFocus: false,
    },
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>,
)

// PWA désactivée pour l'instant (voir vite.config.ts, plus de plugin VitePWA) : aucun
// nouveau service worker n'est généré, donc sans ce nettoyage les visiteurs qui en ont
// déjà un installé resteraient bloqués indéfiniment sur son cache - plus aucune
// nouvelle version ne sera jamais poussée pour le remplacer.
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then((registrations) => {
    registrations.forEach((registration) => registration.unregister())
  })
  caches?.keys().then((keys) => keys.forEach((key) => caches.delete(key)))
}
