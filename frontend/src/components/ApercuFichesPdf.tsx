import { CheckCircle2, FileText, Printer } from "lucide-react"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

/**
 * Aperçu figé des deux PDF générés (énoncé + corrigé), montré à la place du
 * récapitulatif tant que le répétiteur n'a pas l'add-on Fiches (voir FichesPage) - la
 * colonne de droite ne rendait rien sans lui, ce qui se lisait comme une page
 * inachevée. Donne un aperçu concret du produit plutôt qu'une simple promesse.
 */
export function ApercuFichesPdf() {
  return (
    <Card aria-hidden className="select-none">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 font-display text-base">
          <Printer className="size-4 text-primary" />
          Deux PDF, prêts à imprimer
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <div className="flex items-center gap-3 rounded-lg border border-border bg-card px-3 py-2.5">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <FileText className="size-4" />
          </span>
          <div className="min-w-0">
            <p className="text-sm font-medium">Fiche énoncé</p>
            <p className="text-xs text-muted-foreground">À distribuer telle quelle à tes élèves.</p>
          </div>
        </div>
        <div className="flex items-center gap-3 rounded-lg border border-border bg-card px-3 py-2.5">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-success/10 text-success">
            <CheckCircle2 className="size-4" />
          </span>
          <div className="min-w-0">
            <p className="text-sm font-medium">Fiche corrigé</p>
            <p className="text-xs text-muted-foreground">Le même exercice, corrigé pas à pas, à ton nom.</p>
          </div>
        </div>
        <p className="mt-1 text-xs text-muted-foreground">
          Choisis les compétences et la difficulté ci-contre : les deux documents se composent en quelques secondes.
        </p>
      </CardContent>
    </Card>
  )
}
