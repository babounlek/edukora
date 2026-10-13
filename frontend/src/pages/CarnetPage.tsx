import { useMemo, useState } from "react"
import { Link, Navigate } from "react-router-dom"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { ArrowRight, Bookmark, BookOpen, FileText, NotebookPen, Trash2 } from "lucide-react"
import { toast } from "sonner"

import { getCarnet, saveMarqueEtude } from "@/api/endpoints"
import type { CarnetEntree } from "@/api/types"
import { COURS_SECTION_LABELS } from "@/components/CoursSection"
import { ErreurChargement } from "@/components/ErreurChargement"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { coursReaderPath, epreuveReaderPath } from "@/lib/countryPath"
import { useSeo } from "@/lib/seo"
import { capitaliserTheme } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/** "regle" → "La règle", "exercice-3" → "Exercice 3" : le nom de la section, pas son ancre. */
function libelleSection(entree: CarnetEntree): string {
  if (entree.type === "cours") {
    const label = COURS_SECTION_LABELS[entree.cle as keyof typeof COURS_SECTION_LABELS]
    if (label) return label.full
  }
  const exercice = /^exercice-(.+)$/.exec(entree.cle)
  if (exercice) return t("ed.exercice_n", { n: exercice[1].toUpperCase() })
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
  useI18n()
  useSeo({ title: t("cpt.carnet") })
  const queryClient = useQueryClient()
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const { country } = useCountry()

  const { data, isLoading, isError, refetch } = useQuery({
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
    onError: () => {
      toast.error(t("ca.erreur_retrait"))
    },
    onSuccess: (_reponse, entree) => {
      setAConfirmer(null)
      queryClient.invalidateQueries({ queryKey: ["carnet"] })
      // La page du lecteur garde son propre cache de marques pour ce document.
      queryClient.invalidateQueries({ queryKey: ["etude", entree.type === "cours" ? "cours" : "lesson", entree.slug] })
    },
  })

  // La corbeille supprime le signet ET la note : une note écrite à la main ne se récupère pas,
  // on demande donc confirmation quand l'entrée en porte une (un simple signet se refait en un clic).
  const [aConfirmer, setAConfirmer] = useState<CarnetEntree | null>(null)
  function demanderRetrait(entree: CarnetEntree) {
    if (entree.note) setAConfirmer(entree)
    else retirer.mutate(entree)
  }

  const entrees = useMemo(() => data ?? [], [data])

  if (!authLoading && !isAuthenticated) {
    return <Navigate to="/connexion" state={{ from: "/carnet" }} replace />
  }

  return (
    <div className="mx-auto max-w-3xl animate-fade-up px-4 py-10 sm:px-6">
      <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
        <NotebookPen className="size-3.5" />
        {t("cpt.carnet")}
      </p>
      <h1 className="mt-2 font-display text-3xl font-semibold tracking-tight sm:text-4xl">{t("ca.titre")}</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        {t("ca.texte")}
      </p>

      {isLoading || authLoading ? (
        <div className="mt-8 flex flex-col gap-3">
          <Skeleton className="h-28 w-full rounded-2xl" />
          <Skeleton className="h-28 w-full rounded-2xl" />
        </div>
      ) : isError ? (
        // Une panne n'est pas un carnet vide : sans ce cas, l'élève croyait avoir perdu ses notes.
        <ErreurChargement
          objet={t("ca.objet")}
          message={t("ca.message_erreur")}
          onRetry={() => refetch()}
          className="mt-8"
        />
      ) : entrees.length === 0 ? (
        <div className="mt-8 rounded-3xl border border-dashed border-border bg-card/60 p-8 text-center">
          <span className="mx-auto flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <Bookmark className="size-6" />
          </span>
          <p className="mt-4 font-display text-lg font-semibold">{t("ca.vide")}</p>
          <p className="mx-auto mt-1 max-w-sm text-sm text-muted-foreground">
            {t("ca.vide_texte")}
          </p>
          <Button asChild className="mt-5 rounded-full">
            <Link to={`/${country}`}>
              {t("ca.aller_reviser")}
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
                    {entree.type === "cours" ? t("ca.type_cours") : t("ca.type_corrige")} · {entree.matiere}
                  </p>
                  <Link to={lienSection(entree)} className="mt-0.5 block font-display text-base font-semibold leading-snug hover:text-primary">
                    {entree.titre}
                  </Link>
                  <p className="mt-0.5 flex items-center gap-1.5 text-sm text-muted-foreground">
                    {entree.signet && <Bookmark className="size-3.5 shrink-0 fill-current text-gold-text" aria-label={t("ca.garde")} />}
                    {libelleSection(entree)}
                  </p>
                </div>
                <Button
                  type="button"
                  size="icon"
                  variant="ghost"
                  className="shrink-0 text-muted-foreground hover:text-destructive"
                  aria-label={t("ca.retirer_aria")}
                  disabled={retirer.isPending}
                  onClick={() => demanderRetrait(entree)}
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
                {t("ca.rouvrir")}
                <ArrowRight className="size-3" />
              </Link>
            </li>
          ))}
        </ul>
      )}

      <Dialog open={aConfirmer !== null} onOpenChange={(ouvert) => !ouvert && setAConfirmer(null)}>
        <DialogContent>
          <DialogTitle>{t("ca.dialogue_titre")}</DialogTitle>
          <DialogDescription>
            {t("ca.dialogue_texte")}
          </DialogDescription>
          <div className="mt-5 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button variant="outline" onClick={() => setAConfirmer(null)}>
              {t("ca.garder")}
            </Button>
            <Button
              variant="destructive"
              disabled={retirer.isPending}
              onClick={() => aConfirmer && retirer.mutate(aConfirmer)}
            >
              {retirer.isPending ? t("ca.suppression") : t("ca.retirer")}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
