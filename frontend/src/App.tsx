import { Suspense, lazy, useState, type ReactNode } from "react"
import { BrowserRouter, Navigate, Outlet, Route, Routes, unstable_HistoryRouter as HistoryRouter, useParams } from "react-router-dom"
import { Toaster } from "sonner"

import { AuthProvider, useAuth } from "@/context/AuthContext"
import { CountryProvider, useCountry } from "@/context/CountryContext"
import { ThemeProvider, useTheme } from "@/components/theme-provider"
import { Header } from "@/components/Header"
import { BandeauHorsLigne } from "@/components/BandeauHorsLigne"
import { useModeExamen } from "@/lib/modeExamen"
import { BandeauReprisePaiement } from "@/components/BandeauReprisePaiement"
import { Footer } from "@/components/Footer"
import { OnboardingModal } from "@/components/OnboardingModal"
import { PinDialogs } from "@/components/PinDialogs"
import { VerrouInactivite } from "@/components/VerrouInactivite"
import { BandeauCursus } from "@/components/BandeauCursus"
import { BandeauLangueCursus } from "@/components/BandeauLangueCursus"
import { BarreSeance } from "@/components/BarreSeance"
import { BottomTabBar } from "@/components/BottomTabBar"
import { ErrorBoundary } from "@/components/ErrorBoundary"
import { RouteFallback } from "@/components/RouteFallback"
import { ScrollToTop } from "@/components/ScrollToTop"
import { BalisesDeRoute } from "@/components/BalisesDeRoute"
import { COUNTRY_STORAGE_KEY, DEFAULT_COUNTRY_CODE } from "@/lib/countryPath"
import { t, useI18n } from "@/lib/i18n"
import { creerHistoriqueAnglais } from "@/lib/i18n/historiqueAnglais"

// Chargées à la demande (une par route) plutôt qu'au démarrage : les pages de
// lecture (Épreuve/Cours détail + lire) embarquent à elles seules react-markdown +
// katex + le pipeline remark/rehype, largement le plus gros morceau du bundle -
// aucune raison de le télécharger avant qu'un élève ouvre effectivement un contenu.
const CataloguePage = lazy(() => import("@/pages/CataloguePage").then((m) => ({ default: m.CataloguePage })))
const EpreuvesListPage = lazy(() => import("@/pages/EpreuvesListPage").then((m) => ({ default: m.EpreuvesListPage })))
const ThemesFrequentsPage = lazy(() => import("@/pages/ThemesFrequentsPage").then((m) => ({ default: m.ThemesFrequentsPage })))
const ThemeExercicesPage = lazy(() => import("@/pages/ThemeExercicesPage").then((m) => ({ default: m.ThemeExercicesPage })))
const ThemeExerciceLecturePage = lazy(() => import("@/pages/ThemeExerciceLecturePage").then((m) => ({ default: m.ThemeExerciceLecturePage })))
const EpreuveDetailPage = lazy(() => import("@/pages/EpreuveDetailPage").then((m) => ({ default: m.EpreuveDetailPage })))
const EpreuveInediteDetailPage = lazy(() => import("@/pages/EpreuveInediteDetailPage").then((m) => ({ default: m.EpreuveInediteDetailPage })))
const EpreuveReaderPage = lazy(() => import("@/pages/EpreuveReaderPage").then((m) => ({ default: m.EpreuveReaderPage })))
const CoursListPage = lazy(() => import("@/pages/CoursListPage").then((m) => ({ default: m.CoursListPage })))
const CoursDetailPage = lazy(() => import("@/pages/CoursDetailPage").then((m) => ({ default: m.CoursDetailPage })))
const CoursReaderPage = lazy(() => import("@/pages/CoursReaderPage").then((m) => ({ default: m.CoursReaderPage })))
const LoginPage = lazy(() => import("@/pages/LoginPage").then((m) => ({ default: m.LoginPage })))
const QuiEtudiePage = lazy(() => import("@/pages/QuiEtudiePage").then((m) => ({ default: m.QuiEtudiePage })))
const SubscribePage = lazy(() => import("@/pages/SubscribePage").then((m) => ({ default: m.SubscribePage })))
const PricingPage = lazy(() => import("@/pages/PricingPage").then((m) => ({ default: m.PricingPage })))
const AccountPage = lazy(() => import("@/pages/AccountPage").then((m) => ({ default: m.AccountPage })))
const AccesPage = lazy(() => import("@/pages/AccesPage").then((m) => ({ default: m.AccesPage })))
const HistoriquePage = lazy(() => import("@/pages/HistoriquePage").then((m) => ({ default: m.HistoriquePage })))
const CarnetPage = lazy(() => import("@/pages/CarnetPage").then((m) => ({ default: m.CarnetPage })))
const MesPaiementsPage = lazy(() => import("@/pages/MesPaiementsPage").then((m) => ({ default: m.MesPaiementsPage })))
const PrivacyPage = lazy(() => import("@/pages/PrivacyPage").then((m) => ({ default: m.PrivacyPage })))
const TermsPage = lazy(() => import("@/pages/TermsPage").then((m) => ({ default: m.TermsPage })))
const AboutPage = lazy(() => import("@/pages/AboutPage").then((m) => ({ default: m.AboutPage })))
const QuizStartPage = lazy(() => import("@/pages/QuizStartPage").then((m) => ({ default: m.QuizStartPage })))
const QuizSessionPage = lazy(() => import("@/pages/QuizSessionPage").then((m) => ({ default: m.QuizSessionPage })))
const QuizResultPage = lazy(() => import("@/pages/QuizResultPage").then((m) => ({ default: m.QuizResultPage })))
const QuizEssaiLancementPage = lazy(() => import("@/pages/QuizEssaiLancementPage").then((m) => ({ default: m.QuizEssaiLancementPage })))
const QuizEssaiResultPage = lazy(() => import("@/pages/QuizEssaiResultPage").then((m) => ({ default: m.QuizEssaiResultPage })))
const ParcoursPage = lazy(() => import("@/pages/ParcoursPage").then((m) => ({ default: m.ParcoursPage })))
const ParcoursSubjectPage = lazy(() => import("@/pages/ParcoursSubjectPage").then((m) => ({ default: m.ParcoursSubjectPage })))
const InediteTentativePage = lazy(() => import("@/pages/InediteTentativePage").then((m) => ({ default: m.InediteTentativePage })))
const InediteResultPage = lazy(() => import("@/pages/InediteResultPage").then((m) => ({ default: m.InediteResultPage })))
const FichesPage = lazy(() => import("@/pages/FichesPage").then((m) => ({ default: m.FichesPage })))
const NotFoundPage = lazy(() => import("@/pages/NotFoundPage").then((m) => ({ default: m.NotFoundPage })))
const RecherchePage = lazy(() => import("@/pages/RecherchePage").then((m) => ({ default: m.RecherchePage })))

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

/**
 * `/:country` accepte n'importe quel premier segment : sans ce garde, `/n-importe-quoi` affichait
 * l'accueil d'un pays inexistant (vide). Tant que la liste des pays n'est pas arrivée (ou si son
 * chargement échoue), on laisse passer plutôt que d'afficher un 404 à tort.
 */
function CountryGuard() {
  const { country } = useParams<{ country: string }>()
  const { countries } = useCountry()
  const inconnu = countries.length > 0 && !countries.some((c) => c.code.toLowerCase() === country?.toLowerCase())
  return inconnu ? <NotFoundPage /> : <Outlet />
}

/**
 * Réserve la hauteur de la barre d'onglets, qui est en position fixe : sans elle, les derniers
 * liens du pied de page sont recouverts et donc inatteignables sur mobile. Seulement quand la barre
 * existe (voir BottomTabBar : élève connecté avec un examen préparé) - pour un visiteur, ces 80 px
 * n'étaient qu'un grand vide sous le pied de page.
 */
function ReserveBarreOnglets() {
  const { isAuthenticated, user } = useAuth()
  if (!isAuthenticated || !user?.cursus_prepare) return null
  return <div className="h-20 lg:hidden" aria-hidden="true" />
}

// Composant à part plutôt qu'appelé directement dans App() : useTheme() exige un
// ThemeProvider ancêtre, or App() rend lui-même ce ThemeProvider - son propre corps
// s'exécute donc avant que le contexte n'existe.
function AppToaster() {
  const { theme } = useTheme()
  return <Toaster theme={theme} richColors closeButton />
}

/**
 * Le routeur de la langue de la page, fixée au chargement par initialiserLangue (`basename` : `/en`, ou rien
 * pour le français). En français, le routeur habituel. En anglais, le même routeur sur un historique qui
 * traduit l'adresse à la frontière (`/en/cm/past-papers/x` pour le routeur : `/cm/epreuves/x`) : toutes les
 * routes ci-dessous valent pour les deux langues et tout lien interne reste dans la langue de la page.
 */
function RouteurDeLangue({ basename, children }: { basename: string; children: ReactNode }) {
  const [historique] = useState(() => (basename ? creerHistoriqueAnglais() : null))
  if (historique) return <HistoryRouter history={historique}>{children}</HistoryRouter>
  return <BrowserRouter>{children}</BrowserRouter>
}

function App({ basename = "" }: { basename?: string }) {
  useI18n()
  const enExamen = useModeExamen()
  return (
    <ThemeProvider defaultTheme="light" storageKey="edukamer-theme">
      <AppToaster />
      <AuthProvider>
        <RouteurDeLangue basename={basename}>
          <ScrollToTop />
          <BalisesDeRoute />
          <CountryProvider>
            <div className="flex min-h-screen flex-col">
              {/* Premier élément atteint au clavier : évite de retraverser tout l'en-tête à
                  chaque page. Invisible tant qu'il n'a pas le focus. */}
              <a
                href="#contenu"
                className="sr-only rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground focus:not-sr-only focus:fixed focus:left-3 focus:top-3 focus:z-[100]"
              >
                {t("gl.aller_contenu")}
              </a>
              {/* Salle d'examen : tant qu'une épreuve chronométrée tourne, seul le bandeau hors connexion
                  reste (il sert l'élève) - voir lib/modeExamen.ts. */}
              {!enExamen && <Header />}
              <BandeauHorsLigne />
              {!enExamen && <BandeauCursus />}
              {!enExamen && <BandeauLangueCursus />}
              {!enExamen && <BandeauReprisePaiement />}
              {!enExamen && <BarreSeance />}
              <main id="contenu" tabIndex={-1} className="flex-1 outline-none">
                <ErrorBoundary>
                  <Suspense fallback={<RouteFallback />}>
                    <Routes>
                      <Route path="/" element={<RootRedirect />} />
                      <Route path="/:country" element={<CountryGuard />}>
                        <Route index element={<CataloguePage />} />
                        <Route path="epreuves" element={<EpreuvesListPage />} />
                        <Route path="recherche" element={<RecherchePage />} />
                        <Route path="themes-frequents" element={<ThemesFrequentsPage />} />
                        <Route path="themes-frequents/:tagId/exercices" element={<ThemeExercicesPage />} />
                        <Route path="themes-frequents/:tagId/exercices/:exerciseId" element={<ThemeExerciceLecturePage />} />
                        <Route path="cours" element={<CoursListPage />} />
                        <Route path="epreuves/:slug" element={<EpreuveDetailPage />} />
                        <Route path="epreuves/:slug/lire" element={<EpreuveReaderPage />} />
                        <Route path="epreuves-inedites/:id" element={<EpreuveInediteDetailPage />} />
                      </Route>
                      {/* Anciennes URLs sans préfixe pays (avant la reco d'audit UX qui l'a
                          introduit) - conservées pour les liens/favoris/index déjà en
                          circulation, chaque page se recanonicalise elle-même dès que le
                          pays de l'épreuve est connu (voir EpreuveDetailPage/EpreuveReaderPage). */}
                      <Route path="/epreuves/:slug" element={<EpreuveDetailPage />} />
                      <Route path="/epreuves/:slug/lire" element={<EpreuveReaderPage />} />
                      <Route path="/cours/:slug" element={<CoursDetailPage />} />
                      <Route path="/cours/:slug/lire" element={<CoursReaderPage />} />
                      <Route path="/connexion" element={<LoginPage />} />
                      <Route path="/qui-etudie" element={<QuiEtudiePage />} />
                      <Route path="/tarifs" element={<PricingPage />} />
                      <Route path="/abonnement" element={<SubscribePage />} />
                      <Route path="/compte" element={<AccountPage />} />
                      <Route path="/mes-acces" element={<AccesPage />} />
                      <Route path="/historique" element={<HistoriquePage />} />
                      <Route path="/carnet" element={<CarnetPage />} />
                      <Route path="/mes-paiements" element={<MesPaiementsPage />} />
                      <Route path="/quiz" element={<QuizStartPage />} />
                      <Route path="/quiz/essai" element={<QuizSessionPage essai />} />
                      <Route path="/quiz/essai/resultat" element={<QuizEssaiResultPage />} />
                      <Route path="/quiz/essai/:cursus/:subject/:theme" element={<QuizEssaiLancementPage />} />
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
                      {/* Simulation d'une annale officielle en conditions d'examen - même page que les
                          épreuves inédites, notée exercice par exercice. */}
                      <Route path="/simulation/:id" element={<InediteTentativePage source="officielle" />} />
                      <Route path="/simulation/:id/resultat" element={<InediteResultPage source="officielle" />} />
                      <Route path="/fiches" element={<FichesPage />} />
                      <Route path="/confidentialite" element={<PrivacyPage />} />
                      <Route path="/cgu" element={<TermsPage />} />
                      <Route path="/a-propos" element={<AboutPage />} />
                      <Route path="*" element={<NotFoundPage />} />
                    </Routes>
                  </Suspense>
                </ErrorBoundary>
              </main>
              {!enExamen && <Footer />}
              {/* Réserve la hauteur de la barre d'onglets, qui est en position fixe :
                  sans elle, les derniers liens du pied de page sont recouverts et donc
                  inatteignables sur mobile. */}
              {!enExamen && <ReserveBarreOnglets />}
            </div>
            {!enExamen && <BottomTabBar />}
            <OnboardingModal />
            <PinDialogs />
            <VerrouInactivite />
          </CountryProvider>
        </RouteurDeLangue>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
