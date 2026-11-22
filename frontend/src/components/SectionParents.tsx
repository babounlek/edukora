import { Link } from "react-router-dom"
import { ShieldCheck, Smartphone, Users } from "lucide-react"

import { MotDuFondateur } from "@/components/MotDuFondateur"
import { Button } from "@/components/ui/button"
import { trackEvent } from "@/lib/analytics"
import { PRIX_MOIS_FCFA } from "@/lib/tarifs"
import { formatAmount } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/**
 * « Tu es parent ? » : l'accueil parle à l'élève (« tu », « ton examen ») alors que c'est souvent le parent qui paie. Ce
 * bloc lui donne, au même endroit, ce qu'il cherche avant de décider : ce que son enfant obtient, comment on paie, ce
 * qu'il garde sous contrôle (audit du 2026-11-12, UX-03). Il ne dit que ce que le produit fait déjà : profils d'enfants
 * dans un seul compte, Mobile Money sans prélèvement automatique, code parent pour les paiements et la gestion.
 *
 * Un seul bouton, « Comment payer ? » : le bloc qui suit sur l'accueil (« Prêt à commencer ? ») porte déjà « Voir les
 * prix », et les deux se suivaient à un écran d'écart (audit de l'accueil du 2026-11-15, R4).
 */
export function SectionParents() {
  useI18n()
  const prix = formatAmount(PRIX_MOIS_FCFA)

  const cartes = [
    { Icone: Users, titre: t("parents.c1_titre"), texte: t("parents.c1_texte") },
    { Icone: Smartphone, titre: t("parents.c2_titre"), texte: t("parents.c2_texte", { prix }) },
    { Icone: ShieldCheck, titre: t("parents.c3_titre"), texte: t("parents.c3_texte") },
  ]

  return (
    <section className="mx-auto max-w-5xl px-4 pb-10 sm:px-6" aria-labelledby="accueil-parents">
      <h2 id="accueil-parents" className="font-display text-xl font-semibold">
        {t("parents.titre")}
      </h2>
      <p className="mt-1 max-w-2xl text-sm text-muted-foreground">{t("parents.sous_titre")}</p>
      {/* Sur un téléphone, une seule carte à trois lignes, l'icône à gauche : trois cartes empilées faisaient 793 px,
          presque un écran, pour un bloc que l'élève ne lit pas (audit des accueils, 2026-11-21). Le texte est entier
          dans les deux cas. À partir de `sm`, les trois cartes côte à côte. */}
      <div className="mt-4 divide-y divide-border rounded-2xl border border-border bg-card sm:grid sm:grid-cols-3 sm:gap-5 sm:divide-y-0 sm:rounded-none sm:border-0 sm:bg-transparent">
        {cartes.map(({ Icone, titre, texte }) => (
          <div key={titre} className="flex gap-3 p-4 sm:block sm:rounded-2xl sm:border sm:border-border sm:bg-card sm:p-5">
            <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <Icone className="size-5" aria-hidden="true" />
            </span>
            <div className="min-w-0">
              <h3 className="font-display text-base font-semibold sm:mt-3">{titre}</h3>
              <p className="mt-1 text-sm text-muted-foreground">{texte}</p>
            </div>
          </div>
        ))}
      </div>
      {/* Le mot du fondateur, lui-même parent d'un élève : le seul nom de personne que lit le parent avant de payer. */}
      <MotDuFondateur className="mt-5" />
      <div className="mt-5 flex flex-wrap gap-2">
        <Button asChild variant="outline">
          <Link to="/aide/comment-payer" onClick={() => trackEvent("accueil_bouton_clic", { cible: "parents_payer" })}>
            {t("parents.comment_payer")}
          </Link>
        </Button>
      </div>
    </section>
  )
}
