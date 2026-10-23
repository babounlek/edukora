import { useCallback } from "react"
import { useLocation } from "react-router-dom"

import { useAuth } from "@/context/AuthContext"
import { useCursusPrepareEnAttente } from "@/lib/cursusPrepare"
import { useModeExamen } from "@/lib/modeExamen"
import { ciblePresente, dialogueOuvert } from "./cibles"
import { useEtatGuides } from "./etat"
import type { ContexteGuide, PublicGuide } from "./types"

/**
 * Qui regarde, pour les guides :
 *  - un « élève » : connecté, avec un examen déclaré ;
 *  - un « visiteur » : pas connecté, mais qui a déjà dit quel examen il prépare (l'écran de
 *    première visite, voir OnboardingModal) ;
 *  - personne (null) sinon, ou tant que la session n'est pas lue : un compte sans examen
 *    déclaré est d'abord invité à le dire (BandeauCursus), pas à lire un tutoriel.
 */
export function usePublicGuide(): PublicGuide | null {
  const { isAuthenticated, isLoading, user } = useAuth()
  const cursusEnAttente = useCursusPrepareEnAttente()
  if (isLoading) return null
  if (isAuthenticated) return user?.cursus_prepare ? "eleve" : null
  return cursusEnAttente !== null ? "visiteur" : null
}

/**
 * Le contexte que le moteur lit pour décider d'un affichage automatique. Les valeurs qui
 * viennent de React sont lues ici (donc le composant se re-rend quand elles changent) ;
 * celles qui viennent du DOM (cibles, fenêtres ouvertes) ne sont lues qu'à l'appel de la
 * fonction retournée, à l'intérieur d'un effet, quand la page est réellement peinte.
 */
export function useContexteGuide(): () => ContexteGuide {
  const { pathname } = useLocation()
  const enExamen = useModeExamen()
  const { onboardingOuvert } = useEtatGuides()
  const publicGuide = usePublicGuide()
  return useCallback(
    () => ({
      pathname,
      public: publicGuide,
      onboardingOuvert,
      enExamen,
      dialogueOuvert: dialogueOuvert(),
      ciblePresente,
    }),
    [pathname, publicGuide, onboardingOuvert, enExamen],
  )
}
