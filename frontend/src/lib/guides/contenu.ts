import type { DefinitionGuide, EtapeGuide } from "./types"

/**
 * Le contenu de tous les guides, au même endroit. Les textes eux-mêmes sont des clés
 * i18n (`guide.*` dans lib/i18n/fr.ts et en.ts) : le français et l'anglais passent par
 * le même mécanisme que le reste du site.
 *
 * Ajouter un guide = ajouter une entrée ici, des clés de texte, et - pour une aide
 * contextuelle - un `<AideContextuelle guide="..." />` dans la page. Aucune logique à écrire.
 *
 * Modifier un guide :
 *   - une correction de formulation : changer le texte, rien d'autre ;
 *   - un changement qui justifie de le montrer de nouveau à ceux qui l'ont déjà vu :
 *     augmenter `version`.
 */

// Même motif que l'accueil catalogue d'un pays (/cm, /sn...) - voir OnboardingModal.
const ACCUEIL = /^\/[a-z]{2}\/?$/i

export function estAccueilCatalogue(pathname: string): boolean {
  return ACCUEIL.test(pathname)
}

/** La première étape de bienvenue est la même pour l'élève et le visiteur : un seul texte. */
const ETAPE_INTERET: EtapeGuide = {
  id: "interet",
  titre: "guide.bienvenue.interet.titre",
  texte: "guide.bienvenue.interet.texte",
}

// Pages de contenu (chemins internes du routeur) : un cours ouvert en lecture, un exercice d'un
// thème, la page de CHOIX du quiz (jamais une session en cours, voir moteur.ts).
const COURS_LECTURE = /^\/cours\/[^/]+\/lire\/?$/
const EXERCICE_THEME = /^\/[a-z]{2}\/themes-frequents\/[^/]+\/exercices\/[^/]+\/?$/i
const QUIZ_DEPART = /^\/quiz\/?$/
const ACCES = /^\/mes-acces\/?$/
const ANNALES = /^\/[a-z]{2}\/epreuves\/?$/i
const INEDITE = /^\/[a-z]{2}\/epreuves-inedites\/[^/]+\/?$/i
const PROGRESSION = /^\/parcours\/?$/

export const GUIDES: readonly DefinitionGuide[] = [
  {
    id: "bienvenue",
    version: 1,
    type: "parcours",
    titre: "guide.bienvenue.titre",
    description: "guide.bienvenue.description",
    declencheur: "premiere-visite",
    public: "eleve",
    cheminRelance: "accueil",
    route: estAccueilCatalogue,
    // Le tutoriel parle de la séance du jour : sans le bouton de séance à l'écran (élève sans
    // abonnement, séance du jour absente), il décrirait quelque chose qu'on ne voit pas.
    condition: (contexte) => contexte.ciblePresente("seance-commencer"),
    etapes: [
      ETAPE_INTERET,
      {
        id: "seance",
        titre: "guide.bienvenue.seance.titre",
        texte: "guide.bienvenue.seance.texte",
        cible: "seance-commencer",
        cibleObligatoire: true,
      },
      {
        id: "etapes",
        titre: "guide.bienvenue.etapes.titre",
        texte: "guide.bienvenue.etapes.texte",
        cible: "seance-parcours",
        cibleObligatoire: true,
      },
    ],
  },
  {
    // Un autre identifiant que le tutoriel de l'élève : ce qu'il a vu en visiteur n'est pas ce
    // qu'il verra une fois connecté, et la séance du jour n'existe pas pour un visiteur.
    id: "bienvenue-visiteur",
    version: 1,
    type: "parcours",
    titre: "guide.visiteur.titre",
    description: "guide.visiteur.description",
    declencheur: "premiere-visite",
    public: "visiteur",
    cheminRelance: "accueil",
    route: estAccueilCatalogue,
    etapes: [
      ETAPE_INTERET,
      {
        id: "compte",
        titre: "guide.visiteur.compte.titre",
        texte: "guide.visiteur.compte.texte",
        action: { label: "guide.visiteur.compte.action", to: "/connexion" },
      },
    ],
  },
  {
    id: "seance-du-jour",
    version: 1,
    type: "aide",
    titre: "guide.seance.titre",
    description: "guide.seance.description",
    declencheur: "premiere-fonctionnalite",
    public: "eleve",
    cheminRelance: "accueil",
    route: estAccueilCatalogue,
    etapes: [
      {
        id: "fonctionnement",
        titre: "guide.seance.titre",
        texte: "guide.seance.texte",
        cible: "seance-commencer",
      },
    ],
  },
  {
    id: "cours",
    version: 1,
    type: "aide",
    titre: "guide.cours.titre",
    description: "guide.cours.description",
    declencheur: "premiere-fonctionnalite",
    public: "eleve",
    route: (pathname) => COURS_LECTURE.test(pathname),
    etapes: [{ id: "lecture", titre: "guide.cours.titre", texte: "guide.cours.texte" }],
  },
  {
    id: "exercice",
    version: 1,
    type: "aide",
    titre: "guide.exercice.titre",
    description: "guide.exercice.description",
    declencheur: "premiere-fonctionnalite",
    public: "eleve",
    route: (pathname) => EXERCICE_THEME.test(pathname),
    etapes: [{ id: "travail", titre: "guide.exercice.titre", texte: "guide.exercice.texte" }],
  },
  {
    id: "quiz-depart",
    version: 1,
    type: "aide",
    titre: "guide.quiz.titre",
    description: "guide.quiz.description",
    declencheur: "premiere-fonctionnalite",
    public: "eleve",
    cheminRelance: "/quiz",
    route: (pathname) => QUIZ_DEPART.test(pathname),
    // La carte de réglage n'existe que pour un abonné : sans elle, l'aide décrirait des choix absents.
    condition: (contexte) => contexte.ciblePresente("quiz-config"),
    etapes: [{ id: "lancer", titre: "guide.quiz.titre", texte: "guide.quiz.texte" }],
  },
  {
    id: "examen-matieres",
    version: 1,
    type: "aide",
    titre: "guide.acces.titre",
    description: "guide.acces.description",
    declencheur: "premiere-fonctionnalite",
    public: "eleve",
    cheminRelance: "/mes-acces",
    route: (pathname) => ACCES.test(pathname),
    etapes: [{ id: "examen", titre: "guide.acces.titre", texte: "guide.acces.texte" }],
  },
  {
    id: "annales",
    version: 1,
    type: "aide",
    titre: "guide.annales.titre",
    description: "guide.annales.description",
    declencheur: "premiere-fonctionnalite",
    public: "eleve",
    route: (pathname) => ANNALES.test(pathname),
    etapes: [{ id: "trouver", titre: "guide.annales.titre", texte: "guide.annales.texte" }],
  },
  {
    id: "inedites",
    version: 1,
    type: "aide",
    titre: "guide.inedites.titre",
    description: "guide.inedites.description",
    declencheur: "premiere-fonctionnalite",
    public: "eleve",
    // Liée à une épreuve précise : se relit depuis sa fiche.
    route: (pathname) => INEDITE.test(pathname),
    etapes: [{ id: "inedite", titre: "guide.inedites.titre", texte: "guide.inedites.texte" }],
  },
  {
    id: "progression",
    version: 1,
    type: "aide",
    titre: "guide.progression.titre",
    description: "guide.progression.description",
    declencheur: "premiere-fonctionnalite",
    public: "eleve",
    cheminRelance: "/parcours",
    route: (pathname) => PROGRESSION.test(pathname),
    etapes: [{ id: "lire", titre: "guide.progression.titre", texte: "guide.progression.texte" }],
  },
]

export function trouverGuide(id: string): DefinitionGuide | undefined {
  return GUIDES.find((guide) => guide.id === id)
}

/**
 * Le guide de bienvenue qui correspond à qui regarde : le centre d'aide propose « revoir la
 * bienvenue » sans que l'élève ait à savoir qu'il en existe deux.
 */
export function guideDeBienvenue(connecte: boolean): DefinitionGuide {
  return trouverGuide(connecte ? "bienvenue" : "bienvenue-visiteur")!
}
