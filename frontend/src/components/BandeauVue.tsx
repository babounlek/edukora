import { Link } from "react-router-dom"

import { useAuth } from "@/context/AuthContext"
import { useAffichageMatieres, useMatieres } from "@/components/ChoixMatieres"
import { desactiverFiltreCursus, retablirFiltreCursus, useEtatFiltreCursus } from "@/lib/filtreCursus"
import { useI18n } from "@/lib/i18n"

const LIEN = "underline underline-offset-4 transition-colors hover:text-primary"

/**
 * Dit en une phrase ce que l'élève regarde (« Tu vois : GCE O Level · 6 matières ») et comment en sortir, sur les listes
 * dont l'examen est un paramètre d'URL (épreuves, cours). Remplace deux bandeaux voisins - le filtre par examen et
 * « voir seulement mes matières » - qui racontaient chacun la moitié de la même réduction.
 *
 * Deux réglages distincts, deux sorties : l'examen (un DÉFAUT, jamais une frontière - voir useFiltreCursusParDefaut ;
 * visiteurs, liens partagés et révisions d'un autre niveau gardent tout le catalogue) et les matières (préférence du
 * profil, voir quiz.matieres). Pour un abonné, la sortie d'examen se fait discrète (« Voir un autre examen ») : son
 * parcours est son examen. Un visiteur ou un compte sans abonnement garde « Voir tout le catalogue », qui sert à
 * choisir. Une fois élargi, le bandeau reste pour revenir à son examen.
 */
export function BandeauVue() {
  const { t, tn } = useI18n()
  const { user } = useAuth()
  const { applique, cursusPrepare, voirTout, searchParams, setSearchParams } = useEtatFiltreCursus()
  const { actif, cursusId, data } = useMatieres()
  const affichage = useAffichageMatieres(cursusId)

  if (!cursusPrepare) return null

  if (!applique) {
    // Pas élargi, pas filtré non plus (examen d'une autre langue, chargement) : rien à raconter.
    if (!voirTout) return null
    return (
      <p className="mb-4 flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-muted-foreground">
        <span>{t("vue.tous_examens")}</span>
        <button
          type="button"
          onClick={() => setSearchParams(retablirFiltreCursus(new URLSearchParams(searchParams)))}
          className={LIEN}
        >
          {t("vue.revenir")}
        </button>
      </p>
    )
  }

  const libelle = `${cursusPrepare.examen_display}${cursusPrepare.series ? ` ${cursusPrepare.series.code}` : ""}`
  const aDesMatieres = actif && Boolean(data) && (data?.choisies.length ?? 0) > 0
  const seulement = data?.seulement_mes_matieres ?? true
  // Interrupteur actif mais sans effet (choix sans contenu sur cet examen) : on n'en parle pas.
  const matieresMontrees = aDesMatieres && (!seulement || Boolean(data?.affichage_restreint))
  const abonne = Boolean(user?.a_un_abonnement_actif)

  return (
    <p className="mb-4 flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-muted-foreground">
      <span>
        {t("vue.tu_vois")} <span className="font-medium text-foreground">{libelle}</span>
        {matieresMontrees && (
          <> · {seulement ? tn("vue.matieres", data?.nb_affichees ?? 0) : t("vue.matieres_toutes")}</>
        )}
        .
      </span>
      {matieresMontrees && (
        <button type="button" disabled={affichage.isPending} onClick={() => affichage.mutate(!seulement)} className={LIEN}>
          {seulement ? t("matieres.bandeau_voir_toutes") : t("matieres.bandeau_voir_miennes")}
        </button>
      )}
      {matieresMontrees && (
        <Link to="/mes-acces" className={LIEN}>
          {t("matieres.bandeau_modifier")}
        </Link>
      )}
      <button
        type="button"
        onClick={() => setSearchParams(desactiverFiltreCursus(new URLSearchParams(searchParams)))}
        className={abonne ? `${LIEN} text-xs opacity-80` : LIEN}
      >
        {abonne ? t("vue.autre_examen") : t("ep.voir_catalogue")}
      </button>
    </p>
  )
}
