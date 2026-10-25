import { Check, ChevronDown, Flame, Zap } from "lucide-react"

import type { EtatXp, SerieDeJours } from "@/api/types"
import { NiveauXp } from "@/components/NiveauXp"
import { RythmeRapide } from "@/components/RythmeRapide"
import { cn } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/**
 * L'objectif d'XP du jour, la série et la semaine sur UNE ligne fine : de quoi se situer d'un
 * coup d'œil sans repousser le bouton principal sous le pli. Les versions détaillées
 * (ObjectifXp, SemaineDeSerie) servent l'écran de fin de quiz, où l'élève a le temps de lire.
 *
 * Objectif atteint : « Objectif atteint » plutôt que « 35 / 20 XP », qui ressemble à une erreur.
 */
export function LigneJour({ etat, serie }: { etat: EtatXp; serie: SerieDeJours }) {
  useI18n()
  const initiales = t("ligne.initiales").split(",")
  const noms = t("gl.sem_noms").split(",")
  const semaine = serie.semaine
  const part = etat.objectif > 0 ? Math.min(100, Math.round((100 * etat.xp) / etat.objectif)) : 0

  return (
    <div className="mb-5 flex flex-wrap items-center justify-between gap-x-6 gap-y-2.5 rounded-2xl border border-border/70 bg-muted/30 px-4 py-2.5">
      <div className="flex items-center gap-2.5 text-sm">
        {etat.atteint ? (
          <Check className="size-4 text-success" aria-hidden="true" />
        ) : (
          <Zap className="size-4 text-gold-text" aria-hidden="true" />
        )}
        {/* Le texte de l'objectif ouvre le choix du rythme : il n'était réglable que dans « Mon compte ». */}
        <RythmeRapide etat={etat} className="-my-1.5 flex min-h-9 items-center gap-1 py-1.5">
          <span className={cn("font-semibold", etat.atteint && "text-success")}>
            {etat.atteint ? t("ligne.objectif_atteint") : t("ligne.points", { xp: etat.xp, objectif: etat.objectif })}
          </span>
          <ChevronDown className="size-3.5 text-muted-foreground" aria-hidden="true" />
        </RythmeRapide>
        <div
          className="h-1.5 w-16 overflow-hidden rounded-full bg-secondary sm:w-24"
          role="progressbar"
          aria-label={t("ligne.objectif_aria")}
          aria-valuemin={0}
          aria-valuemax={etat.objectif}
          aria-valuenow={Math.min(etat.xp, etat.objectif)}
        >
          <div
            className={cn("h-full rounded-full transition-all duration-700", etat.atteint ? "bg-success" : "bg-gold")}
            style={{ width: `${part}%` }}
          />
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
        {/* Le niveau, sur la ligne que l'élève voit à chaque visite : de quoi se situer et viser le suivant. */}
        {etat.niveau && <NiveauXp niveau={etat.niveau} compact />}
        {/* La série se voit dès le premier jour (« Jour 1 : bien parti ! ») : attendre le deuxième la cachait à qui venait de
            commencer, alors que c'est le premier jour qu'elle donne envie de revenir (test élève Guyguy). Elle ne culpabilise
            jamais ; un repos pardonné reste signalé en infobulle. */}
        {serie.jours >= 1 && (
          <span
            className="flex items-center gap-1 whitespace-nowrap text-sm font-semibold"
            title={serie.repos_pris ? t("ligne.repos_pardonne") : undefined}
          >
            <Flame className="size-4 text-warning" aria-hidden="true" />
            {serie.jours === 1 ? t("serie.premier_jour") : t("serie.jours_de_suite", { n: serie.jours })}
          </span>
        )}
        {semaine && semaine.length === 7 && (
          <ol className="flex gap-1" aria-label={t("ligne.semaine_aria")}>
            {semaine.map((jour, i) => (
              <li
                key={jour.date}
                role="img"
                aria-label={`${noms[i]}, ${jour.fait ? t("ligne.travaille") : jour.aujourdhui ? t("ligne.aujourdhui_pas_encore") : t("ligne.non_travaille")}`}
                title={noms[i]}
                className={cn(
                  "flex size-5 items-center justify-center rounded-full border text-[0.6rem] font-semibold",
                  jour.fait ? "border-gold/50 bg-gold/20 text-gold-text" : "border-border bg-card text-muted-foreground",
                  jour.aujourdhui && !jour.fait && "border-dashed border-primary/60",
                )}
              >
                {jour.fait ? <Check className="size-3" aria-hidden="true" /> : initiales[i]}
              </li>
            ))}
          </ol>
        )}
      </div>
    </div>
  )
}
