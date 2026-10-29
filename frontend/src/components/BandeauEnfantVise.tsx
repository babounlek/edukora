import { Link } from "react-router-dom"
import { User } from "lucide-react"

import { useProfils } from "@/lib/changerProfilActif"
import { t, useI18n } from "@/lib/i18n"

/**
 * « Abonnement de {prénom} » et ce qui va se passer (l'accès s'ouvrira sur SON profil) : au-dessus des formules, quand on
 * arrive avec `?profil=` depuis le bouton « Payer pour {prénom} » de Mes accès. Un parent de plusieurs enfants doit lire pour
 * qui il est sur le point de payer, et où l'accès s'ouvrira.
 *
 * Rien si le paramètre est absent ou n'est pas un enfant de ce compte (lien périmé, autre compte) : mieux vaut aucune phrase
 * qu'un prénom faux.
 */
export function BandeauEnfantVise({ profilId }: { profilId: string | null }) {
  useI18n()
  const profils = useProfils()
  const enfant = profilId ? profils.find((p) => String(p.id) === profilId) : undefined
  if (!enfant) return null
  const prenom = enfant.prenom || t("ac.sans_nom")

  return (
    <div
      role="status"
      className="mb-6 flex flex-col gap-1 rounded-xl border border-primary/30 bg-primary/[0.06] px-4 py-3 sm:flex-row sm:items-center sm:justify-between"
    >
      <div className="flex items-start gap-2.5">
        <User className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden="true" />
        <div>
          <p className="text-sm font-semibold">{t("prix.pour_enfant", { prenom })}</p>
          <p className="text-sm text-muted-foreground">{t("prix.pour_enfant_texte", { prenom })}</p>
        </div>
      </div>
      <Link to="/mes-acces" className="text-xs font-medium text-primary underline-offset-4 hover:underline">
        {t("prix.pour_enfant_autre")}
      </Link>
    </div>
  )
}
