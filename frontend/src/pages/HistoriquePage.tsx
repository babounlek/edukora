import { useEffect, useState, type ReactNode } from "react"
import { Link, useNavigate } from "react-router-dom"
import { ArrowRight, BookOpen, CheckCircle2, Crown, type LucideIcon } from "lucide-react"

import { getMyProgression, listMyTentativesInedites } from "@/api/endpoints"
import type { Progression, TentativeInediteListItem } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
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

/** Une section : titre avec pastille d'icône, contenu dans une carte discrète. */
function Section({
  icone: Icone, titre, children,
}: { icone: LucideIcon; titre: string; children: ReactNode }) {
  return (
    <section className="rounded-2xl border border-border bg-card p-4 sm:p-5">
      <h2 className="mb-3 flex items-center gap-2 font-display text-base font-semibold">
        <Icone className="size-4 text-primary" aria-hidden="true" />
        {titre}
      </h2>
      {children}
    </section>
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
      <div className="mb-6">
        <p className="mb-1 font-display text-sm italic text-primary">Activité</p>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-balance">Mon historique</h1>
        <p className="mt-2 text-muted-foreground">Tes tentatives d'épreuves inédites et ce que tu as déjà lu.</p>
      </div>

      {!charge ? (
        <div className="flex flex-col gap-4" aria-busy="true" aria-label="Chargement de l'historique">
          <Skeleton className="h-32 w-full rounded-2xl" />
          <Skeleton className="h-32 w-full rounded-2xl" />
        </div>
      ) : vide ? (
        <div className="flex flex-col items-center gap-3 rounded-3xl border border-dashed border-border bg-card/60 px-6 py-12 text-center">
          <span className="flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <BookOpen className="size-6" />
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
      ) : (
        <div className="flex flex-col gap-4">
          {tentatives.length > 0 && (
            <Section icone={Crown} titre="Tentatives d'épreuves inédites">
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
            </Section>
          )}

          {totalRead > 0 && (
            <Section icone={BookOpen} titre="Ce que j'ai lu">
              <div className="flex flex-col gap-4">
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
            </Section>
          )}
        </div>
      )}
    </div>
  )
}
