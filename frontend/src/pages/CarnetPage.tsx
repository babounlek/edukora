import { useMemo } from "react"
import { Link, Navigate } from "react-router-dom"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { ArrowRight, Bookmark, BookOpen, FileText, NotebookPen, Trash2 } from "lucide-react"

import { getCarnet, saveMarqueEtude } from "@/api/endpoints"
import type { CarnetEntree } from "@/api/types"
import { COURS_SECTION_LABELS } from "@/components/CoursSection"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { coursReaderPath, epreuveReaderPath } from "@/lib/countryPath"
import { useSeo } from "@/lib/seo"
import { capitaliserTheme } from "@/lib/utils"

/** "regle" → "La règle", "exercice-3" → "Exercice 3" : le nom de la section, pas son ancre. */
function libelleSection(entree: CarnetEntree): string {
  if (entree.type === "cours") {
    const label = COURS_SECTION_LABELS[entree.cle as keyof typeof COURS_SECTION_LABELS]
    if (label) return label.full
  }
  const exercice = /^exercice-(.+)$/.exec(entree.cle)
  if (exercice) return `Exercice ${exercice[1].toUpperCase()}`
  return capitaliserTheme(entree.cle.replace(/-/g, " "))
}

function lienSection(entree: CarnetEntree): string {
  const base = entree.type === "cours" ? coursReaderPath(entree.slug) : epreuveReaderPath(entree.country, entree.slug)
  return `${base}#${entree.cle}`
}

/**
 * Le carnet de l'élève : ses signets et ses notes, tous documents confondus, du plus
 * récent au plus ancien - chaque entrée rouvre la section exacte.
 *
 * C'est ce qui donne un sens aux notes : une remarque écrite au fond d'un cours qu'on ne
 * rouvrira jamais ne sert à personne. Regroupées ici, elles deviennent la fiche de
 * révision que l'élève s'est écrite lui-même.
 */
export function CarnetPage() {
  useSeo({ title: "Mon carnet" })
  const queryClient = useQueryClient()
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const { country } = useCountry()

  const { data, isLoading } = useQuery({
    queryKey: ["carnet"],
    queryFn: ({ signal }) => getCarnet(signal),
    enabled: isAuthenticated,
  })

  const retirer = useMutation({
    mutationFn: (entree: CarnetEntree) =>
      saveMarqueEtude(
        { type: entree.type === "cours" ? "cours" : "lesson", slug: entree.slug },
        entree.cle,
        { signet: false, note: "" },
      ),
    onSuccess: (_reponse, entree) => {
      queryClient.invalidateQueries({ queryKey: ["carnet"] })
      // La page du lecteur garde son propre cache de marques pour ce document.
      queryClient.invalidateQueries({ queryKey: ["etude", entree.type === "cours" ? "cours" : "lesson", entree.slug] })
    },
  })

  const entrees = useMemo(() => data ?? [], [data])

  if (!authLoading && !isAuthenticated) {
    return <Navigate to="/connexion" state={{ from: "/carnet" }} replace />
  }

  return (
    <div className="mx-auto max-w-3xl animate-fade-up px-4 py-10 sm:px-6">
      <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
        <NotebookPen className="size-3.5" />
        Mon carnet
      </p>
      <h1 className="mt-2 font-display text-3xl font-semibold tracking-tight sm:text-4xl">Ce que tu as gardé</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        Tes signets et tes notes, tous cours et épreuves confondus. Chaque entrée te ramène à l'endroit exact.
      </p>

      {isLoading || authLoading ? (
        <div className="mt-8 flex flex-col gap-3">
          <Skeleton className="h-28 w-full rounded-2xl" />
          <Skeleton className="h-28 w-full rounded-2xl" />
        </div>
      ) : entrees.length === 0 ? (
        <div className="mt-8 rounded-3xl border border-dashed border-border bg-card/60 p-8 text-center">
          <span className="mx-auto flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <Bookmark className="size-6" />
          </span>
          <p className="mt-4 font-display text-lg font-semibold">Ton carnet est vide pour l'instant</p>
          <p className="mx-auto mt-1 max-w-sm text-sm text-muted-foreground">
            En lisant un cours ou un corrigé, garde une section pour plus tard ou écris-toi une note : tu la retrouveras ici.
          </p>
          <Button asChild className="mt-5 rounded-full">
            <Link to={`/${country}`}>
              Aller réviser
              <ArrowRight />
            </Link>
          </Button>
        </div>
      ) : (
        <ul className="mt-8 flex flex-col gap-3">
          {entrees.map((entree) => (
            <li
              key={`${entree.type}-${entree.slug}-${entree.cle}`}
              className="group rounded-2xl border border-border bg-card p-4 transition-colors hover:border-primary/40 sm:p-5"
            >
              <div className="flex items-start gap-3">
                <span className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                  {entree.type === "cours" ? <BookOpen className="size-4" /> : <FileText className="size-4" />}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="text-xs text-muted-foreground">
                    {entree.type === "cours" ? "Cours" : "Corrigé"} · {entree.matiere}
                  </p>
                  <Link to={lienSection(entree)} className="mt-0.5 block font-display text-base font-semibold leading-snug hover:text-primary">
                    {entree.titre}
                  </Link>
                  <p className="mt-0.5 flex items-center gap-1.5 text-sm text-muted-foreground">
                    {entree.signet && <Bookmark className="size-3.5 shrink-0 fill-current text-gold" aria-label="Gardé" />}
                    {libelleSection(entree)}
                  </p>
                </div>
                <Button
                  type="button"
                  size="icon"
                  variant="ghost"
                  className="shrink-0 text-muted-foreground hover:text-destructive"
                  aria-label="Retirer du carnet"
                  disabled={retirer.isPending}
                  onClick={() => retirer.mutate(entree)}
                >
                  <Trash2 className="size-4" />
                </Button>
              </div>
              {entree.note && (
                <p className="mt-3 whitespace-pre-wrap rounded-xl border border-gold/30 bg-gold/[0.06] px-4 py-3 text-sm leading-relaxed">
                  {entree.note}
                </p>
              )}
              <Link
                to={lienSection(entree)}
                className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
              >
                Rouvrir la section
                <ArrowRight className="size-3" />
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
