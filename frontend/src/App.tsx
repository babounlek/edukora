import { Suspense, lazy } from "react"
import { BrowserRouter, Route, Routes } from "react-router-dom"

import { AuthProvider } from "@/context/AuthContext"
import { ThemeProvider } from "@/components/theme-provider"
import { Header } from "@/components/Header"
import { Footer } from "@/components/Footer"
import { RouteFallback } from "@/components/RouteFallback"

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

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="edukamer-theme">
      <AuthProvider>
        <BrowserRouter>
          <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1">
              <Suspense fallback={<RouteFallback />}>
                <Routes>
                  <Route path="/" element={<CataloguePage />} />
                  <Route path="/lecons/:id" element={<LessonDetailPage />} />
                  <Route path="/lecons/:id/lire" element={<LessonReaderPage />} />
                  <Route path="/cours" element={<CoursListPage />} />
                  <Route path="/cours/:id" element={<CoursDetailPage />} />
                  <Route path="/cours/:id/lire" element={<CoursReaderPage />} />
                  <Route path="/connexion" element={<LoginPage />} />
                  <Route path="/tarifs" element={<PricingPage />} />
                  <Route path="/abonnement" element={<SubscribePage />} />
                  <Route path="/compte" element={<AccountPage />} />
                  <Route path="/confidentialite" element={<PrivacyPage />} />
                  <Route path="/cgu" element={<TermsPage />} />
                </Routes>
              </Suspense>
            </main>
            <Footer />
          </div>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
