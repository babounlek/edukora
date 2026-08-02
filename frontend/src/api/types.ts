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

export interface Country {
  id: number
  code: string
  label: string
  dial_code: string
  currency: string
  has_lessons: boolean
}

export interface Subject {
  id: number
  code: string
  label: string
  country: Country
}

export interface Pays {
  code: string
  label: string
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

export type EpreuveType = "FICHE" | "CORR" | "SUJET"

export interface EpreuveRelatedCours {
  id: number
  titre: string
  has_access: boolean
}

export type Origine = "OFFICIEL" | "BLANC" | "ETABLISSEMENT" | "AUTRE"

export interface Epreuve {
  id: number
  title: string
  subject: Subject
  cursus: Cursus[]
  lesson_type: EpreuveType
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
  related_cours: EpreuveRelatedCours[]
  sujet_pdf_url: string | null
}

export interface EpreuveHeader {
  matiere: string
  serie: string | null
  examen: string | null
  annee: number | null
  duree: string | null
  coefficient: string | null
  origine: string | null
  etablissement: string | null
  pays: Pays
}

export interface EpreuveContent {
  id: number
  title: string
  content_markdown: string
  header: EpreuveHeader
  sujet_pdf_url: string | null
}

export interface EpreuvePreview {
  id: number
  title: string
  preview_markdown: string
  header: EpreuveHeader
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
  pays: Pays
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
  lessons: Epreuve[]
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

export type ModeQuiz = "PRATIQUE" | "DIAGNOSTIC"
export type ResultatDeclare = "REUSSI" | "PARTIEL" | "ECHEC"
export type TypeReponse = "OUVERTE" | "QCM"

export interface QuizChoix {
  lettre: string
  texte: string
}

export interface QuizAnswerInfo {
  reponse_choisie: string
  resultat_declare: string
  est_correcte: boolean
}

export interface QuizQuestion {
  id: number
  ordre: number
  enonce_markdown: string
  type_reponse: TypeReponse
  choix: QuizChoix[]
  subject_label: string
  // Présent uniquement pour un item CompetenceItem, source du quiz depuis la bascule
  // (voir quiz.views._question_payload côté backend) - un item n'appartient à aucune
  // épreuve/leçon d'origine, contrairement à numero/lesson_id/enonce_intro_markdown
  // ci-dessous.
  theme?: string
  // Présents uniquement pour l'historique pré-bascule (source catalog.Question,
  // extraite d'une épreuve réelle) - jamais peuplés pour une session créée après la
  // bascule vers CompetenceItem.
  numero?: string
  enonce_intro_markdown?: string
  lesson_id?: number
  lesson_title?: string
  // Présents uniquement une fois la question répondue (voir quiz.views._question_payload côté backend).
  corrige_markdown?: string
  reponse_correcte?: string
  reponse?: QuizAnswerInfo
}

export interface QuizSession {
  id: number
  mode: ModeQuiz
  cursus: number
  cursus_display: string
  started_at: string
  completed_at: string | null
  total_questions: number
  questions: QuizQuestion[]
}

export interface QuizCorrige {
  corrige_markdown: string
  reponse_correcte: string
}

export interface QuizThemeScore {
  theme: string
  total: number
  reussies: number
}

export interface QuizResult {
  id: number
  total_questions: number
  questions_repondues: number
  score: number
  par_theme: QuizThemeScore[]
}
