import { Suspense, lazy } from "react"
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"
import { Toaster } from "sonner"

import { AuthProvider } from "@/context/AuthContext"
import { CountryProvider } from "@/context/CountryContext"
import { ThemeProvider, useTheme } from "@/components/theme-provider"
import { Header } from "@/components/Header"
import { Footer } from "@/components/Footer"
import { OnboardingModal } from "@/components/OnboardingModal"
import { InstallPrompt } from "@/components/InstallPrompt"
import { ErrorBoundary } from "@/components/ErrorBoundary"
import { RouteFallback } from "@/components/RouteFallback"
import { ScrollToTop } from "@/components/ScrollToTop"
import { COUNTRY_STORAGE_KEY, DEFAULT_COUNTRY_CODE } from "@/lib/countryPath"

// Chargées à la demande (une par route) plutôt qu'au démarrage : les pages de
// lecture (Épreuve/Cours détail + lire) embarquent à elles seules react-markdown +
// katex + le pipeline remark/rehype, largement le plus gros morceau du bundle -
// aucune raison de le télécharger avant qu'un élève ouvre effectivement un contenu.
const CataloguePage = lazy(() => import("@/pages/CataloguePage").then((m) => ({ default: m.CataloguePage })))
const EpreuvesListPage = lazy(() => import("@/pages/EpreuvesListPage").then((m) => ({ default: m.EpreuvesListPage })))
const EpreuveDetailPage = lazy(() => import("@/pages/EpreuveDetailPage").then((m) => ({ default: m.EpreuveDetailPage })))
const EpreuveInediteDetailPage = lazy(() => import("@/pages/EpreuveInediteDetailPage").then((m) => ({ default: m.EpreuveInediteDetailPage })))
const EpreuveReaderPage = lazy(() => import("@/pages/EpreuveReaderPage").then((m) => ({ default: m.EpreuveReaderPage })))
const CoursListPage = lazy(() => import("@/pages/CoursListPage").then((m) => ({ default: m.CoursListPage })))
const CoursDetailPage = lazy(() => import("@/pages/CoursDetailPage").then((m) => ({ default: m.CoursDetailPage })))
const CoursReaderPage = lazy(() => import("@/pages/CoursReaderPage").then((m) => ({ default: m.CoursReaderPage })))
const LoginPage = lazy(() => import("@/pages/LoginPage").then((m) => ({ default: m.LoginPage })))
const SubscribePage = lazy(() => import("@/pages/SubscribePage").then((m) => ({ default: m.SubscribePage })))
const PricingPage = lazy(() => import("@/pages/PricingPage").then((m) => ({ default: m.PricingPage })))
const AccountPage = lazy(() => import("@/pages/AccountPage").then((m) => ({ default: m.AccountPage })))
const MesPaiementsPage = lazy(() => import("@/pages/MesPaiementsPage").then((m) => ({ default: m.MesPaiementsPage })))
const PrivacyPage = lazy(() => import("@/pages/PrivacyPage").then((m) => ({ default: m.PrivacyPage })))
const TermsPage = lazy(() => import("@/pages/TermsPage").then((m) => ({ default: m.TermsPage })))
const AboutPage = lazy(() => import("@/pages/AboutPage").then((m) => ({ default: m.AboutPage })))
const QuizStartPage = lazy(() => import("@/pages/QuizStartPage").then((m) => ({ default: m.QuizStartPage })))
const QuizSessionPage = lazy(() => import("@/pages/QuizSessionPage").then((m) => ({ default: m.QuizSessionPage })))
const QuizResultPage = lazy(() => import("@/pages/QuizResultPage").then((m) => ({ default: m.QuizResultPage })))
const ParcoursPage = lazy(() => import("@/pages/ParcoursPage").then((m) => ({ default: m.ParcoursPage })))
const ParcoursSubjectPage = lazy(() => import("@/pages/ParcoursSubjectPage").then((m) => ({ default: m.ParcoursSubjectPage })))
const InediteTentativePage = lazy(() => import("@/pages/InediteTentativePage").then((m) => ({ default: m.InediteTentativePage })))
const InediteResultPage = lazy(() => import("@/pages/InediteResultPage").then((m) => ({ default: m.InediteResultPage })))
const FichesPage = lazy(() => import("@/pages/FichesPage").then((m) => ({ default: m.FichesPage })))

/**
 * `/` seul n'est jamais l'URL canonique d'une page (voir countryPath.ts) : on
 * redirige vers le dernier pays choisi (localStorage), sinon le pays par défaut -
 * lu de façon synchrone pour rediriger dès le premier rendu, sans attendre le fetch
 * de la liste des pays (CountryProvider).
 */
function RootRedirect() {
  const target = localStorage.getItem(COUNTRY_STORAGE_KEY) || DEFAULT_COUNTRY_CODE
  return <Navigate to={`/${target}`} replace />
}

// Composant à part plutôt qu'appelé directement dans App() : useTheme() exige un
// ThemeProvider ancêtre, or App() rend lui-même ce ThemeProvider - son propre corps
// s'exécute donc avant que le contexte n'existe.
function AppToaster() {
  const { theme } = useTheme()
  return <Toaster theme={theme} richColors closeButton />
}

function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="edukamer-theme">
      <AppToaster />
      <AuthProvider>
        <BrowserRouter>
          <ScrollToTop />
          <CountryProvider>
            <div className="flex min-h-screen flex-col">
              <Header />
              <main className="flex-1">
                <ErrorBoundary>
                  <Suspense fallback={<RouteFallback />}>
                    <Routes>
                      <Route path="/" element={<RootRedirect />} />
                      <Route path="/:country" element={<CataloguePage />} />
                      <Route path="/:country/epreuves" element={<EpreuvesListPage />} />
                      <Route path="/:country/cours" element={<CoursListPage />} />
                      <Route path="/:country/epreuves/:slug" element={<EpreuveDetailPage />} />
                      <Route path="/:country/epreuves/:slug/lire" element={<EpreuveReaderPage />} />
                      <Route path="/:country/epreuves-inedites/:id" element={<EpreuveInediteDetailPage />} />
                      {/* Anciennes URLs sans préfixe pays (avant la reco d'audit UX qui l'a
                          introduit) - conservées pour les liens/favoris/index déjà en
                          circulation, chaque page se recanonicalise elle-même dès que le
                          pays de l'épreuve est connu (voir EpreuveDetailPage/EpreuveReaderPage). */}
                      <Route path="/epreuves/:slug" element={<EpreuveDetailPage />} />
                      <Route path="/epreuves/:slug/lire" element={<EpreuveReaderPage />} />
                      <Route path="/cours/:slug" element={<CoursDetailPage />} />
                      <Route path="/cours/:slug/lire" element={<CoursReaderPage />} />
                      <Route path="/connexion" element={<LoginPage />} />
                      <Route path="/tarifs" element={<PricingPage />} />
                      <Route path="/abonnement" element={<SubscribePage />} />
                      <Route path="/compte" element={<AccountPage />} />
                      <Route path="/mes-paiements" element={<MesPaiementsPage />} />
                      <Route path="/quiz" element={<QuizStartPage />} />
                      <Route path="/quiz/session/:id" element={<QuizSessionPage />} />
                      <Route path="/quiz/session/:id/resultat" element={<QuizResultPage />} />
                      {/* /parcours a absorbé "à réviser" (badge par savoir) - une ancienne
                          entrée (favori, lien externe) doit continuer à mener quelque
                          part de cohérent plutôt qu'un 404. */}
                      <Route path="/revision" element={<Navigate to="/parcours" replace />} />
                      <Route path="/parcours" element={<ParcoursPage />} />
                      <Route path="/parcours/:subjectId" element={<ParcoursSubjectPage />} />
                      <Route path="/inedit/tentative/:id" element={<InediteTentativePage />} />
                      <Route path="/inedit/tentative/:id/resultat" element={<InediteResultPage />} />
                      <Route path="/fiches" element={<FichesPage />} />
                      <Route path="/confidentialite" element={<PrivacyPage />} />
                      <Route path="/cgu" element={<TermsPage />} />
                      <Route path="/a-propos" element={<AboutPage />} />
                    </Routes>
                  </Suspense>
                </ErrorBoundary>
              </main>
              <Footer />
            </div>
            <OnboardingModal />
            <InstallPrompt />
          </CountryProvider>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
