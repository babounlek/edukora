import { apiRequest } from "./client"
import type {
  Cours,
  CoursContent,
  CoursPreview,
  Cursus,
  Lesson,
  LessonContent,
  LessonPreview,
  Paginated,
  PaymentInitiateResponse,
  PaymentStatusResponse,
  Plan,
  Progression,
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

export interface LessonFilters {
  subject?: string
  cursus?: number
  lesson_type?: string
  origine?: string
  search?: string
  page?: number
}

export function listLessons(filters: LessonFilters = {}) {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "") params.set(key, String(value))
  })
  const query = params.toString()
  return apiRequest<Paginated<Lesson>>(`/catalog/lessons/${query ? `?${query}` : ""}`, {
    auth: "optional",
  })
}

export function getLesson(id: number) {
  return apiRequest<Lesson>(`/catalog/lessons/${id}/`, { auth: "optional" })
}

export function readLesson(id: number) {
  return apiRequest<LessonContent>(`/access/read/${id}/`)
}

export function previewLesson(id: number) {
  return apiRequest<LessonPreview>(`/access/preview/${id}/`, { auth: false })
}

export interface CoursFilters {
  subject?: string
  cursus?: number
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

export function listSubjects() {
  return apiRequest<Subject[]>("/catalog/subjects/", { auth: false })
}

export function listCursus() {
  return apiRequest<Cursus[]>("/catalog/cursus/", { auth: false })
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
