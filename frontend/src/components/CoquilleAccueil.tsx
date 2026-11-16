import { langueDeListe } from "@/lib/discipline"
import { t, useI18n } from "@/lib/i18n"

/** L'accueil d'un pays (/cm, /sn...), dans les chemins internes du routeur (le même en français et en anglais). */
export const ACCUEIL_PAYS_RE = /^\/[a-z]{2}\/?$/i

/**
 * Le hero de l'accueil visiteur sans ses données : ce que React affiche pendant que le morceau de la page se
 * télécharge. Même balisage et mêmes classes que la coquille statique de index.html (qu'il remplace au montage) et que
 * le hero de CataloguePage (qui le remplace ensuite) : le titre ne bouge pas et ne clignote pas entre les trois.
 * Changer l'un oblige à changer les deux autres ; CoquilleAccueil.test.tsx compare les textes avec index.html.
 */
export function CoquilleAccueil() {
  useI18n()
  return (
    <div className="min-h-[100svh]">
      <div className="relative mx-auto grid max-w-5xl gap-x-10 gap-y-6 px-4 pb-8 pt-10 sm:px-6 sm:pt-14 md:grid-cols-[1.1fr_1fr] md:items-center">
        <div className="md:col-start-1 md:row-start-1 md:self-end">
          <p className="mb-2 font-display text-sm italic text-primary">
            {langueDeListe("", false) === "en" ? "GCE O Level · GCE A Level" : "BEPC · Probatoire · BAC"}
          </p>
          <h1 className="max-w-xl font-display text-4xl font-semibold leading-[1.1] tracking-tight sm:text-5xl">
            {t("accueil.hero_titre_debut")}{" "}
            <span className="text-primary">{t("accueil.hero_titre_accent")}</span>.
          </h1>
          <p className="mt-4 max-w-lg text-muted-foreground">{t("accueil.hero_texte")}</p>
        </div>
        <div className="md:col-start-2 md:row-span-2 md:row-start-1">
          <div aria-hidden="true" className="min-h-[19.5rem] rounded-2xl border border-primary/25 bg-card shadow-lg shadow-primary/5" />
        </div>
        <div aria-hidden="true" className="min-h-[10rem] md:col-start-1 md:row-start-2 md:self-start" />
      </div>
    </div>
  )
}
