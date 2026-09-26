import { useState } from "react"
import { Link, useLocation } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { X } from "lucide-react"

import { getPaiementAReprendre } from "@/api/endpoints"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/context/AuthContext"
import { formatAmount } from "@/lib/utils"

const FERME_KEY = "edukamer_bandeau_paiement_ferme"

// Pages où le bandeau gênerait ou ferait doublon : le paiement lui-même, la lecture, le
// quiz et l'épreuve en cours.
const PAGES_SANS_BANDEAU = /\/lire$|^\/quiz\/session|^\/inedit\/tentative|^\/abonnement|^\/tarifs|^\/mes-paiements|^\/connexion/

function lireFerme(): boolean {
  try {
    return sessionStorage.getItem(FERME_KEY) === "1"
  } catch {
    return false
  }
}

/**
 * « Ton paiement n'a pas abouti » - pour l'élève qui a essayé de payer et n'a rien reçu. Même
 * règle que la relance par e-mail (relances.services.paiement_a_reprendre) : ce bandeau et le
 * message ne peuvent pas se contredire, et lui seul touche ceux qui n'ont pas d'e-mail confirmé.
 *
 * Neutre et fermable pour la visite : ce n'est pas une alerte, c'est un raccourci vers ce que
 * la personne voulait faire.
 */
export function BandeauReprisePaiement() {
  const { pathname } = useLocation()
  const { isAuthenticated } = useAuth()
  const [ferme, setFerme] = useState(lireFerme)

  const { data } = useQuery({
    queryKey: ["paiement-a-reprendre"],
    queryFn: ({ signal }) => getPaiementAReprendre(signal),
    enabled: isAuthenticated,
    // Un élève qui vient de payer ailleurs ne doit pas revoir ce bandeau : revérifié au retour.
    staleTime: 60_000,
    retry: false,
  })

  if (!isAuthenticated || ferme || !data?.a_reprendre || PAGES_SANS_BANDEAU.test(pathname)) return null

  function fermer() {
    try {
      sessionStorage.setItem(FERME_KEY, "1")
    } catch {
      // stockage indisponible : il reste simplement visible à la prochaine page
    }
    setFerme(true)
  }

  return (
    <div role="region" aria-label="Paiement à reprendre" className="border-b border-border bg-accent/60">
      <div className="mx-auto flex max-w-5xl items-center gap-3 px-4 py-2 sm:px-6">
        <p className="min-w-0 flex-1 text-sm">
          Ton paiement de {formatAmount(data.montant ?? 0)} FCFA {data.statut === "FAILED" ? "n'a pas abouti" : "n'a pas été confirmé"}.
        </p>
        <Button asChild size="sm" className="shrink-0">
          <Link to={`/abonnement?cursus=${data.cursus_id}`}>Reprendre</Link>
        </Button>
        <button
          type="button"
          onClick={fermer}
          aria-label="Masquer ce message"
          className="shrink-0 rounded-md p-1.5 text-muted-foreground hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none"
        >
          <X className="size-4" />
        </button>
      </div>
    </div>
  )
}
