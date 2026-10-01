import { useEffect, useState, type ReactNode } from "react"
import { Link, useNavigate } from "react-router-dom"
import { BookOpen, CheckCircle2, Crown, History } from "lucide-react"

import { getMyProgression, listMyTentativesInedites } from "@/api/endpoints"
import type { Progression, TentativeInediteListItem } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { EnteteCompte, EtatVide, Section } from "@/components/CompteSection"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { formatNote } from "@/lib/notation"
import { useSeo } from "@/lib/seo"
import { coursReaderPath, epreuveReaderPath } from "@/lib/countryPath"

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

function ContenuTentatives({ tentatives }: { tentatives: TentativeInediteListItem[] }) {
  return (
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
  )
}

function ContenuLectures({ progression }: { progression: Progression }) {
  return (
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
  )
}

export function HistoriquePage() {
  useSeo({ title: "Mon historique" })

  const { isAuthenticated, isLoading, user } = useAuth()
  const navigate = useNavigate()
  const [progression, setProgression] = useState<Progression | null>(null)
  const [tentatives, setTentatives] = useState<TentativeInediteListItem[] | null>(null)
  // Les deux réponses sont filtrées côté serveur sur le cursus préparé actuellement
  // (voir access.views.my_progression/inedit.views.list_my_tentatives_inedites) - sans
  // cette dépendance, basculer d'examen (voir le sélecteur dans Header.tsx) depuis
  // cette page laissait l'historique de l'ancien cursus affiché jusqu'au prochain
  // aller-retour de page.
  const cursusId = user?.cursus_prepare?.id

  useEffect(() => {
    if (isLoading) return
    if (!isAuthenticated) {
      navigate("/connexion", { state: { from: "/historique" } })
      return
    }
    getMyProgression().then(setProgression)
    listMyTentativesInedites().then(setTentatives)
  }, [isLoading, isAuthenticated, navigate, cursusId])

  if (isLoading) return null

  const totalRead = (progression?.lessons.length ?? 0) + (progression?.cours.length ?? 0)
  const charge = progression !== null && tentatives !== null
  const vide = charge && totalRead === 0 && tentatives.length === 0

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:py-10 sm:px-6">
      <EnteteCompte
        icone={History}
        titre="Mon historique"
        sousTitre="Tes tentatives d'épreuves inédites et ce que tu as déjà lu."
      />

      {!charge ? (
        <Section icone={History} titre="Activité">
          <p className="text-sm text-muted-foreground">Chargement…</p>
        </Section>
      ) : vide ? (
        <Section icone={History} titre="Activité">
          <EtatVide
            texte="Rien à afficher pour l'instant. Tes tentatives d'épreuves inédites et tes lectures apparaîtront ici au fil de tes révisions."
            lien="/tarifs"
            libelleLien="Voir les formules"
          />
        </Section>
      ) : tentatives.length > 0 && totalRead > 0 ? (
        <Tabs defaultValue="tentatives">
          <TabsList>
            <TabsTrigger value="tentatives">Tentatives ({tentatives.length})</TabsTrigger>
            <TabsTrigger value="lectures">Lectures ({totalRead})</TabsTrigger>
          </TabsList>
          <TabsContent value="tentatives">
            <div className="rounded-2xl border border-border bg-card p-4 sm:p-5">
              <ContenuTentatives tentatives={tentatives} />
            </div>
          </TabsContent>
          <TabsContent value="lectures">
            <div className="rounded-2xl border border-border bg-card p-4 sm:p-5">
              <ContenuLectures progression={progression} />
            </div>
          </TabsContent>
        </Tabs>
      ) : tentatives.length > 0 ? (
        <Section icone={Crown} titre="Tentatives d'épreuves inédites">
          <ContenuTentatives tentatives={tentatives} />
        </Section>
      ) : (
        <Section icone={BookOpen} titre="Ce que j'ai lu">
          <ContenuLectures progression={progression} />
        </Section>
      )}
    </div>
  )
}
