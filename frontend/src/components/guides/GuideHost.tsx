import { lazy, Suspense, useEffect, useState } from "react"
import { useLocation } from "react-router-dom"

import { useAuth } from "@/context/AuthContext"
import { useChangementsDePage } from "@/lib/guides/cibles"
import { estAccueilCatalogue, trouverGuide } from "@/lib/guides/contenu"
import {
  definirIdentite, fermerGuide, lireEtat, memoireActuelle, ouvrirGuide, useEtatGuides,
} from "@/lib/guides/etat"
import { guideAutomatique } from "@/lib/guides/moteur"
import { useContexteGuide, usePublicGuide } from "@/lib/guides/useContexte"

// Chargés à la demande : le tutoriel et le centre d'aide ne pèsent sur le chargement de AUCUNE page tant
// que personne ne les ouvre. Seuls le moteur (quelques kilo-octets) et ce chef d'orchestre sont toujours là.
const GuideRunner = lazy(() => import("@/components/guides/GuideRunner").then((m) => ({ default: m.GuideRunner })))
const CentreAide = lazy(() => import("@/components/guides/CentreAide").then((m) => ({ default: m.CentreAide })))

/**
 * Le chef d'orchestre des guides, monté UNE fois dans App :
 *  1. dit au magasin QUI regarde (compte et profil actif, ou visiteur), pour que la mémoire
 *     de chacun reste la sienne ;
 *  2. lance le tutoriel de bienvenue quand le moteur l'autorise (lib/guides/moteur.ts) ;
 *  3. ferme un guide quand l'élève quitte la page où il avait un sens ;
 *  4. affiche le tutoriel en cours et le centre d'aide.
 *
 * Les aides de page (AideContextuelle) se lancent d'elles-mêmes depuis leur page ; les deux
 * obéissent aux mêmes règles et à la même limite d'« une aide automatique par visite ».
 */
export function GuideHost() {
  const { isAuthenticated, isLoading, user } = useAuth()
  const { pathname } = useLocation()
  const etat = useEtatGuides()
  const contexte = useContexteGuide()
  const publicGuide = usePublicGuide()

  // 1. Qui regarde. Tant que la session n'est pas lue, personne : rien ne se montre ni ne s'écrit.
  const idCompte = user?.id
  const idProfil = user?.profil_actif?.id ?? 0
  useEffect(() => {
    if (isLoading) return
    definirIdentite(isAuthenticated && idCompte !== undefined ? `${idCompte}:${idProfil}` : "anonyme")
  }, [isLoading, isAuthenticated, idCompte, idProfil])

  // 2. Le tutoriel de bienvenue. Il attend ce dont il parle : pour un élève, que le bouton de la
  // séance du jour soit arrivé à l'écran (l'accueil se charge après le premier rendu), d'où
  // l'observation de la page - uniquement tant qu'il y a quelque chose à attendre.
  const { identite, ouvert, autoDejaMontre, revision } = etat
  const enAttente =
    identite !== null && ouvert === null && !autoDejaMontre && publicGuide === "eleve" && estAccueilCatalogue(pathname)
  const changementsDePage = useChangementsDePage(enAttente)
  useEffect(() => {
    if (!identite) return
    const guide = guideAutomatique(contexte(), {
      memoire: memoireActuelle(),
      guideOuvert: ouvert !== null,
      autoDejaMontre,
    })
    if (guide) ouvrirGuide(guide.id, { explicite: false })
  }, [identite, ouvert, autoDejaMontre, revision, contexte, changementsDePage])

  // 3. Quitter la page d'un guide le ferme. Pour un guide qui s'était montré tout seul, c'est
  // une façon de dire « pas maintenant » : on ne le lui remontre pas à chaque navigation.
  useEffect(() => {
    // Relu au moment de l'effet : l'état a pu changer entre le rendu et la navigation.
    const courant = lireEtat().ouvert
    if (!courant) return
    const guide = trouverGuide(courant.id)
    if (guide && !guide.route(pathname)) fermerGuide(courant.explicite ? undefined : "ignore")
  }, [pathname])

  // Le centre reste monté après sa première ouverture : son panneau joue ainsi son animation de fermeture.
  const [centreDejaOuvert, setCentreDejaOuvert] = useState(false)
  useEffect(() => {
    if (etat.centreOuvert) setCentreDejaOuvert(true)
  }, [etat.centreOuvert])

  const guideOuvert = etat.ouvert ? trouverGuide(etat.ouvert.id) : undefined
  return (
    <Suspense fallback={null}>
      {etat.ouvert && guideOuvert?.type === "parcours" && <GuideRunner guide={guideOuvert} ouvert={etat.ouvert} />}
      {(etat.centreOuvert || centreDejaOuvert) && <CentreAide />}
    </Suspense>
  )
}
