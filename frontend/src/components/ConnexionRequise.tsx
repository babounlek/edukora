import { Link } from "react-router-dom"
import { LogIn } from "lucide-react"

import { Button } from "@/components/ui/button"
import { t, useI18n } from "@/lib/i18n"

/**
 * Ce qu'un visiteur voit sur une page réservée aux comptes (Examens blancs, Erreurs, Cartes, Carnet, Réussites).
 *
 * Avant, ces pages le renvoyaient d'office sur /connexion : il arrivait sur un formulaire sans savoir pourquoi, ni
 * ce qu'il venait chercher. Ici la page dit ce qu'elle contient et pourquoi un compte est nécessaire, puis propose
 * de se connecter ; la destination est mémorisée pour y revenir une fois connecté.
 */
export function ConnexionRequise({ from, titre, explication }: { from: string; titre: string; explication: string }) {
  useI18n()
  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-10 sm:px-6 sm:py-16">
      <div className="mx-auto flex max-w-md flex-col items-center gap-4 rounded-2xl border border-border bg-card px-6 py-10 text-center">
        <span className="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary">
          <LogIn className="size-6" aria-hidden="true" />
        </span>
        <h1 className="font-display text-2xl font-semibold tracking-tight">{titre}</h1>
        <p className="text-sm text-muted-foreground">{explication}</p>
        <p className="text-sm text-muted-foreground">{t("connexion_requise.texte")}</p>
        <Button asChild size="lg" className="w-full sm:w-auto">
          <Link to="/connexion" state={{ from, intent: explication }}>
            {t("connexion_requise.bouton")}
          </Link>
        </Button>
        <Link to="/" className="text-sm text-muted-foreground underline-offset-4 hover:underline">
          {t("connexion_requise.retour")}
        </Link>
      </div>
    </div>
  )
}
