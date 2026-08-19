import type { ReactNode } from "react"
import { Lock, Sparkles } from "lucide-react"

import { cn } from "@/lib/utils"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const CHOIX_DEMO = [
  { lettre: "a", texte: "La dérivée s'annule et change de signe" },
  { lettre: "b", texte: "La fonction est continue" },
  { lettre: "c", texte: "La courbe passe par l'origine" },
  { lettre: "d", texte: "Le second membre est positif" },
]

/**
 * Question figée, non interactive, montrée à la place du récapitulatif tant que le
 * visiteur n'a pas d'abonnement (voir QuizStartPage) - la colonne de droite ne rendait
 * rien sans abonnement, ce qui se lisait comme une page inachevée. Donne un aperçu
 * concret du format QCM plutôt qu'une simple promesse de fonctionnalité.
 */
export function DemoQuizQuestion({ lienConnexion }: { lienConnexion: ReactNode }) {
  return (
    <Card aria-hidden className="select-none">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 font-display text-base">
          <Sparkles className="size-4 text-primary" />
          Exemple de question
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <p className="text-sm">
          À quelle condition un extremum local d'une fonction dérivable est-il atteint en un point ?
        </p>
        <div className="flex flex-col gap-2">
          {CHOIX_DEMO.map((choix) => (
            <div
              key={choix.lettre}
              className={cn(
                "flex items-start gap-2 rounded-lg border px-3 py-2 text-sm",
                choix.lettre === "a" ? "border-success/40 bg-success/[0.06]" : "border-border",
              )}
            >
              <span className="font-medium">{choix.lettre.toUpperCase()}.</span>
              <span>{choix.texte}</span>
            </div>
          ))}
        </div>
        <div className="relative -mx-6 -mb-6 mt-1 flex flex-col items-center gap-2 rounded-b-xl border-t border-border bg-muted/40 px-6 py-5 text-center">
          <Lock className="size-4 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">Réponds pour de vrai et suis ta progression thème par thème.</p>
          {lienConnexion}
        </div>
      </CardContent>
    </Card>
  )
}
