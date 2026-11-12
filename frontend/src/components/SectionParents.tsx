import { Link } from "react-router-dom"
import { ArrowRight, ShieldCheck, Smartphone, Users } from "lucide-react"

import { Button } from "@/components/ui/button"
import { PRIX_MOIS_ENFANT_SUPPLEMENTAIRE_FCFA, PRIX_MOIS_FCFA } from "@/lib/tarifs"
import { formatAmount } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/**
 * « Tu es parent ? » : l'accueil parle à l'élève (« tu », « ton examen ») alors que c'est souvent le parent qui paie. Ce
 * bloc lui donne, au même endroit, ce qu'il cherche avant de décider : ce que son enfant obtient, comment on paie, ce
 * qu'il garde sous contrôle (audit du 2026-11-12, UX-03). Il ne dit que ce que le produit fait déjà : profils d'enfants
 * dans un seul compte, Mobile Money sans prélèvement automatique, code parent pour les paiements et la gestion.
 */
export function SectionParents() {
  useI18n()
  const prix = formatAmount(PRIX_MOIS_FCFA)
  const prixSup = formatAmount(PRIX_MOIS_ENFANT_SUPPLEMENTAIRE_FCFA)

  const cartes = [
    { Icone: Users, titre: t("parents.c1_titre"), texte: t("parents.c1_texte", { prix_sup: prixSup }) },
    { Icone: Smartphone, titre: t("parents.c2_titre"), texte: t("parents.c2_texte", { prix }) },
    { Icone: ShieldCheck, titre: t("parents.c3_titre"), texte: t("parents.c3_texte") },
  ]

  return (
    <section className="mx-auto max-w-5xl px-4 pb-10 sm:px-6" aria-labelledby="accueil-parents">
      <h2 id="accueil-parents" className="font-display text-xl font-semibold">
        {t("parents.titre")}
      </h2>
      <p className="mt-1 max-w-2xl text-sm text-muted-foreground">{t("parents.sous_titre")}</p>
      <div className="mt-4 grid gap-5 sm:grid-cols-3">
        {cartes.map(({ Icone, titre, texte }) => (
          <div key={titre} className="rounded-2xl border border-border bg-card p-5">
            <span className="flex size-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <Icone className="size-5" aria-hidden="true" />
            </span>
            <h3 className="mt-3 font-display text-base font-semibold">{titre}</h3>
            <p className="mt-1 text-sm text-muted-foreground">{texte}</p>
          </div>
        ))}
      </div>
      <div className="mt-5 flex flex-wrap gap-2">
        <Button asChild>
          <Link to="/tarifs">
            {t("parents.voir_prix")}
            <ArrowRight className="size-4" aria-hidden="true" />
          </Link>
        </Button>
        <Button asChild variant="outline">
          <Link to="/aide/comment-payer">{t("parents.comment_payer")}</Link>
        </Button>
      </div>
    </section>
  )
}
