import { useQuery } from "@tanstack/react-query"
import { BookOpen, BrainCircuit, FileCheck2, Layers, Sparkles, type LucideIcon } from "lucide-react"

import { getCursusContenu } from "@/api/endpoints"
import { Card, CardContent } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { formatAmount } from "@/lib/utils"

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
  const { data } = useQuery({
    queryKey: ["cursus-contenu", cursusId],
    queryFn: ({ signal }) => getCursusContenu(cursusId, signal),
    staleTime: 10 * 60 * 1000,
  })

  if (!data) return null

  const lignes: Ligne[] = [
    { icone: FileCheck2, valeur: data.corriges, libelle: data.corriges > 1 ? "épreuves corrigées pas à pas" : "épreuve corrigée pas à pas" },
    { icone: BookOpen, valeur: data.cours, libelle: data.cours > 1 ? "cours et fiches de méthode" : "cours ou fiche de méthode" },
    { icone: BrainCircuit, valeur: data.questions_quiz, libelle: data.questions_quiz > 1 ? "questions de quiz pour t'entraîner" : "question de quiz pour t'entraîner" },
    ...(inclutInedit
      ? [{ icone: Sparkles, valeur: data.epreuves_inedites, libelle: data.epreuves_inedites > 1 ? "épreuves inédites, hors annales" : "épreuve inédite, hors annales" }]
      : []),
    { icone: Layers, valeur: data.matieres, libelle: data.matieres > 1 ? "matières couvertes" : "matière couverte" },
  ].filter((ligne) => ligne.valeur > 0)

  if (lignes.length === 0) return null

  return (
    <Card className="animate-fade-up overflow-hidden">
      <CardContent className="flex flex-col gap-3 p-6">
        <Label className="text-sm font-semibold">Ce que tu débloques</Label>
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
