import { useState } from "react"
import { useLocation } from "react-router-dom"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { X } from "lucide-react"
import { listCursus, updateMe } from "@/api/endpoints"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { lireCursusPrepareEnAttente, memoriserCursusPrepareEnAttente } from "@/lib/cursusPrepare"
import { Button } from "@/components/ui/button"

const FERME_KEY = "edukamer_bandeau_cursus_ferme"

// Pages où un bandeau gênerait ce que l'élève est en train de faire : lecture,
// quiz en cours, paiement, connexion. Ailleurs il reste visible, y compris quand
// l'élève arrive directement sur un cours ou une épreuve depuis un PDF ou une recherche.
const PAGES_SANS_BANDEAU = /\/lire$|^\/quiz\/session|^\/inedit\/tentative|^\/abonnement|^\/login|^\/tarifs/

function lireFerme(): boolean {
  try {
    return sessionStorage.getItem(FERME_KEY) === "1"
  } catch {
    return false
  }
}

/**
 * "Choisis ton examen pour recevoir ta séance du jour" - la seule façon de déclarer ce
 * qu'on prépare hors de l'onboarding, visible sur toutes les pages tant que la
 * déclaration manque. Il remplace les invites qui existaient page par page (accueil,
 * séance du jour) : une seule question, un seul endroit.
 *
 * Fermable pour la visite seulement (sessionStorage), jamais pour toujours : la
 * fermeture définitive appartient au "Je préfère parcourir librement" de l'onboarding,
 * et un élève sans examen déclaré n'a pas de séance - autant lui redemander la
 * prochaine fois. Un visiteur non connecté écrit sa déclaration en attente, reprise
 * à sa première connexion (voir cursusPrepare.ts).
 */
export function BandeauCursus() {
  const { pathname } = useLocation()
  const { isAuthenticated, user, updateUser } = useAuth()
  const { country } = useCountry()
  const queryClient = useQueryClient()
  const [ferme, setFerme] = useState(lireFerme)
  const [declareEnAttente, setDeclareEnAttente] = useState(() => lireCursusPrepareEnAttente() !== null)

  const aDeclare = isAuthenticated ? Boolean(user?.cursus_prepare) : declareEnAttente
  const visible = !ferme && !aDeclare && !PAGES_SANS_BANDEAU.test(pathname) && Boolean(country)

  const { data: cursusList = [] } = useQuery({
    queryKey: ["cursus", country],
    queryFn: ({ signal }) => listCursus(country, signal),
    enabled: visible,
  })

  const declarer = useMutation({
    mutationFn: (cursusId: number) => updateMe({ cursus_prepare: cursusId }),
    onSuccess: (utilisateur) => {
      updateUser(utilisateur)
      // La séance ne se construit qu'une fois le cursus connu.
      queryClient.invalidateQueries({ queryKey: ["plan-du-jour"] })
    },
  })

  function choisir(cursusId: number) {
    if (isAuthenticated) {
      declarer.mutate(cursusId)
      return
    }
    memoriserCursusPrepareEnAttente(cursusId)
    setDeclareEnAttente(true)
  }

  function fermer() {
    try {
      sessionStorage.setItem(FERME_KEY, "1")
    } catch {
      // stockage indisponible : le bandeau reviendra à la page suivante, sans gravité
    }
    setFerme(true)
  }

  if (!visible || cursusList.length === 0) return null

  return (
    <div role="region" aria-label="Choisir ton examen" className="border-b border-primary/20 bg-primary/5">
      <div className="mx-auto flex max-w-5xl items-start gap-3 px-4 py-2.5 sm:px-6">
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium">Choisis ton examen pour recevoir ta séance du jour</p>
          <div className="-mx-1 mt-2 flex gap-1.5 overflow-x-auto px-1 pb-1 [scrollbar-width:none] sm:flex-wrap sm:overflow-visible sm:pb-0 [&::-webkit-scrollbar]:hidden">
            {cursusList.map((cursus) => (
              <Button
                key={cursus.id}
                variant="outline"
                size="sm"
                className="h-8 shrink-0 rounded-full px-3.5 text-sm"
                disabled={declarer.isPending}
                onClick={() => choisir(cursus.id)}
              >
                {cursus.examen_display}
                {cursus.series ? ` ${cursus.series.code}` : ""}
              </Button>
            ))}
          </div>
        </div>
        <button
          type="button"
          onClick={fermer}
          aria-label="Fermer"
          className="rounded-md p-1 text-muted-foreground transition-colors hover:text-foreground"
        >
          <X className="size-4" />
        </button>
      </div>
    </div>
  )
}
