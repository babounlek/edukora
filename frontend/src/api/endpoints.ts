import { API_BASE_URL, apiRequest, getAccessToken } from "./client"
import type {
  Cours,
  CoursContent,
  CoursPreview,
  Country,
  Cursus,
  Difficulte,
  Epreuve,
  EpreuveContent,
  EpreuveInediteListItem,
  EpreuvePreview,
  Fiche,
  FicheThemeEligible,
  InscriptionInedite,
  InscriptionRepetiteur,
  ManualPayment,
  MobileMoneyAccount,
  ModeQuiz,
  Paginated,
  ParcoursModule,
  PaymentInitiateResponse,
  PaymentStatusResponse,
  Plan,
  PlanDuJour,
  Progression,
  QuizCorrige,
  QuizFichePdfStatus,
  QuizQuestion,
  QuizResult,
  QuizSession,
  PlatformStats,
  ResumeMatiere,
  RevisionDue,
  Subject,
  Subscription,
  Temoignage,
  ThemeExercicesResponse,
  ThemesFrequentsResponse,
  TentativeInedite,
  TentativeInediteCorrige,
  TentativeInediteListItem,
  TentativeInediteQuestion,
  TentativeInediteResult,
  User,
  WhatsAppStatus,
} from "./types"

export function requestOtp(phoneNumber: string) {
  return apiRequest<{ message: string }>("/auth/otp/request/", {
    method: "POST",
    body: { phone_number: phoneNumber },
    auth: false,
  })
}

export function verifyOtp(phoneNumber: string, code: string, referralCode?: string) {
  // Le refresh token ne fait plus partie de la réponse JSON - voir client.ts, posé
  // en cookie httpOnly directement par la réponse HTTP.
  return apiRequest<{ access: string; user: User }>("/auth/otp/verify/", {
    method: "POST",
    body: { phone_number: phoneNumber, code, referral_code: referralCode || undefined },
    auth: false,
  })
}

export function googleSignIn(credential: string, referralCode?: string) {
  // Même charge utile que verifyOtp (access + user, refresh en cookie httpOnly) :
  // les deux méthodes de connexion se traitent par le même chemin côté AuthContext.
  return apiRequest<{ access: string; user: User; created: boolean }>("/auth/google/", {
    method: "POST",
    body: { credential, referral_code: referralCode || undefined },
    auth: false,
  })
}

export function linkGoogle(credential: string) {
  return apiRequest<User>("/auth/google/link/", { method: "POST", body: { credential } })
}

export function requestEmailCode(email: string) {
  return apiRequest<{ message: string }>("/auth/email/request/", {
    method: "POST",
    body: { email },
    auth: false,
  })
}

export function verifyEmailCode(email: string, code: string, referralCode?: string) {
  // Même charge utile que verifyOtp et googleSignIn : les trois méthodes de connexion
  // se traitent par le même chemin côté AuthContext.
  return apiRequest<{ access: string; user: User; created: boolean }>("/auth/email/verify/", {
    method: "POST",
    body: { email, code, referral_code: referralCode || undefined },
    auth: false,
  })
}

export function requestEmailLink(email: string) {
  return apiRequest<{ message: string }>("/auth/email/link/request/", {
    method: "POST",
    body: { email },
  })
}

export function confirmEmailLink(email: string, code: string) {
  return apiRequest<User>("/auth/email/link/confirm/", {
    method: "POST",
    body: { email, code },
  })
}

export function requestPhoneChange(phoneNumber: string) {
  return apiRequest<{ message: string }>("/auth/phone/change/request/", {
    method: "POST",
    body: { phone_number: phoneNumber },
  })
}

export function confirmPhoneChange(phoneNumber: string, code: string) {
  return apiRequest<User>("/auth/phone/change/confirm/", {
    method: "POST",
    body: { phone_number: phoneNumber, code },
  })
}

export function unlinkIdentity(provider: string) {
  return apiRequest<User>(`/auth/identities/${provider}/`, { method: "DELETE" })
}

export interface UpdateProfileParams {
  full_name?: string
  pseudo?: string | null
  // Id du Cursus préparé, ou null pour effacer la déclaration - voir
  // users.serializers.UserProfileUpdateSerializer.
  cursus_prepare?: number | null
}

export function updateMe(params: UpdateProfileParams) {
  return apiRequest<User>("/auth/me/", { method: "PATCH", body: params })
}

export function getMe() {
  // "optional" (pas le défaut strict) : appelé au démarrage sur TOUTE page, y compris
  // publiques, pour savoir silencieusement si une session existe déjà (voir
  // AuthContext) - un visiteur jamais connecté y échoue normalement (401 sans cookie
  // de refresh valide), ce n'est pas une session qui "expire" et ne doit déclencher
  // aucun toast "Session expirée".
  return apiRequest<User>("/auth/me/", { auth: "optional" })
}

export interface EpreuveFilters {
  subject?: string
  cursus?: number
  country?: string
  lesson_type?: string
  origine?: string
  // Théorique/Pratique - voir NatureEpreuve. Distinct de `subject` : filtre orthogonal
  // à la matière, jamais encodé dans son code.
  nature?: string
  search?: string
  page?: number
  exclude_read?: boolean
  ordering?: "year" | "recent" | "popular"
  est_vitrine?: boolean
  // Lien "s'entraîner sur ce thème" depuis ThemesFrequents - correspondance exacte sur
  // un nom de Tag déjà connu (voir catalog.views.LessonListView), pas une saisie libre.
  theme?: string
}

export function listEpreuves(filters: EpreuveFilters = {}, signal?: AbortSignal) {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "") params.set(key, String(value))
  })
  const query = params.toString()
  return apiRequest<Paginated<Epreuve>>(`/catalog/lessons/${query ? `?${query}` : ""}`, {
    auth: "optional",
    signal,
  })
}

export function getEpreuve(slug: string) {
  return apiRequest<Epreuve>(`/catalog/lessons/${slug}/`, { auth: "optional" })
}

// slugOrId : accepte le slug (URL publique) ou l'id numérique (liens partagés avant
// l'introduction d'EpreuveInedite.slug) - résolu côté backend, voir
// inedit.views.epreuve_inedite_detail.
export function getEpreuveInedite(slugOrId: string) {
  return apiRequest<Epreuve>(`/inedit/epreuves/${slugOrId}/`, { auth: "optional" })
}

export function readEpreuve(slug: string) {
  // "optional" (pas le défaut strict) : une Lesson vitrine (voir has_access côté
  // backend) se lit sans connexion - un visiteur anonyme doit obtenir son contenu
  // normalement plutôt qu'un événement "session expirée" déclenché à tort par
  // l'échec du refresh silencieux d'un token qui n'a jamais existé.
  return apiRequest<EpreuveContent>(`/access/read/${slug}/`, { auth: "optional" })
}

export function previewEpreuve(slug: string) {
  return apiRequest<EpreuvePreview>(`/access/preview/${slug}/`, { auth: false })
}

export interface CoursFilters {
  subject?: string
  cursus?: number
  country?: string
  search?: string
  page?: number
  exclude_read?: boolean
  // Fait remonter les cours de ce sous-thème sans exclure le reste (voir
  // catalog.views.CoursListView) - utilisé par RelatedCours pour prioriser les
  // suggestions sur le même sous-thème que le cours consulté.
  sous_theme_prioritaire?: string
  // Restreint aux cours rattachés à ce Savoir officiel (programme.Savoir.id, voir
  // catalog.views.CoursListView) - utilisé par /parcours pour "voir tous les cours"
  // d'un savoir au-delà du plafond d'affichage de la page.
  savoir?: number
  // Pendant de `savoir` ci-dessus pour les matières en mode Parcours par fréquence
  // (voir ParcoursSavoir.theme_id) - restreint directement sur le Tag (catalog.Tag.id),
  // sans passer par Tag.savoir_officiel. Les deux sont mutuellement exclusifs.
  theme?: number
}

export function listCours(filters: CoursFilters = {}, signal?: AbortSignal) {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "") params.set(key, String(value))
  })
  const query = params.toString()
  return apiRequest<Paginated<Cours>>(`/catalog/cours/${query ? `?${query}` : ""}`, {
    auth: "optional",
    signal,
  })
}

export function getCours(slug: string) {
  return apiRequest<Cours>(`/catalog/cours/${slug}/`, { auth: "optional" })
}

export function readCours(slug: string) {
  // "optional" (pas le défaut strict) : un Cours vitrine (voir Cours.est_vitrine,
  // dérivé de sa/ses épreuve(s) source(s)) se lit sans connexion - un visiteur anonyme
  // doit obtenir son contenu normalement plutôt qu'un événement "session expirée"
  // déclenché à tort par l'échec du refresh silencieux d'un token qui n'a jamais
  // existé. Même motif que readEpreuve.
  return apiRequest<CoursContent>(`/access/cours/read/${slug}/`, { auth: "optional" })
}

export function previewCours(slug: string) {
  return apiRequest<CoursPreview>(`/access/cours/preview/${slug}/`, { auth: false })
}

export function listSubjects(country?: string, signal?: AbortSignal) {
  const query = country ? `?country=${country}` : ""
  return apiRequest<Subject[]>(`/catalog/subjects/${query}`, { auth: false, signal })
}

export function listCursus(country?: string, signal?: AbortSignal) {
  const query = country ? `?country=${country}` : ""
  return apiRequest<Cursus[]>(`/catalog/cursus/${query}`, { auth: false, signal })
}

export function getThemesFrequents(cursusId: number, subjectId: string, signal?: AbortSignal) {
  // "optional" : le teaser (voir ThemesFrequentsResponse.has_access) doit s'afficher
  // normalement pour un visiteur anonyme, jamais déclencher un événement "session
  // expirée" - même motif que readEpreuve/readCours.
  return apiRequest<ThemesFrequentsResponse>(
    `/catalog/cursus/${cursusId}/themes-frequents/?subject=${subjectId}`,
    { auth: "optional", signal },
  )
}

export function getThemeExercices(cursusId: number, tagId: number, subjectId: string, signal?: AbortSignal) {
  // "optional" : chaque exercice porte son propre has_access (voir ThemeExercice) -
  // même motif que getThemesFrequents, un visiteur anonyme voit la liste normalement.
  return apiRequest<ThemeExercicesResponse>(
    `/catalog/cursus/${cursusId}/themes-frequents/${tagId}/exercices/?subject=${subjectId}`,
    { auth: "optional", signal },
  )
}

export function listCountries() {
  return apiRequest<Country[]>("/catalog/countries/", { auth: false })
}

export function listTemoignages() {
  return apiRequest<Temoignage[]>("/catalog/temoignages/", { auth: false })
}

export function getPlatformStats() {
  return apiRequest<PlatformStats>("/catalog/stats/", { auth: false })
}

export function listPlans(cursusId?: number) {
  const query = cursusId ? `?cursus=${cursusId}` : ""
  return apiRequest<Plan[]>(`/subscriptions/plans/${query}`, { auth: false })
}

interface InitiatePaymentParams {
  planId: number
  phoneNumber: string
}

export function initiatePayment({ planId, phoneNumber }: InitiatePaymentParams) {
  return apiRequest<PaymentInitiateResponse>("/payments/initiate/", {
    method: "POST",
    body: { plan_id: planId, phone_number: phoneNumber },
  })
}

export function checkPaymentStatus(transactionId: number) {
  return apiRequest<PaymentStatusResponse>(`/payments/status/${transactionId}/`)
}

export function listManualPaymentMethods() {
  return apiRequest<MobileMoneyAccount[]>("/payments/manual/methods/")
}

export interface DeclareManualPaymentParams {
  planId: number
  operator: string
  amountDeclared: number
  payerPhoneNumber: string
  transactionReference: string
  paidAt?: string
  proof?: File
}

export function declareManualPayment(params: DeclareManualPaymentParams) {
  const formData = new FormData()
  formData.append("plan", String(params.planId))
  formData.append("operator", params.operator)
  formData.append("amount_declared", String(params.amountDeclared))
  formData.append("payer_phone_number", params.payerPhoneNumber)
  formData.append("transaction_reference", params.transactionReference)
  if (params.paidAt) formData.append("paid_at", params.paidAt)
  if (params.proof) formData.append("proof", params.proof)
  return apiRequest<ManualPayment>("/payments/manual/declare/", { method: "POST", body: formData })
}

export function listMyManualPayments() {
  return apiRequest<ManualPayment[]>("/payments/manual/mine/")
}

export function listMySubscriptions() {
  return apiRequest<Subscription[]>("/subscriptions/mine/")
}

export function getMyProgression(signal?: AbortSignal) {
  return apiRequest<Progression>("/access/progression/", { signal })
}

export interface StartQuizSessionParams {
  cursus: number
  mode?: ModeQuiz
  subject?: number
  theme?: number
  // Alternative à theme : cible tous les CompetenceItem du savoir, quel que soit le
  // Tag exact qui les porte (un Savoir peut en porter plusieurs) - voir
  // ParcoursPage, qui lance toujours par savoir, jamais par theme.
  savoir?: number
  n?: number
  // Drapeau "ce quiz est l'étape finale de ma séance du jour" - le serveur ne lui
  // fait pas confiance pour DÉSIGNER une séance, il ne rattache que la séance du jour
  // de l'utilisateur (voir quiz.services.rattacher_quiz_a_la_seance). Sert à clore la
  // séance automatiquement et à en afficher le score.
  seance?: number
}

export function startQuizSession(params: StartQuizSessionParams) {
  return apiRequest<QuizSession>("/quiz/sessions/", {
    method: "POST",
    body: params,
  })
}

export function getQuizSession(id: number) {
  return apiRequest<QuizSession>(`/quiz/sessions/${id}/`)
}

export function revealQuizCorrige(sessionId: number, quizQuestionId: number) {
  return apiRequest<QuizCorrige>(`/quiz/sessions/${sessionId}/questions/${quizQuestionId}/corrige/`)
}

export interface AnswerQuizQuestionParams {
  reponse_choisie?: string
  resultat_declare?: string
}

export function answerQuizQuestion(sessionId: number, quizQuestionId: number, params: AnswerQuizQuestionParams) {
  return apiRequest<QuizQuestion>(`/quiz/sessions/${sessionId}/questions/${quizQuestionId}/answer/`, {
    method: "POST",
    body: params,
  })
}

export function completeQuizSession(sessionId: number) {
  return apiRequest<QuizResult>(`/quiz/sessions/${sessionId}/completer/`, { method: "POST" })
}

export function requestQuizFichePdf(sessionId: number) {
  return apiRequest<QuizFichePdfStatus>(`/quiz/sessions/${sessionId}/fiche-pdf/`, { method: "POST" })
}

/**
 * Tout l'écran "Aujourd'hui" en un appel : compte à rebours, séance du jour, état.
 * Le serveur décide de l'état (voir quiz.views.plan_du_jour_view), le frontend
 * n'en réimplémente aucune règle.
 */
export function getPlanDuJour(signal?: AbortSignal) {
  return apiRequest<PlanDuJour>("/quiz/plan-du-jour/", { signal })
}

export function terminerSeanceDuJour() {
  return apiRequest<{ statut: string; seances_cette_semaine: number }>(
    "/quiz/plan-du-jour/terminer/", { method: "POST" },
  )
}

export function getQuizFichePdfStatus(sessionId: number) {
  return apiRequest<QuizFichePdfStatus>(`/quiz/sessions/${sessionId}/fiche-pdf/`)
}

export function downloadQuizSujetPdf(sessionId: number) {
  return openPdfInNewTab(
    `${API_BASE_URL}/quiz/sessions/${sessionId}/sujet.pdf`,
    "Impossible d'ouvrir la fiche pour le moment.",
  )
}

export function downloadQuizCorrigePdf(sessionId: number) {
  return openPdfInNewTab(
    `${API_BASE_URL}/quiz/sessions/${sessionId}/corrige.pdf`,
    "Impossible d'ouvrir la correction pour le moment.",
  )
}

export function listQuizSubjects(cursus: number) {
  return apiRequest<Subject[]>(`/quiz/subjects/?cursus=${cursus}`)
}

export function getParcours(cursus: number, subject: number) {
  return apiRequest<ParcoursModule[]>(`/quiz/parcours/?cursus=${cursus}&subject=${subject}`)
}

export function getResumeParcours(cursus: number) {
  return apiRequest<ResumeMatiere[]>(`/quiz/parcours/resume/?cursus=${cursus}`)
}

/**
 * File "à réviser" tous cursus confondus (voir quiz.views.list_revisions_dues) -
 * l'endpoint est en place et testé depuis longtemps, mais plus aucun écran ne
 * l'appelait depuis la redirection de /revision vers /parcours.
 */
export function listRevisionsDues(signal?: AbortSignal) {
  return apiRequest<RevisionDue[]>("/quiz/revisions/", { signal })
}

export function listMyInscriptionsInedites() {
  return apiRequest<InscriptionInedite[]>("/inedit/mes-inscriptions/")
}

export function listEpreuvesInedites(cursusId: number) {
  return apiRequest<EpreuveInediteListItem[]>(`/inedit/epreuves/?cursus=${cursusId}`)
}

export function startTentativeInedite(epreuveId: number) {
  return apiRequest<TentativeInedite>("/inedit/tentatives/", {
    method: "POST",
    body: { epreuve: epreuveId },
  })
}

export function getTentativeInedite(id: number) {
  return apiRequest<TentativeInedite>(`/inedit/tentatives/${id}/`)
}

export function startExamMode(tentativeId: number) {
  return apiRequest<TentativeInedite>(`/inedit/tentatives/${tentativeId}/mode-examen/`, { method: "POST" })
}

export function toggleQuestionMarquee(tentativeId: number, questionId: number) {
  return apiRequest<{ questions_marquees: number[] }>(
    `/inedit/tentatives/${tentativeId}/questions/${questionId}/marquer/`, { method: "POST" },
  )
}

export function revealTentativeCorrige(tentativeId: number, questionId: number) {
  return apiRequest<TentativeInediteCorrige>(`/inedit/tentatives/${tentativeId}/questions/${questionId}/corrige/`)
}

export interface AnswerTentativeQuestionParams {
  reponse_choisie?: string
  resultat_declare?: string
}

export function answerTentativeQuestion(tentativeId: number, questionId: number, params: AnswerTentativeQuestionParams) {
  return apiRequest<TentativeInediteQuestion>(`/inedit/tentatives/${tentativeId}/questions/${questionId}/answer/`, {
    method: "POST",
    body: params,
  })
}

export function completeTentative(tentativeId: number) {
  return apiRequest<TentativeInediteResult>(`/inedit/tentatives/${tentativeId}/completer/`, { method: "POST" })
}

export function listMyTentativesInedites() {
  return apiRequest<TentativeInediteListItem[]>("/inedit/mes-tentatives/")
}

/**
 * Ouvre un PDF gated dans un nouvel onglet - pas un simple <a href target="_blank">, le
 * fichier vit sur un storage privé (voir inedit.views.download_sujet_pdf côté backend)
 * et exige le token JWT en en-tête Authorization, que le navigateur n'attache jamais
 * tout seul à une navigation classique (contrairement au cookie httpOnly du refresh
 * token).
 *
 * L'onglet est ouvert de façon SYNCHRONE, avant le moindre await : un window.open()
 * appelé après un fetch échoue silencieusement sous certains bloqueurs de popup (Safari
 * notamment), qui n'autorisent l'ouverture que dans le prolongement direct du geste
 * utilisateur. On y navigue ensuite vers l'URL objet une fois le blob récupéré.
 */
async function openPdfInNewTab(url: string, errorMessage: string) {
  const newTab = window.open("", "_blank")
  const token = getAccessToken()
  const response = await fetch(url, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    credentials: "include",
  })
  if (!response.ok) {
    newTab?.close()
    throw new Error(errorMessage)
  }
  const blob = await response.blob()
  const blobUrl = URL.createObjectURL(blob)
  if (newTab) {
    newTab.location.href = blobUrl
  } else {
    // Onglet bloqué malgré l'ouverture synchrone (rare) - on retombe sur la fenêtre courante.
    window.location.href = blobUrl
  }
  // Révocation différée plutôt qu'immédiate : le nouvel onglet doit avoir le temps de
  // charger la ressource avant qu'elle ne devienne invalide.
  window.setTimeout(() => URL.revokeObjectURL(blobUrl), 60_000)
}

export function downloadSujetPdf(epreuveId: number) {
  return openPdfInNewTab(
    `${API_BASE_URL}/inedit/epreuves/${epreuveId}/sujet.pdf`,
    "Impossible d'ouvrir le sujet pour le moment.",
  )
}

export function listMyInscriptionsRepetiteur() {
  return apiRequest<InscriptionRepetiteur[]>("/fiches/mes-inscriptions/")
}

export function getFicheEligibilite(cursusId: number, subjectId: number) {
  return apiRequest<FicheThemeEligible[]>(`/fiches/eligibilite/?cursus=${cursusId}&subject=${subjectId}`)
}

export interface CreateFicheParams {
  cursus: number
  subject: number
  themes: number[]
  difficulte?: Difficulte | ""
  n: number
  titre: string
}

export function createFiche(params: CreateFicheParams) {
  return apiRequest<Fiche>("/fiches/", { method: "POST", body: params })
}

export function listMyFiches() {
  return apiRequest<Fiche[]>("/fiches/mes-fiches/")
}

export function getFiche(id: number) {
  return apiRequest<Fiche>(`/fiches/${id}/`)
}

export function downloadFicheSujetPdf(id: number) {
  return openPdfInNewTab(`${API_BASE_URL}/fiches/${id}/sujet.pdf`, "Impossible d'ouvrir l'énoncé pour le moment.")
}

export function downloadFicheCorrigePdf(id: number) {
  return openPdfInNewTab(`${API_BASE_URL}/fiches/${id}/corrige.pdf`, "Impossible d'ouvrir le corrigé pour le moment.")
}

export function getWhatsAppStatus() {
  return apiRequest<WhatsAppStatus>("/whatsapp/statut/")
}

export function optInWhatsApp() {
  return apiRequest<WhatsAppStatus>("/whatsapp/opt-in/", { method: "POST" })
}

export function optOutWhatsApp() {
  return apiRequest<WhatsAppStatus>("/whatsapp/opt-out/", { method: "POST" })
}

/**
 * Demande une séance de PLUS pour aujourd'hui (voir quiz.views.continuer_view).
 * Renvoie la même charge utile que getPlanDuJour - y compris l'état
 * "rien_a_proposer" quand il n'y avait plus rien à proposer.
 */
export function continuerSeanceDuJour() {
  return apiRequest<PlanDuJour>("/quiz/plan-du-jour/continuer/", { method: "POST" })
}

/**
 * "Ce n'est pas ce que je veux réviser" : demande une AUTRE séance pour aujourd'hui,
 * sur un thème différent (voir quiz.views.autre_chose_view). Même charge utile que
 * getPlanDuJour, avec "rien_a_proposer" quand il n'y a plus d'alternative.
 */
export function proposerAutreChose() {
  return apiRequest<PlanDuJour>("/quiz/plan-du-jour/autre-chose/", { method: "POST" })
}

/**
 * "Combien de temps as-tu ?" : recompose la séance du jour pour cette durée, sans
 * changer de thème (voir quiz.views.duree_seance_view). Même charge utile que
 * getPlanDuJour.
 */
export function ajusterDureeSeance(minutes: number) {
  return apiRequest<PlanDuJour>("/quiz/plan-du-jour/duree/", { method: "POST", body: { minutes } })
}

/**
 * L'élève déclare avoir traité cet exercice, ou revient sur sa déclaration (voir
 * access.views.marquer_exercice_fait). Rien n'est jamais déduit d'une ouverture de
 * page : un suivi deviné serait pire que pas de suivi.
 */
export function marquerExerciceFait(exerciseId: number, fait: boolean) {
  return apiRequest<{ exercise_id: number; fait: boolean }>(
    `/access/exercices/${exerciseId}/fait/`,
    { method: "POST", body: { fait } },
  )
}
