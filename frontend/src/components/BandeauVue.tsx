import { Link } from "react-router-dom"

import { useMatieres } from "@/components/ChoixMatieres"
import { useAbonneActif } from "@/lib/abonneActif"
import { desactiverFiltreCursus, retablirFiltreCursus, useEtatFiltreCursus } from "@/lib/filtreCursus"
import { useI18n } from "@/lib/i18n"

const LIEN = "underline underline-offset-4 transition-colors hover:text-primary"

/**
 * Dit à l'élève ce qu'il regarde sur les listes dont l'examen est un paramètre d'URL (épreuves, cours), et comment
 * corriger ses matières.
 *
 * Abonné (profil actif abonné à son examen) : son examen est une évidence et ses matières un choix qu'il règle dans
 * « Mes accès » - le bandeau ne dit que « Tu vois tes 6 matières » avec le lien pour les modifier. Ni mention de l'examen,
 * ni sortie d'examen, ni « voir toutes les matières » (un clic trop facile ; l'interrupteur vit dans « Mes accès »).
 *
 * Visiteur ou compte sans abonnement : « Tu vois : <examen> » et « Voir tout le catalogue », qui sert à choisir. Le filtre
 * par examen reste un DÉFAUT, jamais une frontière côté serveur (liens partagés, robots, comparaison). Si la liste est
 * pourtant élargie (ancien lien, dernière recherche restaurée), le bandeau reste pour revenir à son examen - sans cela
 * l'abonné resterait coincé sur tout le catalogue.
 */
export function BandeauVue() {
  const { t, tn } = useI18n()
  const abonne = useAbonneActif()
  const { applique, cursusPrepare, voirTout, searchParams, setSearchParams } = useEtatFiltreCursus()
  const { actif, data } = useMatieres()

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
  const phraseMatieres = seulement ? tn("matieres.bandeau_seulement", data?.nb_affichees ?? 0) : t("matieres.bandeau_toutes")

  if (abonne) {
    if (!matieresMontrees) return null
    return (
      <p className="mb-4 flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-muted-foreground">
        <span>{phraseMatieres}</span>
        <Link to="/mes-acces" className={LIEN}>
          {t("matieres.bandeau_modifier")}
        </Link>
      </p>
    )
  }

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
        <Link to="/mes-acces" className={LIEN}>
          {t("matieres.bandeau_modifier")}
        </Link>
      )}
      <button
        type="button"
        onClick={() => setSearchParams(desactiverFiltreCursus(new URLSearchParams(searchParams)))}
        className={LIEN}
      >
        {t("ep.voir_catalogue")}
      </button>
    </p>
  )
}
