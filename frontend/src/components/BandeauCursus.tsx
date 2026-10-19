import { useState } from "react"
import { useLocation } from "react-router-dom"
import { X } from "lucide-react"
import { toast } from "sonner"
import type { Cursus } from "@/api/types"
import { useCursusListe } from "@/lib/cursusLangue"
import { trierCursus } from "@/lib/cursus"
import { langueDeListe } from "@/lib/discipline"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { memoriserCursusPrepareEnAttente, useCursusPrepareEnAttente } from "@/lib/cursusPrepare"
import { useChangerCursusPrepare } from "@/lib/changerCursusPrepare"
import { InviteAutreSousSysteme } from "@/components/InviteAutreSousSysteme"
import { Button } from "@/components/ui/button"
import { t, useI18n } from "@/lib/i18n"

const FERME_KEY = "edukamer_bandeau_cursus_ferme"

// Pages où un bandeau gênerait ce que l'élève est en train de faire : lecture,
// quiz en cours, paiement, connexion. Ailleurs il reste visible, y compris quand
// l'élève arrive directement sur un cours ou une épreuve depuis un PDF ou une recherche.
const PAGES_SANS_BANDEAU = /\/lire$|^\/quiz\/session|^\/quiz\/essai|^\/inedit\/tentative|^\/simulation|^\/abonnement|^\/login|^\/tarifs/

// L'accueil d'un pays (/cm, /sn...) : même motif que celui de l'onboarding (OnboardingModal).
const ACCUEIL_PAYS_RE = /^\/[a-z]{2}\/?$/i

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
 * fermeture définitive appartient à la touche Échap de l'onboarding,
 * et un élève sans examen déclaré n'a pas de séance - autant lui redemander la
 * prochaine fois. Un visiteur non connecté écrit sa déclaration en attente, reprise
 * à sa première connexion (voir cursusPrepare.ts).
 */
export function BandeauCursus() {
  useI18n()
  const { pathname } = useLocation()
  const { isAuthenticated, user } = useAuth()
  const { country } = useCountry()
  const [ferme, setFerme] = useState(lireFerme)
  const enAttente = useCursusPrepareEnAttente()

  const aDeclare = isAuthenticated ? Boolean(user?.cursus_prepare) : enAttente !== null
  const visible = !ferme && !aDeclare && !PAGES_SANS_BANDEAU.test(pathname) && Boolean(country)

  // Seulement les examens de la langue de l'interface (voir lib/cursusLangue).
  const { data: cursusList, tous: tousLesCursus } = useCursusListe(country, { langue: langueDeListe("", false), enabled: visible })

  const declarer = useChangerCursusPrepare()

  function choisir(cursus: Cursus) {
    if (isAuthenticated) {
      declarer.mutate(cursus.id)
      return
    }
    memoriserCursusPrepareEnAttente(cursus.id)
    // Sans compte, le seul changement visible ailleurs sur la page est discret (la
    // vedette "épreuve inédite" du catalogue, hors champ de vision) - un visiteur qui
    // ne la remarque pas a l'impression que son choix n'a rien fait. Une confirmation
    // immédiate, à l'endroit même du clic, ne dépend d'aucun autre composant.
    toast.success(t("bandeau.note", { cursus: `${cursus.examen_display}${cursus.series ? ` ${cursus.series.code}` : ""}` }), {
      description: t("bandeau.connecte_toi"),
    })
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
    <div role="region" aria-label={t("bandeau.aria")} className="border-b border-primary/20 bg-primary/5">
      <div className="mx-auto flex max-w-5xl items-start gap-3 px-4 py-2.5 sm:px-6">
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium">{t("bandeau.titre")}</p>
          <div className="-mx-1 mt-2 flex gap-1.5 overflow-x-auto px-1 pb-1 [scrollbar-width:none] sm:flex-wrap sm:overflow-visible sm:pb-0 [&::-webkit-scrollbar]:hidden">
            {trierCursus(cursusList).map((cursus) => (
              <Button
                key={cursus.id}
                variant="outline"
                size="sm"
                className="h-8 shrink-0 rounded-full px-3.5 text-sm"
                disabled={declarer.isPending}
                onClick={() => choisir(cursus)}
              >
                {cursus.examen_display}
                {cursus.series ? ` ${cursus.series.code}` : ""}
              </Button>
            ))}
          </div>
          {/* Pas sur l'accueil d'un pays : le hero y porte déjà la même invitation, et la montrer deux fois
              sur le même écran serait du bruit. */}
          <InviteAutreSousSysteme
            disponible={!ACCUEIL_PAYS_RE.test(pathname) && tousLesCursus.some((c) => c.langue && c.langue !== langueDeListe("", false))}
            className="mt-1.5"
          />
        </div>
        <button
          type="button"
          onClick={fermer}
          aria-label={t("moments.fermer")}
          className="rounded-md p-1 text-muted-foreground transition-colors hover:text-foreground"
        >
          <X className="size-4" />
        </button>
      </div>
    </div>
  )
}
