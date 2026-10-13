import type { ReactNode } from "react"
import { Lock, Sparkles } from "lucide-react"

import { cn } from "@/lib/utils"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { t, useI18n, type CleI18n } from "@/lib/i18n"

const CHOIX_DEMO = [
  { lettre: "a", texte: "qd.demo_a" },
  { lettre: "b", texte: "qd.demo_b" },
  { lettre: "c", texte: "qd.demo_c" },
  { lettre: "d", texte: "qd.demo_d" },
] as const satisfies readonly { lettre: string; texte: CleI18n }[]

/**
 * Question figée, non interactive, montrée à la place du récapitulatif tant que le
 * visiteur n'a pas d'abonnement (voir QuizStartPage) - la colonne de droite ne rendait
 * rien sans abonnement, ce qui se lisait comme une page inachevée. Donne un aperçu
 * concret du format QCM plutôt qu'une simple promesse de fonctionnalité.
 */
export function DemoQuizQuestion({ lienConnexion }: { lienConnexion: ReactNode }) {
  useI18n()
  return (
    // aria-hidden sur la question factice seulement, pas sur la carte : le lien de connexion
    // qu'elle porte est un vrai contrôle, qu'un lecteur d'écran doit atteindre.
    <Card className="select-none">
      <CardHeader aria-hidden className="pb-4">
        <CardTitle className="flex items-center gap-2 font-display text-base">
          <Sparkles className="size-4 text-primary" />
          {t("qd.demo_titre")}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <p aria-hidden className="text-sm">
          {t("qd.demo_question")}
        </p>
        <div aria-hidden className="flex flex-col gap-2">
          {CHOIX_DEMO.map((choix) => (
            <div
              key={choix.lettre}
              className={cn(
                "flex items-start gap-2 rounded-lg border px-3 py-2 text-sm",
                choix.lettre === "a" ? "border-success/40 bg-success/[0.06]" : "border-border",
              )}
            >
              <span className="font-medium">{choix.lettre.toUpperCase()}.</span>
              <span>{t(choix.texte)}</span>
            </div>
          ))}
        </div>
        <div className="relative -mx-6 -mb-6 mt-1 flex flex-col items-center gap-2 rounded-b-xl border-t border-border bg-muted/40 px-6 py-5 text-center">
          <Lock className="size-4 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">{t("qd.demo_cta")}</p>
          {lienConnexion}
        </div>
      </CardContent>
    </Card>
  )
}
