import { useLocation } from "react-router-dom"

import { BoutonPartager } from "@/components/BoutonPartager"
import { SITE_NAME } from "@/lib/site"
import { t, useI18n } from "@/lib/i18n"

type TypeContenu = "epreuve" | "cours" | "inedite"

/**
 * Partage compact, à poser sur un mur payant (corrigé/épreuve inédite verrouillés) : l'élève qui ne
 * peut pas payer maintenant envoie la page à un ami en un clic. Décision du 2026-09-28 : le
 * parrainage est un simple partage de lien, sans remise ni récompense d'aucun côté - voir
 * project_parrainage_eleve_recalibrage. Le lien porte le code de parrainage s'il est connecté.
 *
 * Sans `chemin`, on partage la page courante (sans son lecteur, derrière le mur payant) : c'est le
 * cas des écrans qui ne connaissent pas leur contenu (voir AccesRefuse).
 */
export function ParrainageHint({ chemin, texte, type }: { chemin?: string; texte?: string; type?: TypeContenu }) {
  useI18n()
  const { pathname } = useLocation()
  const cheminPartage = chemin ?? pathname.replace(/\/lire$/, "")
  const genre: TypeContenu = type ?? (cheminPartage.startsWith("/cours/") ? "cours" : "epreuve")
  const titre = document.title.replace(new RegExp(`\\s*\\|\\s*${SITE_NAME}$`), "")

  return (
    <BoutonPartager
      chemin={cheminPartage}
      texte={texte ?? (titre ? t("ed.partage", { titre, site: SITE_NAME }) : t("ed.partage_defaut", { site: SITE_NAME }))}
      type={genre}
      variant="ghost"
      className="h-auto w-fit gap-1.5 px-0 text-xs font-normal text-muted-foreground hover:bg-transparent hover:text-primary hover:underline"
      libelle={t("ed.ami")}
    />
  )
}
