import { SITE_NAME } from "@/lib/site"
import { cn } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/**
 * Le mot du fondateur, signé de son nom et de ses deux qualités : parent d'un élève et fondateur du site. Il répond à
 * « qui est derrière ? », la question d'un parent avant de payer (audit du tunnel visiteur → abonné, 2026-11-21 : aucun
 * nom de personne sur le site).
 *
 * Ce n'est PAS un avis de client et il ne doit jamais être rangé avec eux : la section des avis ne montre que des avis
 * vérifiés (voir SocialProofSection), et la page « À propos » promet qu'il n'y en a pas de faux. D'où le titre à part
 * et la signature qui dit le lien avec le site.
 *
 * « Depuis trois mois » est vrai au 2026-11-22 : à remplacer par le mois d'arrêt quand le texte sera relu.
 */
export function MotDuFondateur({ className }: { className?: string }) {
  useI18n()
  return (
    <figure className={cn("rounded-2xl border border-border bg-card p-5", className)}>
      <figcaption className="text-xs font-semibold uppercase tracking-wide text-primary">
        {t("fondateur.titre", { site: SITE_NAME })}
      </figcaption>
      <blockquote className="mt-2 font-display text-base leading-relaxed">
        {t("fondateur.citation", { site: SITE_NAME })}
      </blockquote>
      <p className="mt-3 text-sm">
        <span className="font-semibold">{t("fondateur.nom")}</span>
        <span className="text-muted-foreground">, {t("fondateur.role", { site: SITE_NAME })}</span>
      </p>
    </figure>
  )
}
