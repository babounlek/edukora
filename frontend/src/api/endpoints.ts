import { apiRequest } from "./client"
import type {
  Cours,
  CoursContent,
  CoursPreview,
  Country,
  Cursus,
  Epreuve,
  EpreuveContent,
  EpreuvePreview,
  ModeQuiz,
  Paginated,
  PaymentInitiateResponse,
  PaymentStatusResponse,
  Plan,
  Progression,
  QuizCorrige,
  QuizQuestion,
  QuizResult,
  QuizSession,
  Subject,
  Subscription,
  User,
} from "./types"

export function requestOtp(phoneNumber: string) {
  return apiRequest<{ message: string }>("/auth/otp/request/", {
    method: "POST",
    body: { phone_number: phoneNumber },
    auth: false,
  })
}

export function verifyOtp(phoneNumber: string, code: string, referralCode?: string) {
  return apiRequest<{ access: string; refresh: string; user: User }>("/auth/otp/verify/", {
    method: "POST",
    body: { phone_number: phoneNumber, code, referral_code: referralCode || undefined },
    auth: false,
  })
}

export function getMe() {
  return apiRequest<User>("/auth/me/")
}

export interface EpreuveFilters {
  subject?: string
  cursus?: number
  country?: string
  lesson_type?: string
  origine?: string
  search?: string
  page?: number
  exclude_read?: boolean
  ordering?: "year"
}

export function listEpreuves(filters: EpreuveFilters = {}) {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "") params.set(key, String(value))
  })
  const query = params.toString()
  return apiRequest<Paginated<Epreuve>>(`/catalog/lessons/${query ? `?${query}` : ""}`, {
    auth: "optional",
  })
}

export function getEpreuve(slug: string) {
  return apiRequest<Epreuve>(`/catalog/lessons/${slug}/`, { auth: "optional" })
}

export function readEpreuve(slug: string) {
  return apiRequest<EpreuveContent>(`/access/read/${slug}/`)
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
}

export function listCours(filters: CoursFilters = {}) {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "") params.set(key, String(value))
  })
  const query = params.toString()
  return apiRequest<Paginated<Cours>>(`/catalog/cours/${query ? `?${query}` : ""}`, {
    auth: "optional",
  })
}

export function getCours(id: number) {
  return apiRequest<Cours>(`/catalog/cours/${id}/`, { auth: "optional" })
}

export function readCours(id: number) {
  return apiRequest<CoursContent>(`/access/cours/read/${id}/`)
}

export function previewCours(id: number) {
  return apiRequest<CoursPreview>(`/access/cours/preview/${id}/`, { auth: false })
}

export function listSubjects(country?: string) {
  const query = country ? `?country=${country}` : ""
  return apiRequest<Subject[]>(`/catalog/subjects/${query}`, { auth: false })
}

export function listCursus(country?: string) {
  const query = country ? `?country=${country}` : ""
  return apiRequest<Cursus[]>(`/catalog/cursus/${query}`, { auth: false })
}

export function listCountries() {
  return apiRequest<Country[]>("/catalog/countries/", { auth: false })
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

export function listMySubscriptions() {
  return apiRequest<Subscription[]>("/subscriptions/mine/")
}

export function getMyProgression() {
  return apiRequest<Progression>("/access/progression/")
}

export interface StartQuizSessionParams {
  cursus: number
  mode?: ModeQuiz
  subject?: number
  n?: number
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
