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

export const GUIDES: readonly DefinitionGuide[] = [
  {
    id: "bienvenue",
    version: 1,
    type: "parcours",
    titre: "guide.bienvenue.titre",
    description: "guide.bienvenue.description",
    declencheur: "premiere-visite",
    public: "eleve",
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
