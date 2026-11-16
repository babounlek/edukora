/**
 * « Ce navigateur a déjà affiché l'accueil d'un élève abonné » : un simple indice, pour ne pas montrer la vitrine du
 * visiteur à un abonné pendant que sa session se retrouve (un aller-retour au démarrage). Lu par le script de
 * index.html (coquille de l'accueil) et par CataloguePage. Ce n'est ni une preuve de session ni un droit : si l'indice
 * est faux (déconnexion, abonnement échu), la vitrine s'affiche dès que la session est connue, et l'indice est retiré.
 *
 * La clé est aussi écrite en dur dans index.html : les deux se changent ensemble.
 */
export const CLE_ACCUEIL_ELEVE = "edukora:accueil-eleve"

export function marquerAccueilEleve() {
  try {
    localStorage.setItem(CLE_ACCUEIL_ELEVE, "1")
  } catch {
    // Stockage indisponible : l'abonné verra la vitrine un instant, comme avant.
  }
}

export function oublierAccueilEleve() {
  try {
    localStorage.removeItem(CLE_ACCUEIL_ELEVE)
  } catch {
    // rien à faire
  }
}

export function accueilEleveProbable(): boolean {
  try {
    return localStorage.getItem(CLE_ACCUEIL_ELEVE) !== null
  } catch {
    return false
  }
}
