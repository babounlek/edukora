/** Miroir de users.models.AuthProvider - une manière de prouver qu'on est ce compte. */
export type AuthProvider = "phone" | "google" | "apple" | "email" | "passkey"

export interface User {
  id: number
  // Format local à 9 chiffres, pas E.164 - voir UserSerializer.get_phone_number côté
  // backend. Chaîne vide pour un compte sans numéro (inscrit via Google).
  phone_number: string
  email: string
  email_verified: boolean
  full_name: string
  pseudo: string | null
  date_joined: string
  referral_code: string
  filleuls_count: number
  // Voir subscriptions.models.solde_credit_parrainage - dépensable sur n'importe
  // quel achat futur (voir SubscribePage), pas seulement sur le cursus qui l'a
  // rapporté.
  credit_parrainage_disponible: number
  // Fournisseurs déjà rattachés, triés. Un compte en a toujours au moins un ; c'est
  // l'unicité de cette liste qui rend un compte irrécupérable en cas de perte du
  // moyen d'accès (voir ConnexionMethodsCard).
  auth_methods: AuthProvider[]
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
  /** Nombre de cours publiés dans cette matière. Servi par /catalog/subjects/ seul
   * (voir SubjectListSerializer côté backend) - absent des Subject imbriqués dans un
   * Cours ou une Épreuve, d'où l'optionnalité. */
  cours_count?: number
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

export interface Temoignage {
  id: number
  auteur_nom: string
  auteur_description: string
  contenu: string
  note: number | null
}

export interface PlatformStats {
  corriges_disponibles: number
  cours_disponibles: number
  pays_actifs: number
}

export type EpreuveType = "FICHE" | "CORR" | "SUJET"

export interface EpreuveRelatedCours {
  id: number
  slug: string
  titre: string
  has_access: boolean
}

// "INEDITE" est une valeur synthétique (jamais stockée sur une Lesson) qui n'existe
// qu'au niveau de la sérialisation du catalogue fusionné - voir
// catalog.inedit_bridge.epreuve_inedite_catalogue_payload côté backend.
export type Origine = "OFFICIEL" | "BLANC" | "ETABLISSEMENT" | "AUTRE" | "INEDITE"
export type NatureEpreuve = "THEORIQUE" | "PRATIQUE"

export interface Epreuve {
  id: number
  // "inedite" = EpreuveInedite fondue dans le même catalogue que les Lesson
  // classiques (voir catalog.views.LessonListView.list) - plusieurs champs
  // classique-only (lesson_type, year, coefficient, sujet_pdf_url, related_cours)
  // n'ont alors aucun sens et valent null/[]/"" plutôt que d'exiger une union
  // discriminée sur tous les composants qui consomment ce type. slug fait exception :
  // renseigné des deux côtés (voir EpreuveInedite.slug, motif SEO/partage).
  kind: "classique" | "inedite"
  slug: string | null
  title: string
  subject: Subject
  cursus: Cursus[]
  lesson_type: EpreuveType | null
  lesson_type_display: string
  year: number | null
  duree_epreuve: string
  // Durée indicative en minutes (Blueprint.duree_minutes) - toujours null côté
  // classique, seule source de durée pour une épreuve inédite (duree_epreuve, le
  // champ classique, reste toujours vide pour elle).
  duree_minutes: number | null
  coefficient: string
  origine: Origine
  origine_display: string
  etablissement: string
  // Organisme qui ORGANISE l'examen ("Office du Baccalauréat du Cameroun", "MINESEC",
  // "Edukora" pour une épreuve inédite), à distinguer de `etablissement` qui dit où
  // l'épreuve a été composée. Vide quand l'information n'est pas disponible.
  institution: string
  nature_epreuve: NatureEpreuve | ""
  nature_epreuve_display: string
  themes: Tag[]
  has_access: boolean
  is_read: boolean
  est_vitrine: boolean
  created_at: string
  exercises_count: number
  related_cours: EpreuveRelatedCours[]
  sujet_pdf_url: string | null
  // Toujours false côté classique (déjà couvert par sujet_pdf_url, public) - seule une
  // épreuve inédite expose un sujet PDF téléchargeable via un endpoint gated (voir
  // downloadSujetPdf).
  sujet_pdf_disponible: boolean
  // Énoncé de la toute première question, en aperçu public - jamais le sujet entier
  // (contrairement à EpreuvePreview.preview_markdown côté classique, voir
  // catalog.inedit_bridge._apercu_enonce). Toujours null côté classique et dans le
  // catalogue fusionné (liste) - seulement renseigné sur la fiche détail d'une
  // épreuve inédite (voir getEpreuveInedite).
  apercu_enonce_markdown: string | null
  // Numéro de l'exercice dont provient apercu_enonce_markdown (ExerciceInedite.
  // numero_exercice, ex. "1") - même règle de présence que ce dernier (null si pas
  // d'aperçu). Affiché en référence sous l'aperçu, voir EpreuveInediteDetailPage.tsx.
  apercu_numero_exercice: string | null
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
  // Organisme organisateur - null quand il n'est pas connu (examen blanc sans
  // organisateur identifié, pays dont le référentiel n'est pas encore renseigné).
  institution: string | null
  // Théorique/Pratique - null quand cette distinction n'existe pas pour la matière ou
  // n'a pas pu être déterminée (jamais deviné à l'ingestion, voir NatureEpreuve).
  nature: string | null
  pays: Pays
}

export interface EpreuveExercise {
  numero_exercice: string
  // Libellé de l'exercice extrait de son en-tête d'énoncé ("Exercice 1 : Chimie
  // organique") - chaîne vide quand l'épreuve source n'en portait aucun, le sommaire
  // retombe alors sur "Exercice {numero_exercice}". Barème retiré du titre, exposé à
  // part dans points ("5"), lui aussi vide quand inconnu. Voir
  // catalog.rendering._exercise_titre_et_points.
  titre: string
  points: string
  // Pile de repères de groupe (Partie/section romaine/matière) à laquelle appartient
  // l'exercice, du plus englobant au plus précis ("Partie A", "I. Activités
  // Numériques") - [] pour la grande majorité des épreuves (aucun groupe détecté),
  // auquel cas EpreuveSommaire affiche un sommaire plat, inchangé. Voir
  // catalog.rendering._exercise_group_paths/_simplify_group_label.
  groupes: string[]
  // Référence de l'exercice ("**Exercice 1 (6 points)**") + préambule partagé par
  // ses sous-questions - toujours affiché, même en lecture directe du corrigé (voir
  // EpreuveReaderPage). Distinct de enonce_markdown, qui ne porte plus que les
  // énoncés des sous-questions (repliés par défaut derrière EnonceToggle).
  enonce_intro_markdown: string
  enonce_markdown: string
  corrige_markdown: string
}

export interface EpreuveContent {
  id: number
  title: string
  content_markdown: string
  // Consigne(s) valables pour l'épreuve ENTIÈRE ("le candidat traitera un seul sujet
  // au choix", "l'épreuve comporte deux parties indépendantes") - chaîne vide la
  // plupart du temps (rare dans le corpus). Affichée une seule fois, avant le
  // sommaire/premier exercice - jamais dans `exercises`, voir EpreuveExercise.
  introduction_markdown: string
  // Vide pour un contenu non sectionné (ex. FICHE) - la page de lecture retombe
  // alors sur content_markdown tel quel plutôt que d'afficher un article vide.
  exercises: EpreuveExercise[]
  header: EpreuveHeader
  lesson_type: EpreuveType
  sujet_pdf_url: string | null
}

/**
 * Un exercice du sujet public : l'énoncé complet (préambule inclus), jamais le moindre
 * champ de corrigé - voir catalog.rendering.lesson_preview_exercises, servi par une vue
 * AllowAny. Distinct de EpreuveExercise, réservé à la lecture abonnée.
 */
export interface EpreuvePreviewExercise {
  numero_exercice: string
  titre: string
  points: string
  // Voir EpreuveExercise.groupes - même mécanique, exposée aussi côté sujet public.
  groupes: string[]
  enonce_markdown: string
}

export interface EpreuvePreview {
  id: number
  title: string
  preview_markdown: string
  // Voir EpreuveContent.introduction_markdown - même consigne d'épreuve, exposée
  // aussi côté sujet public (jamais de corrigé dedans, uniquement la consigne).
  introduction_markdown: string
  // Le même sujet découpé par exercice - vide pour une Lesson sans Exercise (FICHE...),
  // la fiche retombe alors sur preview_markdown tel quel.
  exercises: EpreuvePreviewExercise[]
  header: EpreuveHeader
}

export interface CoursApercuContenu {
  has_exemple_resolu: boolean
  exercices_count: number
}

export interface Cours {
  id: number
  slug: string
  titre: string
  subject: Subject
  cursus: Cursus[]
  sous_theme: string
  duree_estimee_min: number | null
  tags: Tag[]
  has_access: boolean
  is_read: boolean
  // Gratuit dès qu'au moins une épreuve source de ce cours est elle-même vitrine
  // (voir catalog.Cours.est_vitrine côté backend) - distinct de has_access, qui vaut
  // aussi true pour un abonné payant. Sert uniquement à afficher "Gratuit" plutôt
  // qu'à décider l'accès : has_access reste la seule source de vérité pour ça.
  est_vitrine: boolean
  apercu_contenu: CoursApercuContenu
  created_at: string
}

export interface CoursHeader {
  matiere: string
  serie: string | null
  sous_theme: string | null
  duree_estimee_min: number | null
  pays: Pays
}

export interface CoursSectionAccroche {
  type: "accroche"
  body_markdown: string
}

export interface CoursSectionPrerequisItem {
  label: string
  cours_slug: string | null
}

export interface CoursSectionPrerequis {
  type: "prerequis"
  items: CoursSectionPrerequisItem[]
}

export interface CoursSectionRegleVariante {
  nom: string | null
  quand_utiliser: string | null
  body_markdown: string
}

export interface CoursSectionRegle {
  type: "regle"
  titre: string
  body_markdown: string
  formule_markdown: string | null
  variantes: CoursSectionRegleVariante[]
}

export interface CoursSectionExempleResoluEtape {
  numero: string | number | null
  action: string | null
  justification: string | null
  resultat_markdown: string | null
  // Rempli seulement pour une étape fournie en chaîne nue (numero/action/justification
  // alors tous null) - voir catalog.rendering._build_exemple_resolu_section_data.
  body_markdown: string | null
}

export interface CoursSectionExempleResolu {
  type: "exemple_resolu"
  enonce_markdown: string
  etapes: CoursSectionExempleResoluEtape[]
  conclusion_markdown: string | null
}

export interface CoursSectionErreurItem {
  erreur_markdown: string
  pourquoi_faux: string | null
  correction_markdown: string | null
}

export interface CoursSectionErreursClassiques {
  type: "erreurs_classiques"
  items: CoursSectionErreurItem[]
}

export interface CoursSectionExerciceItem {
  numero: string | number | null
  difficulte: string | null
  enonce_markdown: string
  solution_markdown: string | null
}

export interface CoursSectionExercicesApplication {
  type: "exercices_application"
  items: CoursSectionExerciceItem[]
}

export interface CoursSectionSynthese {
  type: "synthese"
  body_markdown: string
}

export type CoursSectionData =
  | CoursSectionAccroche
  | CoursSectionPrerequis
  | CoursSectionRegle
  | CoursSectionExempleResolu
  | CoursSectionErreursClassiques
  | CoursSectionExercicesApplication
  | CoursSectionSynthese

export interface CoursContent {
  id: number
  title: string
  content_markdown: string
  sections: CoursSectionData[]
  header: CoursHeader
}

export interface CoursPreview {
  id: number
  title: string
  preview_markdown: string
  sections: CoursSectionData[]
  header: CoursHeader
}

// Formes allégées, pas Epreuve/Cours au complet : /access/progression/ liste TOUT
// l'historique de lecture d'un utilisateur (aucune pagination), et seuls
// id/slug/title(ou titre)/subject.country.code y sont réellement lus - voir
// "Reprendre ma lecture" sur CataloguePage.tsx/CoursListPage.tsx et "Ma progression"
// sur AccountPage.tsx (backend : access.views._LessonProgressionSerializer /
// _CoursProgressionSerializer, qui n'exposent plus les champs coûteux du catalogue
// complet - exercises_count, related_cours, has_access... - inutiles ici).
export interface ProgressionEpreuve {
  id: number
  slug: string | null
  title: string
  subject: { country: { code: string } }
}

export interface ProgressionCours {
  id: number
  slug: string
  titre: string
}

export interface Progression {
  lessons: ProgressionEpreuve[]
  cours: ProgressionCours[]
}

export type DureeMode = "FIXE" | "JUSQUA_EXAMEN"

export type ProductType = "ABONNEMENT" | "ADDON_INEDIT" | "ADDON_REPETITEUR"

export interface Plan {
  id: number
  name: string
  cursus: Cursus
  product_type: ProductType
  price: number
  duration_mode: DureeMode
  duration_days: number
  effective_duration_days: number
  effective_price: number
  inclut_inedit: boolean
}

export interface Subscription {
  id: number
  cursus: Cursus
  expires_at: string
  is_active: boolean
  plan_name: string | null
  duration_mode: DureeMode
}

export interface ThemeFrequent {
  id: number
  tag: string
  nb_epreuves: number
  frequence_pct: number
  // false = aucune CompetenceItem pour ce thème sur ce cursus (couverture Quiz
  // incomplète, voir la campagne de rattachement au référentiel) - le bouton "Quiz"
  // doit se désactiver plutôt que mener à une session vide.
  quiz_disponible: boolean
}

export interface ThemesFrequentsResponse {
  nb_sessions_disponibles: number
  seuil_minimum: number
  // false = corpus encore trop petit pour un classement fiable (voir
  // catalog.views.SEUIL_MINIMUM_THEMES_FREQUENTS) - `themes` est alors toujours vide,
  // distinct de `has_access=false` (classement disponible mais verrouillé).
  disponible: boolean
  has_access: boolean
  nb_themes_verrouilles: number
  themes: ThemeFrequent[]
}

export interface ThemeExercice {
  lesson_slug: string
  lesson_title: string
  lesson_year: number | null
  numero_exercice: string
  has_access: boolean
}

export interface ThemeExercicesResponse {
  tag: string
  exercices: ThemeExercice[]
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
  amount: number
  credit_applique: number
}

export interface PaymentStatusResponse {
  status: TransactionStatus
  subscription_active: boolean
}

export type MobileMoneyOperator = "ORANGE" | "MTN"

export interface MobileMoneyAccount {
  operator: MobileMoneyOperator
  operator_display: string
  phone_number: string
  account_name: string
}

export type ManualPaymentStatus = "PENDING" | "APPROVED" | "REJECTED"

export interface ManualPayment {
  id: number
  plan: Plan
  operator: MobileMoneyOperator
  operator_display: string
  amount_expected: number
  amount_declared: number
  payer_phone_number: string
  transaction_reference: string
  paid_at: string | null
  status: ManualPaymentStatus
  status_display: string
  rejection_reason: string
  rejection_reason_display: string
  created_at: string
  reviewed_at: string | null
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

export interface ParcoursCours {
  slug: string
  titre: string
}

export interface ParcoursSavoir {
  id: number
  numero: string
  intitule: string
  // null = jamais tenté, distinct de 0 (tenté, en échec) - voir
  // quiz.services.construire_parcours côté backend.
  taux: number | null
  en_revision: boolean
  a_lu_le_cours: boolean
  has_quiz: boolean
  cours: ParcoursCours | null
}

export interface ParcoursModule {
  numero: string
  titre: string
  savoirs: ParcoursSavoir[]
}

export interface ResumeMatiere {
  subject_id: number
  subject_code: string
  subject_label: string
  total: number
  maitrises: number
  en_revision: number
  a_decouvrir: number
  sans_contenu: number
}

export interface InscriptionInedite {
  id: number
  cursus: Cursus
  expires_at: string
  is_active: boolean
}

export interface EpreuveInediteListItem {
  id: number
  titre: string
  subject_label: string
  duree_minutes: number | null
  created_at: string
}

export interface TentativeInediteListItem {
  id: number
  epreuve: number
  epreuve_titre: string
  subject_label: string
  cursus_display: string
  started_at: string
  submitted_at: string | null
  score_obtenu: number | null
}

export interface TentativeInediteAnswerInfo {
  reponse_choisie: string
  resultat_declare: string
  // Absent tant que la correction n'est pas disponible pour la tentative (mode
  // examen actif, voir inedit.views._correction_disponible côté backend) - sinon
  // trahirait la bonne réponse pendant une fenêtre chronométrée active.
  est_correcte?: boolean
}

export interface TentativeInediteQuestion {
  id: number
  numero: string
  ordre: number
  // Repère de sous-partie propre à CETTE question (ex. "A-I. Vérification des savoirs
  // (4 pts)") - affiché en en-tête au-dessus quand il diffère de celui de la question
  // précédente (voir InediteTentativePage.tsx). Chaîne vide pour la grande majorité
  // des questions ; jamais gaté par la correction, contrairement à corrige_markdown.
  groupe_local: string
  enonce_markdown: string
  type_reponse: TypeReponse
  choix: QuizChoix[]
  // Présents uniquement quand la correction est disponible pour la tentative (voir
  // TentativeInedite.correction_disponible), pas seulement une fois répondu.
  corrige_markdown?: string
  reponse_correcte?: string
  reponse?: TentativeInediteAnswerInfo
}

export interface TentativeInediteExercice {
  id: number
  numero_exercice: string
  points: string
  // Pile de repères de groupe (Partie/section/matière) - [] pour la grande majorité
  // des épreuves. Voir InediteTentativePage.tsx : affiché en en-tête au-dessus du
  // badge "Exercice N" quand il change, jamais comme sommaire cliquable (contrairement
  // à EpreuveSommaire.tsx côté épreuves classiques - pas de saut en avant pendant un
  // examen chronométré).
  groupes: string[]
  // Support partagé par les questions de l'exercice (document à exploiter, tableau
  // de résultats...) - affiché une seule fois en tête d'exercice, jamais répété
  // question par question. Chaîne vide pour la plupart des exercices.
  enonce_intro_markdown: string
  questions: TentativeInediteQuestion[]
}

export interface TentativeInedite {
  id: number
  epreuve: number
  epreuve_titre: string
  // Code pays (ex. "CM") - permet de reconstruire une URL de catalogue préfixée
  // pays (voir InediteTentativePage.tsx) sans requête supplémentaire.
  country: string
  cursus_display: string
  duree_minutes: number | null
  // Permet d'ouvrir le sujet en PDF depuis la page de tentative elle-même (voir
  // downloadSujetPdf) - même signal que Epreuve.sujet_pdf_disponible sur la fiche.
  sujet_pdf_disponible: boolean
  started_at: string
  // Renseigné uniquement si l'élève a activé le mode examen (chronométré) - voir
  // inedit.models.TentativeInedite.exam_mode_started_at.
  exam_mode_started_at: string | null
  submitted_at: string | null
  score_obtenu: number | null
  correction_disponible: boolean
  questions_marquees: number[]
  exercices: TentativeInediteExercice[]
}

export interface TentativeInediteCorrige {
  corrige_markdown: string
  reponse_correcte: string
}

export type Difficulte = "FAIBLE" | "MOYENNE" | "ELEVEE"

export interface InscriptionRepetiteur {
  id: number
  cursus: Cursus
  expires_at: string
  is_active: boolean
}

export interface FicheThemeEligible {
  theme_id: number
  theme: string
  total: number
  par_difficulte: Partial<Record<Difficulte, number>>
}

export type FicheStatut = "EN_COURS" | "PRETE" | "ECHEC"

export interface WhatsAppStatus {
  opted_in: boolean
}

export interface Fiche {
  id: number
  titre: string
  cursus: number
  cursus_display: string
  subject_label: string
  themes: string[]
  difficulte: Difficulte | ""
  nombre_questions: number
  statut: FicheStatut
  sujet_pdf_disponible: boolean
  corrige_pdf_disponible: boolean
  created_at: string
}

export interface TentativeInediteResult {
  id: number
  epreuve: number
  // Voir la note équivalente dans TentativeInedite.
  country: string
  total_questions: number
  questions_repondues: number
  score: number | null
  temps_total_secondes: number | null
  par_theme: QuizThemeScore[]
}
