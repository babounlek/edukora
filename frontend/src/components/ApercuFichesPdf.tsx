import { CheckCircle2, FileText, Printer } from "lucide-react"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { t, useI18n } from "@/lib/i18n"

/**
 * Aperçu figé des deux PDF générés (énoncé + corrigé), montré à la place du
 * récapitulatif tant que le répétiteur n'a pas l'add-on Fiches (voir FichesPage) - la
 * colonne de droite ne rendait rien sans lui, ce qui se lisait comme une page
 * inachevée. Donne un aperçu concret du produit plutôt qu'une simple promesse.
 */
export function ApercuFichesPdf() {
  useI18n()
  return (
    <Card aria-hidden className="select-none">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 font-display text-base">
          <Printer className="size-4 text-primary" />
          {t("fi.ap_titre")}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <div className="flex items-center gap-3 rounded-lg border border-border bg-card px-3 py-2.5">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <FileText className="size-4" />
          </span>
          <div className="min-w-0">
            <p className="text-sm font-medium">{t("fi.ap_enonce")}</p>
            <p className="text-xs text-muted-foreground">{t("fi.ap_enonce_texte")}</p>
          </div>
        </div>
        <div className="flex items-center gap-3 rounded-lg border border-border bg-card px-3 py-2.5">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-success/10 text-success">
            <CheckCircle2 className="size-4" />
          </span>
          <div className="min-w-0">
            <p className="text-sm font-medium">{t("fi.ap_corrige")}</p>
            <p className="text-xs text-muted-foreground">{t("fi.ap_corrige_texte")}</p>
          </div>
        </div>
        <p className="mt-1 text-xs text-muted-foreground">
          {t("fi.ap_pied")}
        </p>
      </CardContent>
    </Card>
  )
}
