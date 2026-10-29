import { useState } from "react"
import { Link, useLocation } from "react-router-dom"
import { Tag, X } from "lucide-react"

import { useAbonneActif } from "@/lib/abonneActif"
import { dateLimiteCampagne, nomCampagne, urgenceCampagne, useCampagne } from "@/lib/campagne"
import { useCursusDeclare } from "@/lib/cursusAccueil"
import { t, useI18n } from "@/lib/i18n"

const FERME_KEY = "edukamer_bandeau_campagne_ferme"

// Pages où l'offre est déjà montrée en entier (accueil d'un pays, tarifs, abonnement, accès refusé) ou où un bandeau
// gênerait ce que l'élève fait : lecture, quiz en cours, tentative d'inédite, connexion.
const PAGES_SANS_BANDEAU =
  /^\/[a-z]{2}\/?$|\/lire$|^\/quiz\/session|^\/quiz\/essai|^\/inedit\/tentative|^\/simulation|^\/abonnement|^\/connexion|^\/login|^\/tarifs|^\/qui-etudie/

function lireFerme(): boolean {
  try {
    return sessionStorage.getItem(FERME_KEY) === "1"
  } catch {
    return false
  }
}

/**
 * Rappel d'une ligne de la campagne promotionnelle, sur les pages où le bandeau complet (BandeauCampagne) n'est pas.
 * Un visiteur arrivé par une recherche ou un lien partagé sur un cours ne voyait jamais l'offre. Les montants viennent
 * de la campagne renvoyée par le serveur ; ici on ne calcule rien. Absent pour un abonné actif et pour un élève dont
 * l'examen n'est pas concerné par la campagne. Fermable pour la visite seulement.
 */
export function BandeauCampagneFin() {
  useI18n()
  const { pathname } = useLocation()
  const campagne = useCampagne()
  const abonne = useAbonneActif()
  const cursusDeclare = useCursusDeclare()
  const [ferme, setFerme] = useState(lireFerme)

  if (!campagne || ferme || abonne || PAGES_SANS_BANDEAU.test(pathname)) return null
  if (campagne.cursus.length > 0 && cursusDeclare !== null && !campagne.cursus.includes(cursusDeclare)) return null

  function fermer() {
    try {
      sessionStorage.setItem(FERME_KEY, "1")
    } catch {
      // stockage indisponible : le rappel reviendra à la page suivante, sans gravité
    }
    setFerme(true)
  }

  const urgence = urgenceCampagne(campagne.fin)
  return (
    <div role="status" className="border-b border-gold/40 bg-gold/[0.08]">
      <div className="mx-auto flex max-w-5xl items-center gap-2 px-4 py-1.5 text-xs sm:px-6">
        <Tag className="size-3.5 shrink-0 text-gold-text" aria-hidden="true" />
        <p className="min-w-0 flex-1 truncate">
          <span className="font-semibold text-gold-text">
            {t("camp.fin_titre", { nom: nomCampagne(campagne), pct: campagne.pourcentage })}
          </span>{" "}
          <span className="text-foreground">{urgence ?? t("camp.fin_jusqu_au", { date: dateLimiteCampagne(campagne.fin) })}</span>
        </p>
        <Link to="/tarifs" className="shrink-0 font-medium text-gold-text underline-offset-2 hover:underline">
          {t("camp.fin_voir")}
        </Link>
        <button
          type="button"
          onClick={fermer}
          aria-label={t("moments.fermer")}
          className="shrink-0 rounded-md p-1 text-muted-foreground transition-colors hover:text-foreground"
        >
          <X className="size-3.5" />
        </button>
      </div>
    </div>
  )
}
