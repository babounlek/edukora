import { Link } from "react-router-dom"
import { ArrowRight, Check, Lock } from "lucide-react"

import type { Epreuve } from "@/api/types"
import { ApercuMessageParents, BoutonParents } from "@/components/BoutonParents"
import { ParrainageHint } from "@/components/ParrainageHint"
import { Button } from "@/components/ui/button"
import { epreuveDetailPath, epreuvesListPath } from "@/lib/countryPath"
import { useCursusDeclare } from "@/lib/cursusAccueil"
import { SITE_NAME } from "@/lib/site"
import { PRIX_MOIS_FCFA } from "@/lib/tarifs"
import { formatAmount } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/**
 * Le bloc « Débloque le corrigé complet » d'une épreuve dont le corrigé est réservé aux abonnés. C'est la page où arrive
 * un visiteur venu d'un moteur de recherche : il doit y lire, sans changer de page, combien ça coûte et où juger la
 * qualité avant de payer (audit du tunnel visiteur → abonné, 2026-11-21 : ni prix, ni renvoi vers les corrigés gratuits,
 * relevé par trois visiteurs sur trois).
 *
 * - Le prix est écrit sous les boutons, comme sous la séance verrouillée de l'accueil.
 * - Un lien mène aux corrigés en accès libre du même examen : on juge sur pièce, puis on revient.
 * - Quand l'épreuve vaut pour plusieurs examens (BAC C et D) et que la personne a déjà dit lequel elle prépare, un seul
 *   bouton, pour le sien : « S'abonner (C) » et « S'abonner (D) » côte à côte la faisaient douter de son choix.
 */
export function BlocCorrigeVerrouille({ epreuve, pays }: { epreuve: Epreuve; pays: string }) {
  useI18n()
  const cursusDeclare = useCursusDeclare()
  const lesSiens = epreuve.cursus.filter((c) => c.id === cursusDeclare)
  const cibles = lesSiens.length > 0 ? lesSiens : epreuve.cursus
  const seul = cibles.length === 1 ? cibles[0] : null
  const nomExamen = seul ? `${seul.examen_display}${seul.series ? ` ${seul.series.code}` : ""}` : null
  const chemin = epreuveDetailPath(pays, epreuve.slug as string)

  return (
    <section className="relative overflow-hidden rounded-3xl border border-primary/25 bg-gradient-to-br from-primary/[0.08] via-primary/[0.03] to-gold/[0.06] p-5 sm:p-7">
      <div className="flex items-start gap-4">
        <span className="flex size-12 shrink-0 items-center justify-center rounded-2xl bg-primary/10 text-primary">
          <Lock className="size-6" aria-hidden="true" />
        </span>
        <div className="min-w-0">
          <h2 className="font-display text-xl font-semibold sm:text-2xl">{t("ed.debloque")}</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            {cibles.length > 1 ? t("ed.bloc_texte_multi") : t("ed.bloc_texte")}
          </p>
        </div>
      </div>
      <ul className="mt-5 grid gap-2 sm:grid-cols-3">
        {(["ed.avantage1", "ed.avantage2", "ed.avantage3"] as const).map((avantage) => (
          <li key={avantage} className="flex items-start gap-2 rounded-xl bg-background/70 px-3 py-2.5 text-sm">
            <Check className="mt-0.5 size-4 shrink-0 text-primary" strokeWidth={3} aria-hidden="true" />
            {t(avantage)}
          </li>
        ))}
      </ul>
      <div className="mt-5 flex flex-wrap gap-2">
        {cibles.map((c) => (
          <Button key={c.id} asChild size="lg" className="h-12 rounded-full px-6 shadow-lg shadow-primary/25">
            <Link to={`/abonnement?cursus=${c.id}`}>
              {cibles.length > 1
                ? t("ed.sabonner_cursus", { cursus: c.series ? c.series.code : c.examen_display })
                : t("prix.sabonner")}
              <ArrowRight />
            </Link>
          </Button>
        ))}
        {/* « S'abonner » mène à la connexion avant tout prix (voir SubscribePage) : sans ce lien, un
            visiteur devait deviner que la page des prix existe, ou la chercher au bas de l'accueil. */}
        <Button asChild variant="outline" size="lg" className="h-12 rounded-full px-6">
          <Link to="/tarifs">{t("ed.voir_prix")}</Link>
        </Button>
      </div>
      <p className="mt-3 text-sm font-medium">{t("seance.prix_abonnement", { prix: formatAmount(PRIX_MOIS_FCFA) })}</p>
      <p className="mt-1 text-sm text-muted-foreground">
        {t("ed.pas_sur")}{" "}
        <Link
          to={`${epreuvesListPath(pays)}?gratuit=true${seul ? `&cursus=${seul.id}` : ""}`}
          className="font-medium text-primary underline underline-offset-4"
        >
          {nomExamen ? t("ed.corriges_gratuits_examen", { examen: nomExamen }) : t("ed.corriges_gratuits")}
        </Link>
      </p>
      {/* Ce sont les parents qui paient : un message tout prêt avec le prix et le moyen de payer. */}
      <div className="mt-4 flex flex-col items-start gap-1">
        <BoutonParents
          examen={seul ? seul.examen_display : undefined}
          contenu={t("parents.contenu_epreuve", { titre: epreuve.title })}
          className="h-11 rounded-full px-5"
        />
        <p className="text-xs text-muted-foreground">{t("parents.aide")}</p>
        <ApercuMessageParents
          examen={seul ? seul.examen_display : undefined}
          contenu={t("parents.contenu_epreuve", { titre: epreuve.title })}
        />
      </div>
      <div className="mt-4">
        <ParrainageHint chemin={chemin} texte={t("ed.partage", { titre: epreuve.title, site: SITE_NAME })} type="epreuve" />
      </div>
    </section>
  )
}
