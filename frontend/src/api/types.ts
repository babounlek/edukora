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
  // Ce que l'utilisateur déclare préparer (voir users.models.User.cursus_prepare) -
  // indépendant de ses abonnements : un visiteur non abonné en a un dès qu'il l'a dit.
  cursus_prepare: Cursus | null
  // null tant qu'aucun cursus n'est déclaré, ou qu'aucune session d'examen n'est
  // saisie pour ce (pays, examen) - voir ExamSession.compte_a_rebours_pour.
  compte_a_rebours: CompteARebours | null
  // Tous cursus confondus - sert au Header à masquer "Tarifs" pour qui a déjà payé.
  a_un_abonnement_actif: boolean
  // Rappel quotidien de la séance par e-mail (voir relances.services) : jamais actif sans
  // e-mail confirmé, et jamais activé d'office.
  rappels_actifs: boolean
  // L'élève a écarté l'invitation à les activer : on ne la lui représente plus.
  rappels_invite_refusee: boolean
  // Bilan de la semaine envoyé chaque dimanche au titulaire du compte (voir
  // relances.bilan_parent) : même règle d'e-mail confirmé, et réservé au mode parent.
  bilan_parent_actif: boolean
  // L'enfant actif pour cette requête (voir users.profils.profil_actif) - jamais null
  // pour un compte normalement créé, voir sa docstring côté backend.
  profil_actif: Profil
  pin_parent_actif: boolean
  session_restreinte: boolean
}

/** Une étape de la séance du jour - voir quiz.services._construire_etapes. */
// `cle` : identifiant stable renvoyé au serveur à l'ouverture ; `ouverte` : l'élève a déjà
// ouvert cette étape (le quiz : sa session est lancée). Voir quiz.services.cle_etape.
export type EtapeSeance = EtapeSeanceContenu & { cle: string; ouverte: boolean }

type EtapeSeanceContenu =
  | { type: "cours"; libelle: string; slug: string; titre: string; duree_min: number }
  | {
      type: "exercice"
      libelle: string
      // Permet de marquer l'exercice comme fait a la cloture de la seance (voir
      // terminer_seance) - sans quoi la file d'entrainement le reproposerait.
      exercise_id: number
      lesson_slug: string
      lesson_title: string
      lesson_year: number | null
      numero_exercice: string | null
      duree_min: number
    }
  | { type: "quiz"; libelle: string; mode: ModeQuiz; n: number; duree_min: number }

/** Ce que renvoie une séance verrouillée (voir quiz.views._etape_verrouillee côté
 * backend) : la structure du parcours - quel type d'étape, combien de temps - sans
 * rien qui identifie ou ouvre le contenu précis derrière le paywall. */
export interface EtapeSeanceVerrouillee {
  type: "cours" | "exercice" | "quiz"
  libelle: string
  duree_min: number
}

export interface Seance {
  id: number
  origine: "REVISION_DUE" | "LECTURE_EN_COURS" | "DIAGNOSTIC" | "PARCOURS"
  origine_display: string
  subject: Subject | null
  theme: { id: number; name: string } | null
  savoir: { id: number; intitule: string } | null
  duree_estimee_min: number
  // Temps que l'élève s'est donné, et les choix possibles. Un plafond : la durée
  // réelle ci-dessus peut être inférieure quand le contenu manque.
  budget_minutes: number
  budgets_possibles: number[]
  nb_etapes: number
  // Quand `verrouillee`, chaque étape est réduite à EtapeSeanceVerrouillee (type +
  // durée, sans `cle`/`ouverte` ni rien qui ouvre le contenu) - voir _serialiser_seance.
  // `seance.verrouillee` dit sans ambiguïté laquelle des deux formes s'applique.
  etapes: EtapeSeance[] | EtapeSeanceVerrouillee[]
  // "tombé dans 8 des 10 dernières épreuves" - null si le thème n'est jamais tombé,
  // ou si la séance n'en cible pas (calibrage).
  // `annees` : les années réellement concernées, pour que "tombé dans 11 des 21
  // dernières épreuves" soit vérifiable plutôt qu'à croire sur parole.
  frequence: { occurrences: number; epreuves_total: number; annees: number[] } | null
  // Pourquoi cette séance-là : des faits déjà en base (coefficient transcrit, date du
  // ratage, thème jamais travaillé), jamais une reformulation de l'intention. Le
  // `code` pilote l'icône, le texte vient du serveur qui seul a les chiffres.
  raisons: { code: string; texte: string }[]
  // Échéance de révision de ce thème (paliers Leitner), quand il y en a une. Null
  // quand le thème n'est pas dans la file : annoncer une révision serait faux.
  prochaine_revision: string | null
  // Profondeur disponible derriere l'etape d'entrainement : la seance n'en propose
  // qu'un ou deux par budget de temps, pas par manque de contenu.
  exercices_total: number
  statut: "PROPOSEE" | "TERMINEE"
  // Résultat du quiz de la séance, une fois la session terminée - null quand il n'y a
  // rien à noter (voir quiz.services.score_de_la_seance).
  score: { reussies: number; total: number } | null
  verrouillee: boolean
}

/** Réponse de GET /quiz/plan-du-jour/ - voir quiz.views.plan_du_jour_view. */
export interface PlanDuJour {
  etat: "cursus_inconnu" | "examen_passe" | "rien_a_proposer" | "deja_fait_aujourdhui" | "plan_pret"
  cursus: Cursus | null
  compte_a_rebours: CompteARebours | null
  seance: Seance | null
  // Absent quand aucun cursus n'est déclaré : il n'y a alors pas de semaine à compter.
  seances_cette_semaine?: number
  xp?: EtatXp
  // Voir quiz.models.ObjectifMatiere : la matière que l'élève a choisie pour la semaine.
  objectif_matiere?: ObjectifMatiereChoisi | null
  // Matières qu'on peut choisir (celles qui ont un quiz sur ce cursus).
  matieres_objectif?: { id: number; label: string }[]
  serie?: SerieDeJours
}

/** Voir quiz.serie : jours de suite avec une séance terminée, un jour de repos pardonné par
 * semaine. */
export interface SerieDeJours {
  jours: number
  record: number
  actif_aujourdhui: boolean
  // Un jour de repos a été pardonné dans les 7 derniers jours.
  repos_pris: boolean
  // La semaine civile en cours, lundi à dimanche (voir quiz.serie.semaine_courante).
  semaine?: JourDeSemaine[]
}

export interface JourDeSemaine {
  // AAAA-MM-JJ, jour local.
  date: string
  fait: boolean
  aujourdhui: boolean
}

/** Voir quiz.xp : où en est le profil aujourd'hui. L'XP récompense la maîtrise, pas le volume. */
export interface EtatXp {
  xp: number
  objectif: number
  atteint: boolean
  objectifs_possibles: number[]
}

/** Voir relances.views.paiement_a_reprendre_view. */
export interface PaiementAReprendre {
  a_reprendre: boolean
  montant?: number
  cursus_id?: number
  statut?: "PENDING" | "FAILED"
  depuis?: string
}

export interface ObjectifMatiereChoisi {
  subject: number
  label: string
  // AAAA-MM-JJ, dernier jour inclus.
  jusqu_au: string
}

/** Voir catalog.models.ExamSession.compte_a_rebours_pour. */
export interface CompteARebours {
  // AAAA-MM-JJ.
  date_examen: string
  jours_restants: number
  // Ex. "BAC 2027" - porte l'année réellement décomptée, estimée ou non.
  session_label: string
  // Vrai quand la date officielle n'est pas encore saisie et qu'on a décalé la
  // dernière session connue : à n'afficher qu'au mois, jamais au jour.
  estimee: boolean
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
  /** Nombre de questions de quiz VALIDE disponibles. Servi par /quiz/subjects/ seul
   * (voir SubjectWithQuizCountSerializer côté backend), affiché même sans abonnement
   * actif - voir project_gating_non_abonne_quiz_parcours. */
  nb_questions?: number
  /** Thème jouable en entier sans abonnement (voir CompetenceItem.est_vitrine côté
   * backend), null si cette matière n'a pas de thème vitrine curé. Servi par
   * /quiz/subjects/ seul, comme nb_questions. */
  vitrine_theme_id?: number | null
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
  // Copie non rendue de l'élève connecté sur cette épreuve inédite - uniquement sur la
  // fiche détail (voir inedit.views.epreuve_inedite_detail), absent de la liste. null
  // pour un visiteur ou quand rien n'est engagé.
  tentative_en_cours?: TentativeEnCours | null
  // Où en est l'élève connecté de cette épreuve inédite (liste ET fiche) : null si jamais
  // ouverte ou visiteur. Alimente « Faite · 12/20 » et « Reprendre » sur les cartes.
  mes_tentatives?: MesTentatives | null
}

export interface MesTentatives {
  en_cours: boolean
  nb_terminees: number
  // Note de la copie au meilleur taux (pas aux meilleurs points bruts) - null tant qu'aucune
  // copie rendue n'a de note.
  meilleure_note: number | null
  bareme: number | null
}

/** Résumé d'une copie d'épreuve inédite entamée : de quoi proposer « Reprendre » sur la fiche. */
export interface TentativeEnCours {
  id: number
  started_at: string
  // Renseigné seulement si le chrono a été lancé ; `echeance` est alors l'heure où la
  // copie sera rendue d'office.
  exam_mode_started_at: string | null
  echeance: string | null
  mode_papier: boolean
  traitees: number
  total: number
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
  // Identifiant reel de l'Exercise - present en lecture abonnee, absent des apercus
  // publics et des epreuves inedites. Ce qui permet de valider sa resolution.
  id?: number
  // Declare par l'eleve a la fin du corrige (voir access.ExerciceFait).
  fait?: boolean
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

export type ProductType = "ABONNEMENT" | "ADDON_REPETITEUR"

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
  /** Tarif d'un enfant supplémentaire de la même famille (remise fixe de 20 %). */
  prix_enfant_supplementaire: number
  inclut_inedit: boolean
}

/** L'enfant pour qui un abonnement est payé - voir users.models.Profil. */
export interface Profil {
  id: number
  prenom: string
  ordre: number
  pin_actif: boolean
  connexion_active: boolean
}

export interface Subscription {
  id: number
  cursus: Cursus
  profil: Profil
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

/** Matière proposée au choix sur /themes-frequents (voir ThemesFrequentsMatieresView) :
 * seulement celles qui ont des épreuves officielles sur le cursus choisi. */
export interface ThemesFrequentsMatiere {
  code: string
  label: string
  nb_sessions: number
  // false = sous le seuil minimum, le classement ne serait pas fiable.
  disponible: boolean
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
  // Identifiant de l'Exercise - ce qui permet de le marquer comme fait. Le couple
  // (slug, numero) ne suffit pas : c'est un libelle d'affichage.
  exercise_id: number
  lesson_slug: string
  lesson_title: string
  lesson_year: number | null
  // Chaîne brute plutôt que Origine : le backend peut aussi renvoyer SUJET_ZERO.
  origine: string
  numero_exercice: string
  has_access: boolean
  // Declare par l'eleve (voir access.ExerciceFait), jamais deduit d'une ouverture.
  fait: boolean
}

/** Un (examen, matière) où le thème est traité - alimente le choix de l'examen et de la
 * matière sur ThemeExercicesPage, sans jamais proposer une combinaison vide. */
export interface ThemeExercicesContexte {
  cursus_id: number
  subject_code: string
  subject_label: string
  nb_exercices: number
}

/** Une question d'un exercice lu seul depuis un thème (voir ThemeExerciceLectureView). */
export interface QuestionLecture {
  numero: string
  enonce_markdown: string
  // null sans accès : les énoncés sont publics, jamais les corrigés.
  corrige_markdown: string | null
  // Vrai si la question porte le thème d'où l'on vient - surlignée à l'écran.
  sur_le_theme: boolean
}

export interface ExerciceLecture {
  exercise: { id: number; numero_exercice: string; titre: string; points: string; fait: boolean }
  lesson: {
    slug: string
    title: string
    year: number | null
    origine: string
    subject_code: string
    subject_label: string
    introduction_markdown: string
  }
  theme: { id: number; name: string }
  has_access: boolean
  enonce_intro_markdown: string
  // null quand l'exercice ne se découpe pas fidèlement par question : afficher alors
  // enonce_markdown/corrige_markdown en un seul bloc, sans surlignage.
  questions: QuestionLecture[] | null
  enonce_markdown: string
  corrige_markdown: string | null
}

export interface ThemeExercicesResponse {
  tag: string
  exercices: ThemeExercice[]
  total: number
  faits: number
  contextes: ThemeExercicesContexte[]
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
  // Points d'XP gagnés par cette réponse : 0 si fausse, déjà créditée ou plafonnée.
  xp_gagne?: number
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
  // Id du thème et code matière (CompetenceItem seulement) : lien vers les exercices
  // corrigés du thème (/themes-frequents/<id>/exercices).
  theme_id?: number
  subject_code?: string
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
  // Seulement dans la réponse à l'envoi d'une réponse (voir quiz.views.answer_question).
  xp_jour?: EtatXp
  // Cette réponse est celle qui a fait franchir l'objectif du jour.
  objectif_atteint_maintenant?: boolean
}

export interface QuizSession {
  id: number
  mode: ModeQuiz
  cursus: number
  subject: number | null
  cursus_display: string
  started_at: string
  completed_at: string | null
  total_questions: number
  xp_jour?: EtatXp
  questions: QuizQuestion[]
}

export interface QuizCorrige {
  corrige_markdown: string
  reponse_correcte: string
}

export interface QuizCoursSuggere {
  id: number
  slug: string
  titre: string
  has_access: boolean
}

export interface QuizThemeScore {
  theme: string
  theme_id: number
  // null pour une question historique (catalog.Question) : pas de lien vers le thème.
  subject_code: string | null
  total: number
  reussies: number
  // Renseigné seulement pour un thème sous le seuil de maîtrise ET couvert par un cours
  // publié (voir quiz.views._resultat_payload). Absent des résultats d'épreuves inédites.
  cours?: QuizCoursSuggere | null
}

export interface QuizResult {
  id: number
  cursus: number
  subject: number | null
  total_questions: number
  questions_repondues: number
  score: number
  meilleure_serie: number
  seances_cette_semaine: number
  par_theme: QuizThemeScore[]
  // Ce quiz était l'étape finale d'une séance du jour et l'a validée.
  seance_validee: boolean
  mode: ModeQuiz
  // Questions ratées qu'on peut re-proposer telles quelles (voir refaireLesRatees).
  nb_ratees: number
  // Ce que ce quiz a rapporté (réponses + bonus de séance) et où en est la journée.
  xp?: { session: { reponses: number; seance: number; total: number }; jour: EtatXp }
  // La série de jours et sa semaine, pour l'écran de fin (voir quiz.serie).
  serie?: SerieDeJours
  // Où se situe l'élève parmi les candidats de son cursus cette semaine (voir quiz.classement) :
  // une bande, jamais un rang. `bande` est null presque tout le temps, c'est voulu.
  classement?: { disponible: boolean; bande: "quart" | "moitie" | null }
}

export interface QuizFichePdfStatus {
  statut: "" | "EN_COURS" | "PRETE" | "ECHEC"
  sujet_pdf_disponible: boolean
  corrige_pdf_disponible: boolean
}

export interface ParcoursCours {
  slug: string
  titre: string
  // Court, curaté pour l'affichage (voir catalog.Cours.sous_theme) - typiquement
  // plus lisible en libellé de bouton que `titre`, qui peut être une phrase entière.
  sous_theme: string
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
  // Plusieurs cours peuvent couvrir un même savoir (voir
  // quiz.services.PARCOURS_COURS_PAR_SAVOIR_MAX côté backend) - tableau plutôt
  // qu'un cours unique, potentiellement vide plutôt que null.
  cours: ParcoursCours[]
  // Présent (= id d'un catalog.Tag) uniquement pour les matières en mode Parcours
  // par fréquence (voir quiz.services.SUBJECTS_PARCOURS_PAR_FREQUENCE côté
  // backend) - absent/null pour le Module→Savoir classique, où `id` désigne un
  // programme.Savoir. Distingue laquelle des deux sémantiques `id` porte ici :
  // /quiz/sessions/ et /catalog/cours/ n'acceptent pas le même paramètre selon le
  // cas (theme= vs savoir=).
  theme_id?: number | null
  // Additifs, présents seulement en mode fréquence - voir la même docstring.
  savoir_label?: string | null
  nb_epreuves?: number
  frequence_pct?: number
}

export interface ParcoursModule {
  numero: string
  titre: string
  savoirs: ParcoursSavoir[]
}

/**
 * Une ligne de la file "à réviser" (voir quiz.views.list_revisions_dues). L'endpoint
 * existait déjà, testé, mais AUCUN écran ne l'appelait : la page /revision qui le
 * consommait a été redirigée vers /parcours, et la donnée est restée invisible
 * depuis. C'est AccueilEleve qui la fait enfin remonter.
 */
export interface RevisionDue {
  id: number
  theme: string
  theme_id: number
  subject_id: number
  subject_label: string
  cursus: number
  cursus_display: string
  // 0 = due aujourd'hui ; au-delà, le thème est en retard.
  jours_retard: number
  cours: Cours[]
}

export interface ResumeMatiere {
  subject_id: number
  subject_code: string
  subject_label: string
  total: number
  maitrises: number
  en_revision: number
  // Taux connu (déjà pratiqué au moins une fois) mais ni maîtrisé ni actuellement dû
  // en révision - distinct de a_decouvrir, qui n'a jamais été pratiqué du tout. Sans
  // cette distinction, un thème longuement travaillé (mais dont la moyenne
  // historique reste sous le seuil) redevenait indiscernable d'un thème jamais
  // ouvert dès qu'il quittait la file de révision - voir
  // quiz.services.resume_parcours côté backend.
  en_cours: number
  a_decouvrir: number
  sans_contenu: number
  // "Ce qui tombe vraiment" : somme des poids (coefficient x fréquence, voir
  // quiz.services.poids_savoir) des savoirs exploitables, et la part déjà maîtrisée.
  poids_total: number
  poids_maitrise: number
}

/** Phase de la préparation, d'après les jours restants (voir quiz.accueil.phase_examen). */
export type PhaseExamen = "normal" | "simulation" | "derniere_ligne_droite" | "veille" | "jour_j" | "apres"

/** Ce qui a changé depuis la visite précédente (voir quiz.accueil.delta_depuis). Null
 * sans visite précédente ou quand rien n'a bougé. */
export interface DepuisLaDerniereVisite {
  // AAAA-MM-JJ.
  depuis: string
  seances: number
  questions: number
  themes_consolides_total: number
  themes_consolides: { theme: string; subject_label: string }[]
  matiere_en_hausse: { subject_id: number; subject_label: string; gain: number } | null
  revisions_tenues: number
}

/** Où mène le rythme actuel (voir quiz.accueil.trajectoire). Les champs de projection
 * sont null tant qu'il n'y a pas de rythme mesurable. */
export interface Trajectoire {
  jours_restants: number
  fenetre_jours: number
  seances_fenetre: number
  seances_par_semaine: number | null
  couverture_actuelle: number
  couverture_projetee: number | null
  cible: number
  suffisant: boolean | null
  seances_de_plus_par_semaine: number | null
  // Faux quand même en travaillant tous les jours la cible n'est plus atteignable.
  atteignable: boolean | null
}

export interface PreparationExamen {
  // Part pondérée de ce qui tombe vraiment (0-1) - c'est l'anneau.
  ponderee: number
  // Part brute des savoirs exploitables (0-1) - le "12 sur 40" sous l'anneau.
  brute: number
  maitrises: number
  exploitables: number
}

/** Une ligne "à réviser" réduite pour l'accueil (voir views.accueil_view). */
export interface RevisionAccueil {
  id: number
  theme: string
  theme_id: number
  subject_id: number
  subject_label: string
  cursus: number
  jours_retard: number
}

/** Réponse de GET /quiz/accueil/ - tout l'accueil d'un abonné en une requête. */
export interface Accueil {
  plan: PlanDuJour
  phase: PhaseExamen
  absence_jours: number
  premiers_pas: boolean
  nouvelle_visite: boolean
  phrase_coach: string
  depuis: DepuisLaDerniereVisite | null
  trajectoire: Trajectoire | null
  resume: ResumeMatiere[]
  preparation: PreparationExamen | null
  revisions: RevisionAccueil[]
  lecture: { slug: string; title: string; country: string } | null
  simulation_suggeree: { id: number; slug: string; title: string; subject_label: string; year: number | null } | null
  bilan_semaine: BilanPeriode | null
}

export interface InscriptionInedite {
  id: number
  cursus: Cursus
  profil: Profil
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
  exam_mode_started_at: string | null
  // Heure à laquelle la copie en cours est rendue d'office (chrono lancé) - null sinon.
  echeance: string | null
  submitted_at: string | null
  score_obtenu: number | null
  // Note en points sur bareme_snapshot (voir inedit.notation) - null tant que la
  // tentative n'est pas rendue.
  note_obtenue: number | null
  bareme_snapshot: number | null
}

export interface TentativeInediteAnswerInfo {
  reponse_choisie: string
  resultat_declare: string
  // Absents tant que la correction n'est pas disponible pour la tentative (mode
  // examen actif, voir inedit.views._correction_disponible côté backend) - sinon
  // trahirait la bonne réponse pendant une fenêtre chronométrée active.
  est_correcte?: boolean
  // Question ouverte : les points ont été attribués (sinon elle reste « à noter »).
  notee?: boolean
  // null tant que la question n'est pas notée.
  points_obtenus?: number | null
  criteres_valides?: number[]
  // Pourquoi des points ont été perdus, déclaré par l'élève ("" = non précisé).
  cause_perte?: string
}

/** Un critère de la grille de notation d'une question ouverte (voir
 * QuestionInedite.criteres_notation) - servi seulement avec le corrigé. */
export interface CritereNotation {
  libelle: string
  points: number
}

/** Bloc `notation` : note provisoire ou définitive d'une tentative. Absent (null) tant que
 * le corrigé est masqué - la note inclut les QCM, elle trahirait leur correction. */
export interface NotationResume {
  note: number | null
  bareme: number | null
  note_sur_20: number | null
  // Les points de l'exercice sont répartis à parts égales : à annoncer comme estimés.
  bareme_estime: boolean
  questions_total: number
  questions_traitees: number
  questions_non_traitees: number
  questions_a_noter: number
  // Vrai seulement une fois l'épreuve rendue ET toutes les questions traitées notées.
  definitive: boolean
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
  criteres_notation?: CritereNotation[]
  // Traitée : QCM répondu, ou question ouverte que l'élève a déclaré avoir traitée.
  traitee: boolean
  // Barème de la question ; bareme_estime = réparti à parts égales, pas un barème exact.
  points: number
  bareme_estime: boolean
  // Renvoyé avec la question après chaque écriture (answer/noter), jamais dans le
  // payload de la tentative où `notation` se trouve à la racine.
  notation?: NotationResume | null
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
  // Cette annale n'annonce pas sa propre durée : déduite des autres sessions de la même
  // (matière, examen, série, nature d'épreuve) - voir simulations.cadre.duree_minutes_pour_lesson.
  // Toujours false pour une épreuve inédite (elle porte sa propre durée depuis son Blueprint).
  duree_estimee?: boolean
  // Permet d'ouvrir le sujet en PDF depuis la page de tentative elle-même (voir
  // downloadSujetPdf) - même signal que Epreuve.sujet_pdf_disponible sur la fiche.
  sujet_pdf_disponible: boolean
  started_at: string
  // Renseigné uniquement si l'élève a activé le mode examen (chronométré) - voir
  // inedit.models.TentativeInedite.exam_mode_started_at.
  exam_mode_started_at: string | null
  // Composée sur papier : l'écran ne montre que le chrono et la liste de questions.
  mode_papier: boolean
  // "officielle" : annale simulée en conditions d'examen (voir simulations côté backend).
  source?: "officielle"
  // Ce que la page note d'un bloc : une question (défaut) ou un exercice entier (annales).
  granularite?: "question" | "exercice"
  sujet_pdf_url?: string | null
  submitted_at: string | null
  score_obtenu: number | null
  note_obtenue: number | null
  bareme_snapshot: number | null
  bareme: number | null
  bareme_estime: boolean
  notation: NotationResume | null
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
  profil: Profil
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
  // Titre de l'épreuve (ou de l'annale simulée) dont c'est le résultat.
  epreuve_titre: string
  // Voir la note équivalente dans TentativeInedite.
  country: string
  total_questions: number
  // Questions traitées (QCM répondues ou questions ouvertes déclarées traitées).
  questions_repondues: number
  questions_non_traitees: number
  questions_a_noter: number
  // Pourcentage du barème COMPLET : une question non traitée compte zéro.
  score: number | null
  note: number | null
  bareme: number | null
  note_sur_20: number | null
  bareme_estime: boolean
  definitive: boolean
  // Comment l'épreuve a été passée : une note d'entraînement ne se lit pas comme une note en conditions réelles.
  mode: "examen" | "papier" | "libre"
  // Ce que compte la page : des questions (épreuve inédite) ou des exercices (annale officielle).
  granularite: "question" | "exercice"
  temps_total_secondes: number | null
  // Rapport de fin d'épreuve : où sont partis les points, où est passé le temps, où l'on se situe.
  pertes: PertesParCause
  // null en entraînement libre, ou quand trop peu de questions ont été cochées pour estimer.
  temps_par_exercice: TempsExercice[] | null
  exercice_chronophage: string | null
  // null sous 20 candidats, ou en entraînement libre.
  comparaison: ComparaisonCandidats | null
  cursus_id: number | null
  par_exercice: TentativeInediteResultExercice[]
  par_theme: TentativeInediteResultTheme[]
  themes_a_reviser: ThemeARevoir[]
}

/** Un thème de l'épreuve qui revient dans la séance du jour (ou revient déjà). */
export interface ThemeARevoir {
  theme: string
  theme_id: number
  // AAAA-MM-JJ.
  echeance: string
}

export interface PertesParCause {
  total_perdu: number
  causes: { cause: string; libelle: string; points: number; part: number }[]
}

export interface TempsExercice {
  numero_exercice: string
  secondes: number
  part_du_temps: number
  part_des_points: number
}

export interface ComparaisonCandidats {
  effectif: number
  percentile: number
  moyenne: number
}

export interface SimulationListItem {
  id: number
  epreuve: number
  epreuve_titre: string
  started_at: string
  submitted_at: string | null
  note_obtenue: number | null
  bareme_snapshot: number | null
  score_obtenu: number | null
}

export interface TentativeInediteResultExercice {
  numero_exercice: string
  points_possibles: number | null
  points_obtenus: number | null
}

export interface TentativeInediteResultTheme {
  theme: string
  theme_id: number
  total: number
  reussies: number
  points_possibles: number | null
  points_obtenus: number | null
}

/** Bilan des 30 derniers jours d'un abonnement (voir quiz.bilan.bilan_de_periode). */
export interface BilanMatiere {
  subject_id: number
  subject_label: string
  questions: number
  taux_avant: number | null
  taux_periode: number | null
}

export interface BilanPeriode {
  debut: string
  fin: string
  expire_le: string
  abonnement_actif: boolean
  seances: number
  jours_actifs: number
  questions: number
  taux_reussite: number | null
  taux_avant: number | null
  meilleure_serie: number
  themes_travailles: number
  // Compteurs cumulés avant la période et à sa fin : de quoi calculer les jalons.
  jalons: {
    seances_total: number
    seances_avant: number
    questions_total: number
    questions_avant: number
    solides_total: number
    solides_avant: number
  }
  themes_consolides_total: number
  themes_consolides: { theme: string; subject_label: string }[]
  matieres: BilanMatiere[]
  // Faux quand il n'y a rien à raconter : le front n'affiche alors aucun bilan.
  a_de_l_activite: boolean
}

/** Une matière dans la restitution des priorités (voir quiz.priorites). */
export interface PrioriteMatiere {
  subject_id: number
  subject_label: string
  subject_code: string
  // null : aucun coefficient lisible dans les épreuves - on n'en affiche pas.
  coefficient: number | null
  reussies: number
  total: number
  // Repère qualitatif : jamais un pourcentage sur si peu de réponses.
  niveau: "a_situer" | "fragile" | "moyen" | "solide"
  // Longueur de barre relative à la première matière (0-100).
  urgence: number
  rang: number
  prioritaire: boolean
}

/** Réponse de GET /quiz/priorites/. */
export interface Priorites {
  a_deja_repondu: boolean
  diagnostic_fait: boolean
  compte_a_rebours: CompteARebours | null
  matieres: PrioriteMatiere[]
  themes_a_travailler: { theme: string; subject_label: string }[]
}

/** Ce que l'élève garde d'une section : compris, signet, note (voir access.MarqueEtude). */
export interface MarqueEtude {
  cle: string
  compris: boolean
  signet: boolean
  note: string
  updated_at: string | null
}

/** Une entrée du carnet : une marque + de quoi rouvrir la section exacte. */
export interface CarnetEntree extends MarqueEtude {
  type: "cours" | "epreuve"
  titre: string
  slug: string
  country: string
  matiere: string
}

/** Le document sur lequel portent les marques : un cours ou une épreuve, par slug. */
export type CibleEtude = { type: "cours" | "lesson"; slug: string }

// --- Recherche globale (voir recherche.moteur côté backend) ---

export type TypeResultatRecherche = "THEME" | "COURS" | "EPREUVE" | "INEDITE" | "EXERCICE" | "QUIZ"

/** "libre" : sans abonnement · "ouvert" : ce visiteur y a droit · "verrouille" : abonnement requis ·
 * null : sans objet (un thème n'est pas un contenu payant). Un simple indice : c'est la page du
 * contenu qui applique la vraie règle d'accès. */
export type AccesResultat = "libre" | "ouvert" | "verrouille"

export interface ResultatRecherche {
  id: number
  type: TypeResultatRecherche
  titre: string
  /** Extrait du texte public où le mot cherché apparaît, ou ouverture du contenu. Vide pour une
   * question de quiz que le visiteur ne peut pas jouer. */
  apercu: string
  annee: number | null
  matiere: { code: string; label: string }
  cursus: { id: number; label: string }[]
  cursus_total: number
  tous_cursus: boolean
  /** Cursus vers lequel mènent les liens d'un thème ou d'un quiz : celui de l'élève s'il en fait partie. */
  cursus_cible: number | null
  acces: AccesResultat | null
  /** Questions de quiz qui correspondent (un seul résultat par thème). */
  nb: number | null
  details: {
    slug?: string
    id?: number
    ancre?: string
    numero?: string
    libelle?: string
    epreuve?: string
    sous_theme?: string
    type_libelle?: string
    tag_id?: number
    subject_code?: string
    nb_cours?: number
    nb_quiz?: number
    nb_exercices?: number
  }
}

export interface GroupeRecherche {
  type: TypeResultatRecherche
  libelle: string
  total: number
  resultats: ResultatRecherche[]
}

export interface ReponseRecherche {
  q: string
  /** Requête corrigée automatiquement (faute de frappe), quand la saisie ne donnait rien. */
  corrige: string | null
  /** false tant que l'index n'a pas été construit. */
  indexe: boolean
  trop_court: boolean
  total: number
  groupes: GroupeRecherche[]
  /** Résultats cachés par le filtre d'examen (renseigné quand il y en a peu dans l'examen choisi). */
  autres_cursus: number
  /** Matières présentes dans les résultats, la plus fournie d'abord - reste complète quand une matière
   * est choisie, pour pouvoir en changer d'un clic (« tangente » : maths, physique, chimie). */
  matieres: { code: string; label: string; total: number }[]
  /** Thèmes proposés quand rien ne correspond. */
  suggestions: ResultatRecherche[]
  /** Ce que le moteur a compris de la requête (examen, matière, année, type voulu) - null quand elle n'a
   * pas pu être analysée (trop courte). */
  intention: IntentionRecherche | null
  /** La règle du cours qui répond à une question courte (« loi d'ohm ») - null le plus souvent : seulement quand
   * tout est net, jamais sur un onglet ou une page suivante. */
  reponse: CarteReponseRecherche | null
}

/** Un cours (résultat ordinaire) avec sa RÈGLE en Markdown : la section publique de son aperçu. */
export interface CarteReponseRecherche extends ResultatRecherche {
  regle_md: string
}

/** Ce que le moteur a compris d'une requête comme « bac c maths 2019 corrigé » : des filtres, que l'élève
 * peut retirer un à un (paramètre `sans`), et des types de contenu qui passent devant. */
export interface IntentionRecherche {
  cursus: { libelle: string; ids: number[] } | null
  matiere: { libelle: string; codes: string[] } | null
  annees: number[]
  types: TypeResultatRecherche[]
  /** Mots d'intention retirés de la recherche (« corrige », « sujet »...), ramenés au singulier. */
  mots_type: string[]
  /** Vrai quand ces filtres ne donnaient aucun résultat : ils ont été abandonnés, les mots cherchés tels quels. */
  ignoree: boolean
}

/** Ce que l'élève est peut-être en train d'écrire : un intitulé de thème et sa matière. */
export interface CompletionRecherche {
  texte: string
  matiere: string
}
