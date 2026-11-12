import { useEffect, useState } from "react"

import { aUnEssaiSansCompte, EVENEMENT_INVITE } from "@/lib/invite"

/** Vrai tant que ce navigateur porte un essai sans compte (voir lib/invite.ts) ; suit sa création et sa fin. */
export function useEssaiSansCompte(): boolean {
  const [essai, setEssai] = useState(aUnEssaiSansCompte)
  useEffect(() => {
    const maj = () => setEssai(aUnEssaiSansCompte())
    window.addEventListener(EVENEMENT_INVITE, maj)
    return () => window.removeEventListener(EVENEMENT_INVITE, maj)
  }, [])
  return essai
}
