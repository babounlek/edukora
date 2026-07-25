export interface User {
  id: number
  phone_number: string
  full_name: string
  date_joined: string
  referral_code: string
  filleuls_count: number
}

export interface Series {
  id: number
  code: string
  label: string
}

export interface Subject {
  id: number
  code: string
  label: string
}

export interface Country {
  id: number
  code: string
  label: string
  dial_code: string
  currency: string
}

export interface Cursus {
  id: number
  country: Country
  examen: string
  examen_display: string
  series: Series | null
}

export interface Tag {
  id: number
  name: string
}

export type LessonType = "FICHE" | "CORR" | "SUJET"

export interface LessonRelatedCours {
  id: number
  titre: string
  has_access: boolean
}

export type Origine = "OFFICIEL" | "BLANC" | "ETABLISSEMENT" | "AUTRE"

export interface Lesson {
  id: number
  title: string
  subject: Subject
  cursus: Cursus[]
  lesson_type: LessonType
  lesson_type_display: string
  year: number | null
  duree_epreuve: string
  coefficient: string
  origine: Origine
  origine_display: string
  etablissement: string
  themes: Tag[]
  has_access: boolean
  is_read: boolean
  exercises_count: number
  related_cours: LessonRelatedCours[]
  sujet_pdf_url: string | null
}

export interface LessonHeader {
  matiere: string
  serie: string | null
  examen: string | null
  annee: number | null
  duree: string | null
  coefficient: string | null
  origine: string | null
  etablissement: string | null
}

export interface LessonContent {
  id: number
  title: string
  content_markdown: string
  header: LessonHeader
  sujet_pdf_url: string | null
}

export interface LessonPreview {
  id: number
  title: string
  preview_markdown: string
  header: LessonHeader
}

export interface Cours {
  id: number
  titre: string
  subject: Subject
  cursus: Cursus[]
  sous_theme: string
  duree_estimee_min: number | null
  tags: Tag[]
  has_access: boolean
  is_read: boolean
}

export interface CoursHeader {
  matiere: string
  serie: string | null
  sous_theme: string | null
  duree_estimee_min: number | null
}

export interface CoursContent {
  id: number
  title: string
  content_markdown: string
  header: CoursHeader
}

export interface CoursPreview {
  id: number
  title: string
  preview_markdown: string
  header: CoursHeader
}

export interface Progression {
  lessons: Lesson[]
  cours: Cours[]
}

export type DureeMode = "FIXE" | "JUSQUA_EXAMEN"

export interface Plan {
  id: number
  name: string
  cursus: Cursus
  price: number
  duration_mode: DureeMode
  duration_days: number
  effective_duration_days: number
}

export interface Subscription {
  id: number
  cursus: Cursus
  expires_at: string
  is_active: boolean
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export type TransactionStatus = "PENDING" | "SUCCESSFUL" | "FAILED"

export interface PaymentInitiateResponse {
  transaction_id: number
  status: TransactionStatus
}

export interface PaymentStatusResponse {
  status: TransactionStatus
  subscription_active: boolean
}
