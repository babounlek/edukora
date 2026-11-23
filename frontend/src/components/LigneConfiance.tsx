import type { ReactNode } from "react"
import { Link } from "react-router-dom"
import { Building2, MessageCircle, ShieldCheck } from "lucide-react"

import { PastilleOperateur } from "@/components/PastilleOperateur"
import { trackEvent } from "@/lib/analytics"
import { t, useI18n } from "@/lib/i18n"
import { CONTACT_WHATSAPP_AFFICHAGE, CONTACT_WHATSAPP_URL, EDITEUR_NOM } from "@/lib/site"

function Element({ icone, titre, children }: { icone: ReactNode; titre: ReactNode; children: ReactNode }) {
  return (
    <div className="flex items-start gap-3">
      <span className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">{icone}</span>
      <div className="min-w-0">
        <p className="text-sm font-semibold">{titre}</p>
        <div className="mt-0.5 text-sm text-muted-foreground">{children}</div>
      </div>
    </div>
  )
}

/**
 * Qui est derrière, comment on paie, à qui écrire : les trois choses qu'un parent cherche avant de faire confiance, sur
 * une ligne, juste sous les chiffres. Elles n'existaient qu'au pied de page, en petit : l'éditeur dans le copyright, les
 * opérateurs en pastilles de 11 px (audit visuel de l'accueil, 2026-11-23).
 *
 * Rien n'est écrit ici en dur : l'éditeur et le numéro viennent de lib/site, la ville de la page « À propos ». Les
 * opérateurs restent des pastilles de texte, sans logo (droits d'usage non établis, voir PastilleOperateur).
 */
export function LigneConfiance() {
  useI18n()
  const mesurer = (cible: string) => () => trackEvent("accueil_bouton_clic", { cible })

  return (
    <section aria-label={t("confiance.aria")} className="border-b border-border bg-card">
      <div className="mx-auto grid max-w-5xl gap-x-8 gap-y-5 px-4 py-6 sm:grid-cols-3 sm:px-6">
        <Element icone={<ShieldCheck className="size-5" aria-hidden="true" />} titre={t("confiance.paiement_titre")}>
          <p>{t("confiance.paiement_texte")}</p>
          <p className="mt-1.5 flex flex-wrap gap-1.5">
            <PastilleOperateur operateur="ORANGE" className="text-xs">Orange Money</PastilleOperateur>
            <PastilleOperateur operateur="MTN" className="text-xs">MTN MoMo</PastilleOperateur>
          </p>
        </Element>
        <Element icone={<Building2 className="size-5" aria-hidden="true" />} titre={t("confiance.editeur_titre", { editeur: EDITEUR_NOM })}>
          <p>{t("ab.qui_lieu")}</p>
          <Link
            to="/a-propos"
            onClick={mesurer("a_propos")}
            className="mt-1 inline-flex min-h-9 items-center font-medium text-primary underline-offset-4 hover:underline"
          >
            {t("confiance.editeur_lien")}
          </Link>
        </Element>
        <Element icone={<MessageCircle className="size-5" aria-hidden="true" />} titre={t("confiance.contact_titre")}>
          <p>{t("ft.whatsapp_titre")}</p>
          <a
            href={CONTACT_WHATSAPP_URL}
            target="_blank"
            rel="noopener noreferrer"
            onClick={mesurer("whatsapp")}
            className="mt-1 inline-flex min-h-9 items-center font-medium text-primary underline-offset-4 hover:underline"
          >
            WhatsApp {CONTACT_WHATSAPP_AFFICHAGE}
          </a>
        </Element>
      </div>
    </section>
  )
}
