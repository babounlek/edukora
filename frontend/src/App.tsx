import { Suspense, lazy } from "react"
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"

import { AuthProvider } from "@/context/AuthContext"
import { CountryProvider } from "@/context/CountryContext"
import { ThemeProvider } from "@/components/theme-provider"
import { Header } from "@/components/Header"
import { Footer } from "@/components/Footer"
import { RouteFallback } from "@/components/RouteFallback"
import { COUNTRY_STORAGE_KEY, DEFAULT_COUNTRY_CODE } from "@/lib/countryPath"

// Chargées à la demande (une par route) plutôt qu'au démarrage : les pages de
// lecture (Lesson/Cours détail + lire) embarquent à elles seules react-markdown +
// katex + le pipeline remark/rehype, largement le plus gros morceau du bundle -
// aucune raison de le télécharger avant qu'un élève ouvre effectivement un contenu.
const CataloguePage = lazy(() => import("@/pages/CataloguePage").then((m) => ({ default: m.CataloguePage })))
const LessonDetailPage = lazy(() => import("@/pages/LessonDetailPage").then((m) => ({ default: m.LessonDetailPage })))
const LessonReaderPage = lazy(() => import("@/pages/LessonReaderPage").then((m) => ({ default: m.LessonReaderPage })))
const CoursListPage = lazy(() => import("@/pages/CoursListPage").then((m) => ({ default: m.CoursListPage })))
const CoursDetailPage = lazy(() => import("@/pages/CoursDetailPage").then((m) => ({ default: m.CoursDetailPage })))
const CoursReaderPage = lazy(() => import("@/pages/CoursReaderPage").then((m) => ({ default: m.CoursReaderPage })))
const LoginPage = lazy(() => import("@/pages/LoginPage").then((m) => ({ default: m.LoginPage })))
const SubscribePage = lazy(() => import("@/pages/SubscribePage").then((m) => ({ default: m.SubscribePage })))
const PricingPage = lazy(() => import("@/pages/PricingPage").then((m) => ({ default: m.PricingPage })))
const AccountPage = lazy(() => import("@/pages/AccountPage").then((m) => ({ default: m.AccountPage })))
const PrivacyPage = lazy(() => import("@/pages/PrivacyPage").then((m) => ({ default: m.PrivacyPage })))
const TermsPage = lazy(() => import("@/pages/TermsPage").then((m) => ({ default: m.TermsPage })))
const QuizStartPage = lazy(() => import("@/pages/QuizStartPage").then((m) => ({ default: m.QuizStartPage })))
const QuizSessionPage = lazy(() => import("@/pages/QuizSessionPage").then((m) => ({ default: m.QuizSessionPage })))
const QuizResultPage = lazy(() => import("@/pages/QuizResultPage").then((m) => ({ default: m.QuizResultPage })))

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

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="edukamer-theme">
      <AuthProvider>
        <BrowserRouter>
          <CountryProvider>
            <div className="flex min-h-screen flex-col">
              <Header />
              <main className="flex-1">
                <Suspense fallback={<RouteFallback />}>
                  <Routes>
                    <Route path="/" element={<RootRedirect />} />
                    <Route path="/:country" element={<CataloguePage />} />
                    <Route path="/:country/cours" element={<CoursListPage />} />
                    <Route path="/lecons/:id" element={<LessonDetailPage />} />
                    <Route path="/lecons/:id/lire" element={<LessonReaderPage />} />
                    <Route path="/cours/:id" element={<CoursDetailPage />} />
                    <Route path="/cours/:id/lire" element={<CoursReaderPage />} />
                    <Route path="/connexion" element={<LoginPage />} />
                    <Route path="/tarifs" element={<PricingPage />} />
                    <Route path="/abonnement" element={<SubscribePage />} />
                    <Route path="/compte" element={<AccountPage />} />
                    <Route path="/quiz" element={<QuizStartPage />} />
                    <Route path="/quiz/session/:id" element={<QuizSessionPage />} />
                    <Route path="/quiz/session/:id/resultat" element={<QuizResultPage />} />
                    <Route path="/confidentialite" element={<PrivacyPage />} />
                    <Route path="/cgu" element={<TermsPage />} />
                  </Routes>
                </Suspense>
              </main>
              <Footer />
            </div>
          </CountryProvider>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
