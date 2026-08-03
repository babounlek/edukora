import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
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

// Un lien de parrainage est toujours cliqué depuis l'extérieur (WhatsApp, réseaux
// sociaux) donc toujours un chargement de page complet, jamais une navigation
// interne à l'app - un appel unique ici suffit, pas besoin de suivre les
// changements de route.
captureReferralCode()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
