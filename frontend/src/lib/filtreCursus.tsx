import { useEffect } from "react"
import { useSearchParams } from "react-router-dom"

import { useAuth } from "@/context/AuthContext"

/**
 * Pré-filtre les listes du catalogue sur l'examen que l'élève a déclaré.
 *
 * On lui demande ce qu'il prépare, on lui sert une séance faite pour lui - puis il
 * ouvrait "Réviser" et retombait sur 828 épreuves dont les trois quarts ne le
 * concernent pas, à re-filtrer à la main à chaque visite.
 *
 * Un DÉFAUT, jamais une frontière : le filtre est annoncé et se retire d'un clic
 * (voir BandeauFiltreCursus). Trois usages réels cassent sous un masquage dur - un
 * élève de Terminale révise aussi le programme de Première, un répétiteur enseigne
 * plusieurs séries (voir subscriptions.InscriptionRepetiteur), un redoublant change de
 * filière. Et les robots d'indexation n'ayant jamais de session, le catalogue reste
 * entier pour eux.
 *
 * `tout=1` dans l'URL mémorise le choix d'élargir : sans ce marqueur, le filtre se
 * réappliquerait à la navigation suivante et le bouton "Voir tout" semblerait cassé.
 */
export const PARAM_VOIR_TOUT = "tout"

/**
 * Lecture seule : quel est l'état du pré-filtrage, sans jamais l'appliquer.
 *
 * Séparé de useFiltreCursusParDefaut à cause de l'ordre des effets de React, qui
 * remontent des enfants vers le parent : si le bandeau appliquait lui-même le filtre,
 * son effet s'exécuterait AVANT celui de la page qui l'affiche - et sur /epreuves,
 * cela écrirait un `cursus` dans l'URL juste avant la restauration de la dernière
 * recherche en session, qui se croirait alors devant une URL déjà filtrée et
 * renoncerait. La page applique, le bandeau se contente de raconter.
 */
function useEtatFiltreCursus() {
  const { isAuthenticated, user } = useAuth()
  const [searchParams, setSearchParams] = useSearchParams()

  const cursusPrepare = isAuthenticated ? user?.cursus_prepare ?? null : null
  const cursusDansUrl = searchParams.get("cursus") ?? ""
  const voirTout = searchParams.get(PARAM_VOIR_TOUT) === "1"

  return {
    cursusPrepare,
    cursusDansUrl,
    voirTout,
    searchParams,
    setSearchParams,
    applique: Boolean(cursusPrepare) && cursusDansUrl === String(cursusPrepare?.id),
  }
}

export function useFiltreCursusParDefaut() {
  const etat = useEtatFiltreCursus()
  const { cursusPrepare, cursusDansUrl, voirTout, searchParams, setSearchParams } = etat

  useEffect(() => {
    if (!cursusPrepare || cursusDansUrl || voirTout) return
    const suivant = new URLSearchParams(searchParams)
    suivant.set("cursus", String(cursusPrepare.id))
    // `replace` : le pré-filtrage n'est pas une navigation que l'élève a demandée,
    // il ne doit pas s'intercaler dans son historique ni piéger le bouton "retour".
    setSearchParams(suivant, { replace: true })
  }, [cursusPrepare, cursusDansUrl, voirTout, searchParams, setSearchParams])

  return etat
}

/** Dit à l'élève que la liste est réduite à son examen, et comment en sortir. Sans
 * cette phrase, un catalogue soudain trois fois plus court se lit comme un contenu
 * manquant plutôt que comme une aide. */
export function BandeauFiltreCursus() {
  const { applique, cursusPrepare, searchParams, setSearchParams } = useEtatFiltreCursus()
  if (!applique || !cursusPrepare) return null

  const libelle = `${cursusPrepare.examen_display}${cursusPrepare.series ? ` ${cursusPrepare.series.code}` : ""}`
  const montrerTout = () => {
    const suivant = new URLSearchParams(searchParams)
    suivant.delete("cursus")
    suivant.set(PARAM_VOIR_TOUT, "1")
    setSearchParams(suivant)
  }
  return (
    <p className="mb-4 flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-muted-foreground">
      <span>
        Filtré sur ton <span className="font-medium text-foreground">{libelle}</span>.
      </span>
      <button
        type="button"
        onClick={montrerTout}
        className="underline underline-offset-4 transition-colors hover:text-primary"
      >
        Voir tout le catalogue
      </button>
    </p>
  )
}
