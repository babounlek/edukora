import { useEffect } from "react"
import { useSearchParams } from "react-router-dom"

import { useAuth } from "@/context/AuthContext"
import { estDeLangue } from "@/lib/cursusLangue"
import { langueCourante, t, useI18n } from "@/lib/i18n"

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
 * Retire le cursus de l'URL ET pose `tout=1`, dans une même opération.
 *
 * Retirer `cursus` seul ne suffit pas : useFiltreCursusParDefaut le remet aussitôt tant
 * que `tout=1` est absent, si bien que la puce, « Tous » ou « Tout effacer » semblaient
 * sans effet. À appeler sur tout retrait EXPLICITE du cursus par l'élève (jamais pour un
 * changement de pays, où le défaut doit au contraire se réappliquer). Mute `params` et le
 * renvoie, pour s'enchaîner dans un callback de setSearchParams.
 */
export function desactiverFiltreCursus(params: URLSearchParams): URLSearchParams {
  params.delete("cursus")
  params.set(PARAM_VOIR_TOUT, "1")
  return params
}

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
    // Un examen déclaré dans l'autre langue ne pré-filtre pas : l'élève qui lit l'interface en anglais verrait
    // d'office une liste française. Il reste proposé parmi les pastilles (voir lib/cursusLangue).
    if (!estDeLangue(cursusPrepare, langueCourante())) return
    const suivant = new URLSearchParams(searchParams)
    suivant.set("cursus", String(cursusPrepare.id))
    // `replace` : le pré-filtrage n'est pas une navigation que l'élève a demandée,
    // il ne doit pas s'intercaler dans son historique ni piéger le bouton "retour".
    setSearchParams(suivant, { replace: true })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cursusPrepare, cursusDansUrl, voirTout, searchParams, setSearchParams, langueCourante()])

  return etat
}

/** Dit à l'élève que la liste est réduite à son examen, et comment en sortir. Sans
 * cette phrase, un catalogue soudain trois fois plus court se lit comme un contenu
 * manquant plutôt que comme une aide. */
export function BandeauFiltreCursus() {
  useI18n()
  const { applique, cursusPrepare, searchParams, setSearchParams } = useEtatFiltreCursus()
  if (!applique || !cursusPrepare) return null

  const libelle = `${cursusPrepare.examen_display}${cursusPrepare.series ? ` ${cursusPrepare.series.code}` : ""}`
  const montrerTout = () => {
    setSearchParams(desactiverFiltreCursus(new URLSearchParams(searchParams)))
  }
  return (
    <p className="mb-4 flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-muted-foreground">
      <span>
        {t("ep.filtre_cursus_avant")} <span className="font-medium text-foreground">{libelle}</span>.
      </span>
      <button
        type="button"
        onClick={montrerTout}
        className="underline underline-offset-4 transition-colors hover:text-primary"
      >
        {t("ep.voir_catalogue")}
      </button>
    </p>
  )
}
