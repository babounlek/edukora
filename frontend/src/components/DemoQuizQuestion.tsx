import type { ReactNode } from "react"
import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { Lock, Sparkles } from "lucide-react"

import { getQuestionExemple } from "@/api/endpoints"
import { useCountry } from "@/context/CountryContext"
import { epreuveReaderPath } from "@/lib/countryPath"
import { cn } from "@/lib/utils"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { langueCourante, t, useI18n, type CleI18n } from "@/lib/i18n"

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
 *
 * En français : la question de démonstration d'origine (clés `qd.demo_*`). Dans les autres langues : une vraie
 * question QCM d'une épreuve en accès libre, lue en direct (voir catalog.views.question_exemple_gratuite), avec un
 * lien vers l'épreuve - la preuve ne peut plus s'écarter de ce que le site propose. Si le serveur n'en a aucune,
 * ou ne répond pas, la question de démonstration de la langue sert de repli.
 */
export function DemoQuizQuestion({ lienConnexion }: { lienConnexion?: ReactNode }) {
  useI18n()
  const { country } = useCountry()
  const langue = langueCourante()
  const { data: reelle, isPending } = useQuery({
    queryKey: ["question-exemple", country, langue],
    queryFn: ({ signal }) => getQuestionExemple(langue, country, signal),
    enabled: langue !== "fr" && Boolean(country),
    staleTime: 60 * 60_000,
    retry: false,
  })
  // Le temps de la réponse, un emplacement neutre : afficher d'abord la question de repli puis la remplacer
  // ferait clignoter deux questions différentes.
  const enChargement = langue !== "fr" && Boolean(country) && isPending

  const question = reelle?.question ?? t("qd.demo_question")
  const choix = reelle ? reelle.choix : CHOIX_DEMO.map((c) => ({ lettre: c.lettre, texte: t(c.texte) }))
  const bonneReponse = reelle?.reponse_correcte ?? "a"
  const source = reelle
    ? {
        slug: reelle.epreuve.slug,
        texte: t("qd.demo_source_live", { epreuve: reelle.epreuve.title, numero: reelle.numero }),
      }
    : t("qd.demo_source") && t("qd.demo_source_slug")
      ? { slug: t("qd.demo_source_slug"), texte: t("qd.demo_source") }
      : null

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
        {enChargement ? (
          <div aria-hidden data-testid="demo-chargement" className="flex animate-pulse flex-col gap-2">
            <div className="h-4 w-11/12 rounded bg-muted" />
            {CHOIX_DEMO.map((c) => (
              <div key={c.lettre} className="h-9 rounded-lg bg-muted/70" />
            ))}
          </div>
        ) : (
          <>
            <p aria-hidden className="text-sm">
              {question}
            </p>
            {source && (
              <Link
                to={epreuveReaderPath(country, source.slug)}
                className="-mt-2 text-xs text-muted-foreground underline underline-offset-4 transition-colors hover:text-primary"
              >
                {source.texte}
              </Link>
            )}
            <div aria-hidden className="flex flex-col gap-2">
              {choix.map((c) => (
                <div
                  key={c.lettre}
                  className={cn(
                    "flex items-start gap-2 rounded-lg border px-3 py-2 text-sm",
                    c.lettre === bonneReponse ? "border-success/40 bg-success/[0.06]" : "border-border",
                  )}
                >
                  <span className="font-medium">{c.lettre.toUpperCase()}.</span>
                  <span className="min-w-0 flex-1">{c.texte}</span>
                  {c.lettre === bonneReponse && (
                    <span className="ml-auto shrink-0 rounded-full bg-success/15 px-2 py-0.5 text-[11px] font-medium text-success">
                      {t("qd.demo_bonne")}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </>
        )}
        <div className="relative -mx-6 -mb-6 mt-1 flex flex-col items-center gap-2 rounded-b-xl border-t border-border bg-muted/40 px-6 py-5 text-center">
          <Lock className="size-4 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">{t("qd.demo_cta")}</p>
          {lienConnexion}
        </div>
      </CardContent>
    </Card>
  )
}
