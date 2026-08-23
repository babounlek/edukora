import { Link } from "react-router-dom"
import { Gift } from "lucide-react"

import { useAuth } from "@/context/AuthContext"

/**
 * Rappel compact du parrainage, à poser sur un mur payant (corrigé/épreuve inédite
 * verrouillés) - alternative moins chère qu'un abonnement pour qui a un ami motivé.
 * Rien à afficher côté anonyme (pas encore de referral_code, voir AccountPage.tsx) :
 * le lien mène vers la page compte, qui porte le mécanisme complet (copier/WhatsApp).
 */
export function ParrainageHint() {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) return null

  return (
    <Link
      to="/compte"
      className="flex w-fit items-center gap-1.5 text-xs text-muted-foreground hover:text-primary hover:underline"
    >
      <Gift className="size-3.5 shrink-0" />
      Ou invite un ami pour gagner 500 FCFA de crédit
    </Link>
  )
}
