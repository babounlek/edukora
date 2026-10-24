import { useEffect, useState, type ReactNode } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useInfiniteQuery, useQuery } from "@tanstack/react-query"
import { BookOpen, CheckCircle2, Crown, History, ListChecks, Play, RotateCcw } from "lucide-react"

import { getMyProgression, listMyTentativesInedites, listQuizHistorique } from "@/api/endpoints"
import type { Progression, QuizEnCoursItem, QuizHistoriqueItem, TentativeInediteListItem } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { EnteteCompte, EtatVide, Section } from "@/components/CompteSection"
import { ErreurChargement } from "@/components/ErreurChargement"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { formatDureeEcoulee } from "@/lib/duration"
import { useQuizEnCours } from "@/lib/quizEnCours"
import { formatNote } from "@/lib/notation"
import { useSeo } from "@/lib/seo"
import { coursReaderPath, epreuveReaderPath } from "@/lib/countryPath"
import { localeCourante, t, useI18n } from "@/lib/i18n"
import { traduireLibelleSerie } from "@/lib/cursus"

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
            {expanded ? t("hi.voir_moins") : t("hi.voir_autres", { n: items.length - PREVIEW_COUNT })}
          </button>
        </li>
      )}
    </ul>
  )
}

// Même barre que partout ailleurs dans l'app (voir quiz.services.SEUIL_MAITRISE et lib/maitrise.ts).
const SEUIL_REUSSITE = 70

/**
 * Les tentatives interrompues, AVANT l'historique : reprendre rouvre la même session là où l'élève
 * s'était arrêté (ce n'est ni consulter une tentative terminée, ni la rejouer).
 */
function QuizEnCours({ enCours }: { enCours: QuizEnCoursItem[] }) {
  return (
    <ul className="flex flex-col gap-2" aria-label={t("hq.en_cours")}>
      {enCours.map((q) => (
        <li key={q.id}>
          <Link
            to={`/quiz/session/${q.id}`}
            className="flex items-center justify-between gap-3 rounded-xl border border-primary/40 bg-primary/5 px-3.5 py-2.5 text-sm transition-colors hover:border-primary"
          >
            <span className="flex min-w-0 flex-col">
              <span className="flex min-w-0 items-center gap-1.5 font-medium">
                <Play className="size-3.5 shrink-0 text-primary" aria-hidden="true" />
                <span className="truncate">{q.subject_label || q.theme || t("hq.quiz_sans_titre")}</span>
              </span>
              <span className="text-xs text-muted-foreground">
                {traduireLibelleSerie(q.cursus_display)} · {t("hq.repondues", { repondues: q.nb_repondues, total: q.total_questions })}
              </span>
            </span>
            <span className="shrink-0 font-medium text-primary">
              {q.a_terminer ? t("quiz_en_cours.terminer") : t("hq.reprendre")}
            </span>
          </Link>
        </li>
      ))}
    </ul>
  )
}

function ContenuQuiz({
  quiz, enCours, aSuivante, chargeSuivante, onVoirPlus,
}: {
  quiz: QuizHistoriqueItem[]
  enCours: QuizEnCoursItem[]
  aSuivante: boolean
  chargeSuivante: boolean
  onVoirPlus: () => void
}) {
  return (
    <div className="flex flex-col gap-4">
      {enCours.length > 0 && (
        <div>
          {quiz.length > 0 && (
            <p className="mb-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">{t("hq.en_cours")}</p>
          )}
          <QuizEnCours enCours={enCours} />
        </div>
      )}
      {quiz.length > 0 && (
        <div>
          {enCours.length > 0 && (
            <p className="mb-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">{t("hq.termines")}</p>
          )}
          <ListeQuiz quiz={quiz} aSuivante={aSuivante} chargeSuivante={chargeSuivante} onVoirPlus={onVoirPlus} />
        </div>
      )}
    </div>
  )
}

function ListeQuiz({
  quiz, aSuivante, chargeSuivante, onVoirPlus,
}: { quiz: QuizHistoriqueItem[]; aSuivante: boolean; chargeSuivante: boolean; onVoirPlus: () => void }) {
  return (
    <ul className="flex flex-col gap-2">
      {quiz.map((q) => {
        const details = [
          traduireLibelleSerie(q.cursus_display),
          new Date(q.completed_at).toLocaleDateString(localeCourante()),
          q.duree_secondes !== null ? formatDureeEcoulee(q.duree_secondes) : null,
        ].filter(Boolean)
        return (
          <li key={q.id}>
            <Link
              to={`/historique/quiz/${q.id}`}
              className="flex items-center justify-between gap-3 rounded-xl border border-border bg-background/60 px-3.5 py-2.5 text-sm transition-colors hover:border-primary/40"
            >
              <span className="flex min-w-0 flex-col">
                <span className="flex min-w-0 items-center gap-1.5 font-medium">
                  <span className="truncate">{q.subject_label || q.theme || t("hq.quiz_sans_titre")}</span>
                  {q.rejeu_de !== null && (
                    <span className="inline-flex shrink-0 items-center gap-1 rounded-full bg-muted px-1.5 py-0.5 text-[11px] font-normal text-muted-foreground">
                      <RotateCcw className="size-3" aria-hidden="true" />
                      {t("hq.rejeu")}
                    </span>
                  )}
                </span>
                <span className="text-xs text-muted-foreground">
                  {details.join(" · ")}
                  {q.nb_tentatives > 1 && ` · ${t("hq.tentative_n", { n: q.numero_tentative, total: q.nb_tentatives })}`}
                </span>
              </span>
              <Badge variant={q.pourcentage >= SEUIL_REUSSITE ? "success" : "outline"}>
                {q.score}/{q.total_questions}
              </Badge>
            </Link>
          </li>
        )
      })}
      {aSuivante && (
        <li>
          <button
            type="button"
            onClick={onVoirPlus}
            disabled={chargeSuivante}
            className="text-sm font-medium text-primary hover:underline disabled:opacity-60"
          >
            {chargeSuivante ? t("matieres.chargement") : t("hq.voir_plus")}
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
                {traduireLibelleSerie(tentative.cursus_display)} · {new Date(tentative.started_at).toLocaleDateString(localeCourante())}
              </span>
            </span>
            {tentative.submitted_at ? (
              <Badge variant={tentative.score_obtenu !== null && tentative.score_obtenu >= 50 ? "success" : "outline"}>
                {tentative.note_obtenue !== null && tentative.bareme_snapshot !== null
                  ? formatNote(tentative.note_obtenue, tentative.bareme_snapshot)
                  : `${tentative.score_obtenu}%`}
              </Badge>
            ) : (
              <Badge variant="outline">{t("statut.en_cours")}</Badge>
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
          <p className="mb-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">{t("nav.epreuves")}</p>
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
          <p className="mb-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">{t("nav.cours")}</p>
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
  useI18n()
  useSeo({ title: t("compte.historique") })

  const { isAuthenticated, isLoading, user } = useAuth()
  const navigate = useNavigate()
  // Les deux réponses sont filtrées côté serveur sur le cursus préparé actuellement
  // (voir access.views.my_progression/inedit.views.list_my_tentatives_inedites) - sans
  // cette dépendance dans la clé, basculer d'examen (voir le sélecteur dans Header.tsx)
  // depuis cette page laissait l'historique de l'ancien cursus affiché jusqu'au prochain
  // aller-retour de page. staleTime 0 : un historique ne doit jamais être périmé.
  const cursusId = user?.cursus_prepare?.id

  useEffect(() => {
    if (isLoading) return
    if (!isAuthenticated) navigate("/connexion", { state: { from: "/historique" } })
  }, [isLoading, isAuthenticated, navigate])

  const actif = !isLoading && isAuthenticated
  const progressionQuery = useQuery({
    queryKey: ["progression", cursusId ?? null],
    queryFn: ({ signal }) => getMyProgression(signal),
    enabled: actif,
    staleTime: 0,
  })
  const tentativesQuery = useQuery({
    queryKey: ["inedit-tentatives", cursusId ?? null],
    queryFn: () => listMyTentativesInedites(),
    enabled: actif,
    staleTime: 0,
  })
  // Les tentatives de quiz sont filtrées côté serveur sur le profil actif ; paginées (voir
  // quiz.historique) : « Voir plus » charge la page suivante sans rien recharger.
  const quizQuery = useInfiniteQuery({
    queryKey: ["quiz-historique", user?.profil_actif.id ?? null],
    queryFn: ({ pageParam, signal }) => listQuizHistorique(pageParam, signal),
    initialPageParam: 1,
    getNextPageParam: (derniere, pages) => (derniere.next ? pages.length + 1 : undefined),
    enabled: actif,
    staleTime: 0,
  })
  const progression = progressionQuery.data ?? null
  const tentatives = tentativesQuery.data ?? null
  const quiz = quizQuery.data?.pages.flatMap((p) => p.results) ?? []
  const quizTotal = quizQuery.data?.pages[0]?.count ?? 0
  // Accessoire : si la liste des quiz en cours ne répond pas, l'historique reste utile tel quel.
  const enCours = useQuizEnCours().data ?? []
  const nbQuiz = quizTotal + enCours.length

  if (isLoading) return null

  const totalRead = (progression?.lessons.length ?? 0) + (progression?.cours.length ?? 0)
  const charge = progression !== null && tentatives !== null && quizQuery.data !== undefined
  const enErreur = progressionQuery.isError || tentativesQuery.isError || quizQuery.isError
  const vide = charge && totalRead === 0 && tentatives.length === 0 && nbQuiz === 0
  const contenuQuiz = (
    <ContenuQuiz
      quiz={quiz}
      enCours={enCours}
      aSuivante={quizQuery.hasNextPage}
      chargeSuivante={quizQuery.isFetchingNextPage}
      onVoirPlus={() => quizQuery.fetchNextPage()}
    />
  )
  // Un onglet par source non vide ; une seule source se montre directement, sans onglet.
  const sources = charge
    ? [
        nbQuiz > 0 && { cle: "quiz", libelle: t("hq.onglet", { n: nbQuiz }), titre: t("hq.titre"), icone: ListChecks, contenu: contenuQuiz },
        tentatives.length > 0 && {
          cle: "tentatives", libelle: t("hi.tentatives_onglet", { n: tentatives.length }), titre: t("hi.tentatives_titre"),
          icone: Crown, contenu: <ContenuTentatives tentatives={tentatives} />,
        },
        totalRead > 0 && {
          cle: "lectures", libelle: t("hi.lectures_onglet", { n: totalRead }), titre: t("hi.lu"),
          icone: BookOpen, contenu: <ContenuLectures progression={progression} />,
        },
      ].filter((s) => s !== false)
    : []

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:py-10 sm:px-6">
      <EnteteCompte
        icone={History}
        titre={t("compte.historique")}
        sousTitre={t("hi.sous_titre")}
      />

      {enErreur && !charge ? (
        // Sans ce cas, une requête en échec laissait « Chargement… » à l'écran pour toujours.
        <ErreurChargement
          objet={t("hi.objet")}
          compact
          onRetry={() => {
            if (progressionQuery.isError) progressionQuery.refetch()
            if (tentativesQuery.isError) tentativesQuery.refetch()
            if (quizQuery.isError) quizQuery.refetch()
          }}
        />
      ) : !charge ? (
        <Section icone={History} titre={t("hi.activite")}>
          <p className="text-sm text-muted-foreground">{t("matieres.chargement")}</p>
        </Section>
      ) : vide ? (
        <Section icone={History} titre={t("hi.activite")}>
          <EtatVide texte={t("hq.vide")} lien="/quiz" libelleLien={t("hq.vide_lien")} />
        </Section>
      ) : sources.length > 1 ? (
        <Tabs defaultValue={sources[0].cle}>
          <TabsList>
            {sources.map((s) => (
              <TabsTrigger key={s.cle} value={s.cle}>{s.libelle}</TabsTrigger>
            ))}
          </TabsList>
          {sources.map((s) => (
            <TabsContent key={s.cle} value={s.cle}>
              <div className="rounded-2xl border border-border bg-card p-4 sm:p-5">{s.contenu}</div>
            </TabsContent>
          ))}
        </Tabs>
      ) : (
        <Section icone={sources[0].icone} titre={sources[0].titre}>
          {sources[0].contenu}
        </Section>
      )}
    </div>
  )
}
