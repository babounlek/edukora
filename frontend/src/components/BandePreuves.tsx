import { MotifMarque } from "@/components/MotifMarque"
import { t, tn, useI18n } from "@/lib/i18n"
import { SITE_NAME } from "@/lib/site"
import { formatAmount } from "@/lib/utils"

/**
 * Les chiffres du corpus, en grand, dans une bande vert profond sous le hero. Ils étaient dans trois pastilles grises au
 * bas du hero, alors que c'est l'argument le plus solide de la page et le seul qu'un concurrent ne peut pas recopier
 * (audit visuel de l'accueil, 2026-11-23). Tous viennent de l'API, aucun n'est écrit en dur.
 *
 * La bande est rendue avant l'arrivée des chiffres, à sa hauteur finale : sans cela, tout ce qui suit descendrait d'un
 * coup au moment où ils arrivent. Un chiffre à zéro n'est pas affiché (une langue sans épreuve inédite, par exemple).
 */
export function BandePreuves({ chiffres }: {
  /** `undefined` tant que les chiffres se chargent. */
  chiffres: { epreuves: number; cours: number; matieres: number; inedites?: number } | undefined
}) {
  useI18n()
  const pluriel = (n: number) => (n > 1 ? 2 : 1)
  const lignes = chiffres
    ? [
        { valeur: chiffres.epreuves, libelle: tn("accueil.stat_epreuves", pluriel(chiffres.epreuves)) },
        { valeur: chiffres.cours, libelle: t("accueil.stat_cours") },
        { valeur: chiffres.matieres, libelle: tn("accueil.stat_matieres", pluriel(chiffres.matieres)) },
        { valeur: chiffres.inedites ?? 0, libelle: tn("accueil.stat_inedites", pluriel(chiffres.inedites ?? 0)) },
      ].filter((ligne) => ligne.valeur > 0)
    : null

  return (
    <section aria-labelledby="accueil-preuves" className="relative overflow-hidden bg-brand-deep text-brand-deep-foreground">
      <MotifMarque className="absolute -right-10 -top-6 h-64 w-auto opacity-[0.06] sm:-right-4 sm:h-80" />
      <div className="relative mx-auto max-w-5xl px-4 py-10 sm:px-6 sm:py-14">
        <h2 id="accueil-preuves" className="font-display text-2xl font-semibold sm:text-3xl">
          {t("accueil.preuves_titre", { site: SITE_NAME })}
        </h2>
        {/* min-h : la place des chiffres, réservée pendant leur chargement (deux rangées sur un téléphone, une au-delà). */}
        <dl className="mt-7 grid min-h-[13.5rem] grid-cols-2 content-start gap-x-6 gap-y-8 sm:mt-9 sm:min-h-[6.75rem] sm:grid-cols-4">
          {lignes?.map(({ valeur, libelle }) => (
            <div key={libelle} className="flex flex-col-reverse justify-end gap-2">
              <dt className="text-sm leading-snug text-brand-deep-muted sm:text-base">{libelle}</dt>
              <dd className="font-display text-4xl font-semibold leading-none tracking-tight tabular-nums sm:text-5xl lg:text-6xl">
                {formatAmount(valeur)}
              </dd>
              <span aria-hidden="true" className="h-[3px] w-10 bg-gold" />
            </div>
          ))}
        </dl>
      </div>
    </section>
  )
}
