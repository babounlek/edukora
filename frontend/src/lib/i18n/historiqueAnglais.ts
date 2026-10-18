/**
 * L'historique du routeur de la version anglaise : il traduit l'adresse du navigateur à la frontière, pour
 * que le reste de l'application ne voie jamais l'anglais.
 *
 *   barre d'adresse : /en/cm/past-papers/physics-2023/read
 *   pour le routeur : /cm/epreuves/physics-2023/lire        (routes, <Link to>, useParams, pathname...)
 *
 * Dans l'autre sens, tout ce que le routeur navigue ou affiche (`push`, `replace`, `createHref` : donc l'attribut
 * `href` de chaque `<a>`, ce que lisent les moteurs de recherche) est traduit en anglais et préfixé de `/en`.
 *
 * S'appuie sur `UNSAFE_createBrowserHistory` et `unstable_HistoryRouter` de react-router, les seules pièces
 * publiques permettant ça : un test (historiqueAnglais.test.tsx) échoue à la mise à jour de react-router si
 * l'une d'elles change.
 */
import {
  UNSAFE_createBrowserHistory as creerHistoriqueNavigateur,
  parsePath,
  type Location,
  type To,
} from "react-router-dom"

import { cheminDansLangue, cheminInterneDepuisUrl } from "./prefixe"

type History = ReturnType<typeof creerHistoriqueNavigateur>

/** Une destination interne (chemin français, query et ancre inclus) -> la destination publique anglaise. */
function versUrlPublique(to: To): To {
  const chemin = typeof to === "string" ? parsePath(to) : to
  // Une destination relative ou sans chemin (query ou ancre seules) n'a rien à traduire.
  if (!chemin.pathname || !chemin.pathname.startsWith("/")) return to
  return { ...chemin, pathname: cheminDansLangue(chemin.pathname, "en") }
}

function versInterne(emplacement: Location): Location {
  return { ...emplacement, pathname: cheminInterneDepuisUrl(emplacement.pathname) }
}

/**
 * Une URL anglaise qui porte encore des segments français (`/en/cm/epreuves/x`, ancien lien, saisie à la main) est
 * réécrite sur place en sa forme anglaise : une seule adresse par page. Les moteurs de recherche, eux, reçoivent un
 * 301 de Caddy, et le `canonical` de la page est de toute façon la forme anglaise.
 */
function corrigerUrlCourante(): void {
  const { pathname, search, hash } = window.location
  const canonique = cheminDansLangue(cheminInterneDepuisUrl(pathname), "en")
  if (canonique !== pathname) {
    window.history.replaceState(window.history.state, "", `${canonique}${search}${hash}`)
  }
}

export function creerHistoriqueAnglais(): History {
  corrigerUrlCourante()
  // v5Compat : sans lui, l'historique ne prévient le routeur que des retours arrière, jamais de ses propres push
  const navigateur = creerHistoriqueNavigateur({ v5Compat: true })
  return {
    get action() {
      return navigateur.action
    },
    get location() {
      return versInterne(navigateur.location)
    },
    createHref: (to) => navigateur.createHref(versUrlPublique(to)),
    createURL: (to) => navigateur.createURL(versUrlPublique(to)),
    // Reçoit et rend un chemin interne : seul l'encodage des caractères est celui du navigateur.
    encodeLocation: (to) => navigateur.encodeLocation(to),
    push: (to, state) => navigateur.push(versUrlPublique(to), state),
    replace: (to, state) => navigateur.replace(versUrlPublique(to), state),
    go: (delta) => navigateur.go(delta),
    listen: (ecouteur) =>
      navigateur.listen((mise_a_jour) => ecouteur({ ...mise_a_jour, location: versInterne(mise_a_jour.location) })),
  }
}

