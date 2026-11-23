import { Link } from "react-router-dom"
import { ArrowRight } from "lucide-react"

import { trackEvent } from "@/lib/analytics"
import { PHOTO_FONDATEUR, SITE_NAME } from "@/lib/site"
import { cn } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/**
 * Le jour où le répétiteur a été arrêté : « depuis trois mois », dit par le fondateur le 2026-11-22. La durée affichée
 * se calcule à partir de cette date, pour que la phrase reste vraie sans qu'on y retouche. À corriger ici si le mois
 * exact est connu.
 */
const ARRET_REPETITEUR = new Date(2026, 7, 22)

/**
 * « trois mois », « sept mois », puis « plus d'un an », « plus de 2 ans ». Jamais moins de trois mois : c'est ce qui a
 * été dit, et une horloge d'appareil mal réglée ne doit pas faire écrire « depuis zéro mois ».
 */
export function dureeSansRepetiteur(maintenant: Date = new Date()): string {
  const mois =
    (maintenant.getFullYear() - ARRET_REPETITEUR.getFullYear()) * 12 +
    (maintenant.getMonth() - ARRET_REPETITEUR.getMonth()) -
    (maintenant.getDate() < ARRET_REPETITEUR.getDate() ? 1 : 0)
  if (mois >= 24) return t("fondateur.duree_ans", { n: Math.floor(mois / 12) })
  if (mois >= 12) return t("fondateur.duree_un_an")
  // De trois à onze, en toutes lettres, comme dans la phrase d'origine.
  const enLettres = t("fondateur.mois_en_lettres").split(",")
  return t("fondateur.duree_mois", { n: enLettres[Math.max(mois, 3) - 3] })
}

/**
 * Le mot du fondateur, signé de son nom et de ses deux qualités : parent d'un élève et fondateur du site. Il répond à
 * « qui est derrière ? », la question d'un parent avant de payer (audit du tunnel visiteur → abonné, 2026-11-21 : aucun
 * nom de personne sur le site).
 *
 * Ce n'est PAS un avis de client et il ne doit jamais être rangé avec eux : la section des avis ne montre que des avis
 * vérifiés (voir SocialProofSection), et la page « À propos » promet qu'il n'y en a pas de faux. D'où le titre à part
 * et la signature qui dit le lien avec le site.
 */
export function MotDuFondateur({ className, variante = "carte" }: {
  className?: string
  /**
   * `carte` : l'encadré de la page « À propos ». `bande` : la version de l'accueil, en grand, avec la photo du
   * fondateur quand elle existe (voir PHOTO_FONDATEUR) et un lien vers « À propos ». Le mot était rangé au bas du bloc
   * des parents, en petit : c'est pourtant le seul visage de la page (audit visuel de l'accueil, 2026-11-23).
   */
  variante?: "carte" | "bande"
}) {
  useI18n()
  const citation = t("fondateur.citation", { site: SITE_NAME, duree: dureeSansRepetiteur() })

  if (variante === "bande") {
    return (
      <figure className={cn("flex flex-col gap-6 sm:flex-row sm:items-center sm:gap-10", className)}>
        {PHOTO_FONDATEUR && (
          <img
            src={PHOTO_FONDATEUR.src}
            width={PHOTO_FONDATEUR.largeur}
            height={PHOTO_FONDATEUR.hauteur}
            alt={t("fondateur.photo_alt", { nom: t("fondateur.nom"), site: SITE_NAME })}
            loading="lazy"
            decoding="async"
            className="h-auto w-32 shrink-0 rounded-3xl object-cover shadow-lg shadow-primary/10 ring-1 ring-border sm:w-52 lg:w-60"
          />
        )}
        <div className="min-w-0">
          <figcaption className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">
            {t("fondateur.titre", { site: SITE_NAME })}
          </figcaption>
          <blockquote className="mt-3 font-display text-xl leading-snug sm:text-2xl lg:text-[1.7rem] lg:leading-[1.35]">{citation}</blockquote>
          <p className="mt-4">
            <span className="block font-semibold">{t("fondateur.nom")}</span>
            <span className="block text-sm text-muted-foreground first-letter:uppercase">{t("fondateur.role", { site: SITE_NAME })}</span>
          </p>
          <Link
            to="/a-propos"
            onClick={() => trackEvent("accueil_bouton_clic", { cible: "a_propos" })}
            className="mt-3 inline-flex min-h-11 items-center gap-1.5 text-sm font-medium text-primary underline-offset-4 hover:underline"
          >
            {t("fondateur.lien", { site: SITE_NAME })}
            <ArrowRight className="size-4" aria-hidden="true" />
          </Link>
        </div>
      </figure>
    )
  }

  return (
    <figure className={cn("rounded-2xl border border-border bg-card p-5", className)}>
      <figcaption className="text-xs font-semibold uppercase tracking-wide text-primary">
        {t("fondateur.titre", { site: SITE_NAME })}
      </figcaption>
      <blockquote className="mt-2 font-display text-base leading-relaxed">{citation}</blockquote>
      <p className="mt-3 text-sm">
        <span className="font-semibold">{t("fondateur.nom")}</span>
        <span className="text-muted-foreground">, {t("fondateur.role", { site: SITE_NAME })}</span>
      </p>
    </figure>
  )
}
