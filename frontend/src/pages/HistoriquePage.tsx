import { useEffect, useState, type ReactNode } from "react"
import { Link, useNavigate } from "react-router-dom"
import { ArrowRight, CheckCircle2, History } from "lucide-react"

import { getMyProgression, listMyTentativesInedites } from "@/api/endpoints"
import type { Progression, TentativeInediteListItem } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { formatNote } from "@/lib/notation"
import { useSeo } from "@/lib/seo"
import { coursReaderPath, epreuveReaderPath, epreuvesListPath } from "@/lib/countryPath"

// Au-delà de ce nombre, une liste passe derrière un "voir plus" - contrairement à l'ancien widget
// sur /compte (PREVIEW_COUNT=3), cette page est la destination dédiée à l'historique : on peut se
// permettre d'en montrer un peu plus avant de replier.
const PREVIEW_COUNT = 6

/** Tronque une liste à PREVIEW_COUNT éléments avec un bouton "voir plus". */
function ExpandableList<T>({
  items, renderItem,
}: { items: T[]; renderItem: (item: T) => ReactNode }) {
  const [expanded, setExpanded] = useState(false)
  const visible = expanded ? items : items.slice(0, PREVIEW_COUNT)
  return (
    <ul className="flex flex-col gap-2">
      {visible.map(renderItem)}
      {items.length > PREVIEW_COUNT && (
        <li>
          <button
            type="button"
            onClick={() => setExpanded((e) => !e)}
            className="text-sm font-medium text-primary hover:underline"
          >
            {expanded ? "Voir moins" : `Voir les ${items.length - PREVIEW_COUNT} autres`}
          </button>
        </li>
      )}
    </ul>
  )
}

function Resume({ valeur, libelle }: { valeur: string; libelle: string }) {
  return (
    <div className="rounded-2xl border border-border/70 bg-background/70 px-3 py-3 text-center backdrop-blur-sm">
      <dd className="font-display text-2xl font-semibold tabular-nums leading-none sm:text-3xl">{valeur}</dd>
      <dt className="mt-1.5 text-xs leading-tight text-muted-foreground">{libelle}</dt>
    </div>
  )
}

function ListeTentatives({ tentatives }: { tentatives: TentativeInediteListItem[] }) {
  return (
    <div className="rounded-2xl border border-border bg-card p-4 sm:p-5">
      <ExpandableList
        items={tentatives}
        renderItem={(tentative) => (
          <li key={tentative.id}>
            <Link
              to={
                tentative.submitted_at
                  ? `/inedit/tentative/${tentative.id}/resultat`
                  : `/inedit/tentative/${tentative.id}`
              }
              className="flex items-center justify-between gap-3 rounded-xl border border-border bg-background/60 px-3.5 py-2.5 text-sm transition-colors hover:border-primary/40"
            >
              <span className="flex min-w-0 flex-col">
                <span className="truncate font-medium">{tentative.epreuve_titre}</span>
                <span className="text-xs text-muted-foreground">
                  {tentative.cursus_display} · {new Date(tentative.started_at).toLocaleDateString("fr-FR")}
                </span>
              </span>
              {tentative.submitted_at ? (
                <Badge variant={tentative.score_obtenu !== null && tentative.score_obtenu >= 50 ? "success" : "outline"}>
                  {tentative.note_obtenue !== null && tentative.bareme_snapshot !== null
                    ? formatNote(tentative.note_obtenue, tentative.bareme_snapshot)
                    : `${tentative.score_obtenu}%`}
                </Badge>
              ) : (
                <Badge variant="outline">En cours</Badge>
              )}
            </Link>
          </li>
        )}
      />
    </div>
  )
}

function ListeLectures({ progression }: { progression: Progression }) {
  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-border bg-card p-4 sm:p-5">
      {progression.lessons.length > 0 && (
        <div>
          <p className="mb-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">Épreuves</p>
          <ExpandableList
            items={progression.lessons}
            renderItem={(epreuve) => (
              <li key={epreuve.id}>
                <Link
                  // progression.lessons vient de getMyProgression() (endpoint access, non
                  // modifié) - toujours une Lesson classique.
                  to={epreuveReaderPath(epreuve.subject.country.code.toLowerCase(), epreuve.slug as string)}
                  className="flex items-center gap-2 rounded-xl border border-border bg-background/60 px-3.5 py-2 text-sm transition-colors hover:border-primary/40"
                >
                  <CheckCircle2 className="size-3.5 shrink-0 text-success" />
                  <span className="truncate">{epreuve.title}</span>
                </Link>
              </li>
            )}
          />
        </div>
      )}

      {progression.cours.length > 0 && (
        <div>
          <p className="mb-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">Cours</p>
          <ExpandableList
            items={progression.cours}
            renderItem={(cours) => (
              <li key={cours.id}>
                <Link
                  to={coursReaderPath(cours.slug)}
                  className="flex items-center gap-2 rounded-xl border border-border bg-background/60 px-3.5 py-2 text-sm transition-colors hover:border-primary/40"
                >
                  <CheckCircle2 className="size-3.5 shrink-0 text-success" />
                  <span className="truncate">{cours.titre}</span>
                </Link>
              </li>
            )}
          />
        </div>
      )}
    </div>
  )
}

export function HistoriquePage() {
  useSeo({ title: "Mon historique" })

  const { isAuthenticated, isLoading } = useAuth()
  const { country } = useCountry()
  const navigate = useNavigate()
  const [progression, setProgression] = useState<Progression | null>(null)
  const [tentatives, setTentatives] = useState<TentativeInediteListItem[] | null>(null)

  useEffect(() => {
    if (isLoading) return
    if (!isAuthenticated) {
      navigate("/connexion", { state: { from: "/historique" } })
      return
    }
    getMyProgression().then(setProgression)
    listMyTentativesInedites().then(setTentatives)
  }, [isLoading, isAuthenticated, navigate])

  if (isLoading) return null

  const totalRead = (progression?.lessons.length ?? 0) + (progression?.cours.length ?? 0)
  const charge = progression !== null && tentatives !== null
  const vide = charge && totalRead === 0 && tentatives.length === 0

  return (
    <div className="mx-auto max-w-3xl animate-fade-up px-4 py-6 sm:py-10">
      <section className="relative mb-6 overflow-hidden rounded-3xl border border-border bg-gradient-to-br from-primary/[0.09] via-primary/[0.03] to-gold/[0.06] p-5 sm:p-8">
        <History aria-hidden className="pointer-events-none absolute -bottom-6 -right-4 hidden size-44 rotate-[-12deg] text-primary/[0.07] sm:block" />
        <div className="relative">
          <p className="mb-2 font-display text-sm italic text-primary">Activité</p>
          <h1 className="font-display text-3xl font-semibold tracking-tight text-balance sm:text-4xl">Mon historique</h1>
          <p className="mt-2 max-w-xl text-muted-foreground">Tes tentatives d'épreuves inédites et ce que tu as déjà lu.</p>

          {charge && !vide && (
            <dl className="mt-5 grid grid-cols-3 gap-2 sm:gap-3">
              <Resume valeur={String(tentatives.length)} libelle={tentatives.length > 1 ? "tentatives" : "tentative"} />
              <Resume valeur={String(progression?.lessons.length ?? 0)} libelle="épreuves lues" />
              <Resume valeur={String(progression?.cours.length ?? 0)} libelle="cours lus" />
            </dl>
          )}
        </div>
      </section>

      {!charge ? (
        <div className="flex flex-col gap-4" aria-busy="true" aria-label="Chargement de l'historique">
          <Skeleton className="h-32 w-full rounded-3xl" />
          <Skeleton className="h-32 w-full rounded-3xl" />
        </div>
      ) : vide ? (
        <div className="flex flex-col items-center gap-3 rounded-3xl border border-dashed border-border bg-card/60 px-6 py-12 text-center">
          <span className="flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <History className="size-6" />
          </span>
          <p className="font-display text-lg font-semibold">Rien à afficher pour l'instant</p>
          <p className="max-w-sm text-sm text-muted-foreground">
            Tes tentatives d'épreuves inédites et tes lectures apparaîtront ici au fil de tes révisions.
          </p>
          <Button asChild className="mt-1 rounded-full">
            <Link to={epreuvesListPath(country)}>
              Voir les épreuves
              <ArrowRight className="size-3.5" />
            </Link>
          </Button>
        </div>
      ) : tentatives.length > 0 && totalRead > 0 ? (
        <Tabs defaultValue="tentatives">
          <TabsList>
            <TabsTrigger value="tentatives">Tentatives ({tentatives.length})</TabsTrigger>
            <TabsTrigger value="lectures">Lectures ({totalRead})</TabsTrigger>
          </TabsList>
          <TabsContent value="tentatives">
            <ListeTentatives tentatives={tentatives} />
          </TabsContent>
          <TabsContent value="lectures">
            <ListeLectures progression={progression} />
          </TabsContent>
        </Tabs>
      ) : tentatives.length > 0 ? (
        <ListeTentatives tentatives={tentatives} />
      ) : (
        <ListeLectures progression={progression} />
      )}
    </div>
  )
}
