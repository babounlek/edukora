import { useQuery } from "@tanstack/react-query"
import { BookOpen, BrainCircuit, FileCheck2, Layers, Sparkles, type LucideIcon } from "lucide-react"

import { getCursusContenu } from "@/api/endpoints"
import { Card, CardContent } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { formatAmount } from "@/lib/utils"
import { t, tn, useI18n } from "@/lib/i18n"

interface ContenuDebloqueProps {
  cursusId: number
  // Les épreuves inédites ne sont comptées que si le plan choisi les inclut - sinon l'encadré
  // promettrait un contenu que l'abonnement ne débloque pas.
  inclutInedit: boolean
}

interface Ligne {
  icone: LucideIcon
  valeur: number
  libelle: string
}

/**
 * Encadré « Ce que tu débloques » de la page d'abonnement : des comptages réels du contenu
 * publié pour le cursus (voir catalog.views.CursusContenuView), jamais des chiffres écrits en dur.
 * Une ligne à zéro est masquée plutôt qu'affichée « 0 », et l'encadré disparaît si le chargement
 * échoue : mieux vaut pas de preuve chiffrée qu'une preuve fausse ou un message d'erreur sur la
 * page où l'on paie.
 */
export function ContenuDebloque({ cursusId, inclutInedit }: ContenuDebloqueProps) {
  useI18n()
  const { data } = useQuery({
    queryKey: ["cursus-contenu", cursusId],
    queryFn: ({ signal }) => getCursusContenu(cursusId, signal),
    staleTime: 10 * 60 * 1000,
  })

  if (!data) return null

  const lignes: Ligne[] = [
    { icone: FileCheck2, valeur: data.corriges, libelle: tn("cd.corriges", data.corriges) },
    { icone: BookOpen, valeur: data.cours, libelle: tn("cd.cours", data.cours) },
    { icone: BrainCircuit, valeur: data.questions_quiz, libelle: tn("cd.quiz", data.questions_quiz) },
    ...(inclutInedit
      ? [{ icone: Sparkles, valeur: data.epreuves_inedites, libelle: tn("cd.inedites", data.epreuves_inedites) }]
      : []),
    { icone: Layers, valeur: data.matieres, libelle: tn("accueil.stat_matieres", data.matieres) },
  ].filter((ligne) => ligne.valeur > 0)

  if (lignes.length === 0) return null

  return (
    <Card className="animate-fade-up overflow-hidden">
      <CardContent className="flex flex-col gap-3 p-6">
        <Label className="text-sm font-semibold">{t("cd.titre")}</Label>
        <ul className="flex flex-col gap-3">
          {lignes.map(({ icone: Icone, valeur, libelle }) => (
            <li key={libelle} className="flex items-center gap-3">
              <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Icone className="size-4" />
              </span>
              <span className="text-sm text-muted-foreground">
                <strong className="font-display text-base font-semibold text-foreground">{formatAmount(valeur)}</strong>{" "}
                {libelle}
              </span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}
