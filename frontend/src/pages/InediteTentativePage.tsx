import { useCallback, useEffect, useRef, useState } from "react"
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom"
import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import rehypeRaw from "rehype-raw"
import { toast } from "sonner"
import { ArrowLeft, Check, CloudOff, Eye, EyeOff, FileDown, FileText, Flag, Info, Timer, X } from "lucide-react"

import { answerTentativeQuestion, downloadSujetPdf } from "@/api/endpoints"
import type { NoterTentativeQuestionParams } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { NotationResume, TentativeInedite, TentativeInediteQuestion } from "@/api/types"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { BandeauNotation } from "@/components/inedit/BandeauNotation"
import { CausePerte } from "@/components/inedit/CausePerte"
import { BoutonTraitee } from "@/components/inedit/BoutonTraitee"
import { ChoixModeEpreuve } from "@/components/inedit/ChoixModeEpreuve"
import { DialogueModeExamen, DialogueQuitter, DialogueTerminer } from "@/components/inedit/DialoguesEpreuve"
import { BoutonPalette, PaletteQuestions, type EtatPastille, type GroupePalette } from "@/components/inedit/PaletteQuestions"
import { GrilleNotation } from "@/components/inedit/GrilleNotation"
import { messageAlerte, reperesFranchis, type CleAlerte } from "@/lib/alertesTemps"
import { formatDuration } from "@/lib/duration"
import { definirModeExamen } from "@/lib/modeExamen"
import { estANoter, formatNote, formatPoints } from "@/lib/notation"
import { trackEvent } from "@/lib/analytics"
import { useSeo } from "@/lib/seo"
import { cn } from "@/lib/utils"
import { apiPour, cheminResultat, cheminRetour, type SourceEpreuve } from "@/lib/apiEpreuve"
import { mots, uniteDe } from "@/lib/vocabulaire"

/** Rendu inline (pas de <p> bloc) pour le texte d'un choix QCM, qui peut contenir du LaTeX. */
function ChoixText({ texte }: { texte: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkMath]}
      rehypePlugins={[rehypeRaw, rehypeKatex]}
      components={{ p: ({ children }) => <>{children}</> }}
    >
      {texte}
    </ReactMarkdown>
  )
}

interface FlatQuestion extends TentativeInediteQuestion {
  numero_exercice: string
  points_exercice: string
  // Pile de repères de groupe de l'exercice parent (voir TentativeInediteExercice.
  // groupes) - un seul en-tête par exercice, affiché quand isNewExercice (voir plus
  // bas). Distinct de `groupe_local` (hérité de TentativeInediteQuestion via le spread
  // ci-dessous) : celui-ci peut changer PLUSIEURS fois au sein d'un même exercice, pour
  // scinder ses questions en sous-sections successives (ex. "Vérification des savoirs"
  // puis "Vérification des savoir-faire") - voir isNewGroupeLocal plus bas.
  groupes: string[]
  // Renommé (et non `enonce_intro_markdown`) une fois aplati sur la question : à ce
  // niveau, plus rien ne rappelle qu'il appartient à l'exercice, et le confondre avec
  // l'énoncé de la question elle-même le ferait afficher autant de fois qu'il y a de
  // questions - voir le rendu conditionné par isNewExercice plus bas.
  exercice_intro_markdown: string
}

function flattenQuestions(tentative: TentativeInedite): FlatQuestion[] {
  return tentative.exercices.flatMap((exercice) =>
    exercice.questions.map((question) => ({
      ...question,
      numero_exercice: exercice.numero_exercice,
      points_exercice: exercice.points,
      groupes: exercice.groupes,
      exercice_intro_markdown: exercice.enonce_intro_markdown,
    })),
  )
}

function repere(question: FlatQuestion, unite: "question" | "exercice") {
  return {
    id: question.id,
    label: unite === "exercice" ? `Exercice ${question.numero_exercice}` : `Ex. ${question.numero_exercice} · Q${question.numero}`,
  }
}

function scrollToQuestion(questionId: number) {
  const cible = document.getElementById(`question-${questionId}`)
  if (!cible) return
  const reduit = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches
  cible.scrollIntoView({ behavior: reduit ? "auto" : "smooth", block: "start" })
}

const REPONSE_VIDE = { reponse_choisie: "", resultat_declare: "" }

/** Avant la copie rendue : traitée ou pas. Après : à noter, notée, ou non traitée. */
function etatPastille(question: FlatQuestion, rendue: boolean): EtatPastille {
  if (!question.traitee) return "a_traiter"
  if (!rendue) return "traitee"
  return estANoter(question) ? "a_noter" : "notee"
}

export function InediteTentativePage({ source = "inedit" }: { source?: SourceEpreuve }) {
  const api = apiPour(source)

  const { id } = useParams<{ id: string }>()
  const [searchParams] = useSearchParams()

  const [tentative, setTentative] = useState<TentativeInedite | null>(null)
  // Le titre de l'onglet nomme l'épreuve : avec plusieurs onglets ouverts, « Épreuve inédite » seul ne dit rien.
  useSeo({ title: tentative?.epreuve_titre ?? (source === "officielle" ? "Simulation d'épreuve" : "Épreuve inédite") })
  // Ce que la page compte et note d'un bloc : des questions, ou des exercices pour une annale.
  const unite = uniteDe(tentative?.granularite)
  const m = mots(unite)
  const [questions, setQuestions] = useState<FlatQuestion[]>([])
  const [notation, setNotation] = useState<NotationResume | null>(null)
  const [loadError, setLoadError] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [remainingSeconds, setRemainingSeconds] = useState<number | null>(null)
  const [showCorrection, setShowCorrection] = useState(false)
  const [flaggedIds, setFlaggedIds] = useState<Set<number>>(new Set())
  const [startingExam, setStartingExam] = useState(false)
  const [downloadingSujet, setDownloadingSujet] = useState(false)
  const [finishing, setFinishing] = useState(false)
  const [terminerOuvert, setTerminerOuvert] = useState(false)
  // Mode à confirmer avant de lancer le chrono (jamais lancé d'un simple clic : il ne s'arrête plus).
  const [modeAConfirmer, setModeAConfirmer] = useState<"examen" | "papier" | null>(null)
  const [rendueAutomatiquement, setRendueAutomatiquement] = useState(false)
  // L'élève a choisi « entraînement libre » sur le briefing : on ne le lui repropose plus.
  const [libreChoisi, setLibreChoisi] = useState(false)
  const [quitterOuvert, setQuitterOuvert] = useState(false)
  // Dernier repère de temps annoncé, relu par les lecteurs d'écran (région role="status").
  const [annonce, setAnnonce] = useState("")
  // Changements faits hors connexion, envoyés au retour du réseau.
  const [enAttente, setEnAttente] = useState(0)
  const [courante, setCourante] = useState<number | null>(null)
  const navigate = useNavigate()

  // Dernière requête d'écriture émise par question : deux clics rapprochés sur « + »
  // produisent deux requêtes, et une réponse tardive ne doit jamais écraser la plus récente.
  const sequences = useRef(new Map<number, number>())
  const defilementInitial = useRef(false)
  // Un seul refetch de verrouillage à la fois : si l'horloge du serveur retarde sur celle du
  // navigateur, la tentative n'est pas encore verrouillée à 00:00 - sans ce garde, chaque
  // réponse relancerait l'effet ci-dessous et martèlerait l'API.
  const verrouillageDemande = useRef(false)
  const annonces = useRef(new Set<CleAlerte>())
  const chargementInitial = useRef(false)
  const repriseSignalee = useRef(false)
  const traiteesRef = useRef(0)
  const totalRef = useRef(0)
  // Dernier envoi tenté par question quand le réseau était coupé (le dernier gagne).
  const fileHorsLigne = useRef(new Map<number, NoterTentativeQuestionParams>())

  const charger = useCallback((data: TentativeInedite) => {
    setTentative(data)
    setQuestions(flattenQuestions(data))
    setNotation(data.notation)
  }, [])

  useEffect(() => {
    if (!id) return
    api.charger(Number(id))
      .then((data) => {
        charger(data)
        chargementInitial.current = true
        setFlaggedIds(new Set(data.questions_marquees))
        setShowCorrection(data.submitted_at !== null)
        try {
          setLibreChoisi(sessionStorage.getItem(`inedit-libre-${data.id}`) === "1")
        } catch {
          // stockage indisponible : le briefing se reproposera, sans gravité
        }
      })
      .catch((err) => {
        setLoadError(err instanceof ApiError ? err.message : "Impossible de charger cette épreuve.")
      })
  }, [id, charger])

  // Chrono du mode examen - recalcule depuis un timestamp fixe (deadline) à chaque
  // tick plutôt que de décrémenter un compteur : robuste au throttling d'un onglet en
  // arrière-plan (même technique que LoginPage.tsx pour le cooldown de renvoi d'OTP).
  // Reclé sur exam_mode_started_at (pas started_at) : un chrono n'existe que si
  // l'élève a explicitement activé le mode examen.
  useEffect(() => {
    if (!tentative?.exam_mode_started_at || tentative.submitted_at || !tentative.duree_minutes) {
      setRemainingSeconds(null)
      return
    }
    const deadline = new Date(tentative.exam_mode_started_at).getTime() + tentative.duree_minutes * 60_000
    const tick = () => setRemainingSeconds(Math.max(0, Math.round((deadline - Date.now()) / 1000)))
    tick()
    const interval = window.setInterval(tick, 1000)
    return () => window.clearInterval(interval)
  }, [tentative?.exam_mode_started_at, tentative?.duree_minutes, tentative?.submitted_at])

  // À zéro, le serveur a déjà (ou va) verrouiller la tentative dès la prochaine
  // requête qui la touche (voir inedit.views._auto_complete_if_expired) - un simple
  // refetch suffit à faire apparaître submitted_at et le corrigé désormais disponible,
  // sans action explicite de l'élève.
  useEffect(() => {
    if (remainingSeconds !== 0 || !tentative || tentative.submitted_at || verrouillageDemande.current) return
    verrouillageDemande.current = true
    api.charger(tentative.id)
      .then((data) => {
        charger(data)
        if (data.submitted_at) {
          setShowCorrection(true)
          setRendueAutomatiquement(true)
          window.scrollTo({ top: 0 })
        }
      })
      .finally(() => {
        window.setTimeout(() => {
          verrouillageDemande.current = false
        }, 3000)
      })
  }, [remainingSeconds, tentative, charger])

  // Arrivée depuis « Terminer ma notation » (page de résultat) : on amène l'élève droit
  // sur la première question à noter, pas en haut d'une longue épreuve.
  useEffect(() => {
    if (defilementInitial.current || searchParams.get("noter") !== "1" || !tentative?.submitted_at) return
    const premiere = questions.find(estANoter)
    defilementInitial.current = true
    if (premiere) window.requestAnimationFrame(() => scrollToQuestion(premiere.id))
  }, [searchParams, tentative?.submitted_at, questions])

  // Salle d'examen : tant que le chrono tourne, le site autour de l'épreuve s'efface (voir
  // lib/modeExamen.ts). Toujours éteint en quittant la page, quoi qu'il arrive.
  const enExamenTot = tentative !== null && tentative.exam_mode_started_at !== null && tentative.submitted_at === null
  useEffect(() => {
    definirModeExamen(enExamenTot)
    return () => definirModeExamen(false)
  }, [enExamenTot])

  useEffect(() => {
    traiteesRef.current = questions.filter((q) => q.traitee).length
    totalRef.current = questions.length
  })

  // Repères de temps : chacun une seule fois, un élève qui revient sur une épreuve avancée
  // n'entend que le plus récent.
  useEffect(() => {
    if (remainingSeconds === null || !tentative?.duree_minutes) return
    const franchis = reperesFranchis(remainingSeconds, tentative.duree_minutes * 60, annonces.current)
    if (franchis.length === 0) return
    franchis.forEach((cle) => annonces.current.add(cle))
    const cle = franchis[franchis.length - 1]
    const message = messageAlerte(cle, { traitees: traiteesRef.current, total: totalRef.current, unite })
    setAnnonce(message)
    toast(message, { id: cle, duration: cle === "une-minute" ? 8000 : 6000 })
  }, [remainingSeconds, tentative?.duree_minutes])

  // Retour sur une épreuve déjà commencée (page rechargée, onglet fermé) : dire où on en est.
  useEffect(() => {
    if (remainingSeconds === null || repriseSignalee.current) return
    repriseSignalee.current = true
    const debut = tentative?.exam_mode_started_at ? new Date(tentative.exam_mode_started_at).getTime() : Date.now()
    if (chargementInitial.current && Date.now() - debut > 30_000) {
      toast("Reprise de l'épreuve", { description: `Il te reste ${formatDuration(remainingSeconds)}.` })
    }
  }, [remainingSeconds, tentative?.exam_mode_started_at])

  // Retour du réseau : on envoie ce qui attendait.
  useEffect(() => {
    async function envoyerLaFile() {
      if (!tentative || fileHorsLigne.current.size === 0) return
      const file = Array.from(fileHorsLigne.current.entries())
      fileHorsLigne.current.clear()
      setEnAttente(0)
      for (const [questionId, corps] of file) {
        try {
          appliquer(await api.noter(tentative.id, questionId, corps))
        } catch (err) {
          if (err instanceof ApiError && err.status === 409) {
            await refetchAfterLock(true)
            return
          }
          if (!(err instanceof ApiError)) {
            fileHorsLigne.current.set(questionId, corps)
            setEnAttente(fileHorsLigne.current.size)
          }
        }
      }
    }
    window.addEventListener("online", envoyerLaFile)
    return () => window.removeEventListener("online", envoyerLaFile)
  }, [tentative])

  // La question « courante », pour la surligner dans la carte de l'épreuve.
  useEffect(() => {
    if (questions.length === 0 || typeof IntersectionObserver === "undefined") return
    const visibles = new Set<number>()
    const observateur = new IntersectionObserver(
      (entrees) => {
        for (const entree of entrees) {
          const id = Number(entree.target.id.replace("question-", ""))
          if (entree.isIntersecting) visibles.add(id)
          else visibles.delete(id)
        }
        const premiere = questions.find((q) => visibles.has(q.id))
        if (premiere) setCourante(premiere.id)
      },
      { rootMargin: "-20% 0px -60% 0px" },
    )
    questions.forEach((q) => {
      const element = document.getElementById(`question-${q.id}`)
      if (element) observateur.observe(element)
    })
    return () => observateur.disconnect()
  }, [questions.length])

  if (loadError) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10 text-center">
        <p className="text-destructive">{loadError}</p>
        <Link
          to={tentative ? cheminRetour(source, tentative.country) : "/"}
          className="mt-3 inline-block text-sm text-primary hover:underline"
        >
          Retour au catalogue
        </Link>
      </div>
    )
  }

  if (!tentative || questions.length === 0) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-10">
        <Skeleton className="mb-6 h-4 w-32" />
        <Skeleton className="mb-3 h-6 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </div>
    )
  }

  const rendue = tentative.submitted_at !== null
  const enExamen = tentative.exam_mode_started_at !== null && !rendue
  const traiteesCount = questions.filter((q) => q.traitee).length
  const nonTraitees = questions.filter((q) => !q.traitee).map((q) => repere(q, unite))
  const aRevoir = questions.filter((q) => flaggedIds.has(q.id)).map((q) => repere(q, unite))
  const pourcentageTraitees = questions.length ? (traiteesCount / questions.length) * 100 : 0
  const enPapier = enExamen && tentative.mode_papier
  // Le briefing ne s'affiche que tant que rien n'est engagé : ni chrono, ni question traitée.
  const briefingVisible = !rendue && tentative.exam_mode_started_at === null && !libreChoisi && traiteesCount === 0
  const groupesPalette: GroupePalette[] = []
  for (const q of questions) {
    const titre = unite === "exercice" ? "Exercices" : `Exercice ${q.numero_exercice}`
    let groupe = groupesPalette[groupesPalette.length - 1]
    if (!groupe || groupe.titre !== titre) {
      groupe = { titre, pastilles: [] }
      groupesPalette.push(groupe)
    }
    groupe.pastilles.push({ id: q.id, label: unite === "exercice" ? q.numero_exercice : q.numero, etat: etatPastille(q, rendue), aRevoir: flaggedIds.has(q.id) })
  }

  function choisirLibre() {
    setLibreChoisi(true)
    try {
      sessionStorage.setItem(`inedit-libre-${tentative!.id}`, "1")
    } catch {
      // stockage indisponible : le briefing se reproposera au prochain chargement
    }
  }

  /** Fusionne une question renvoyée par le serveur dans l'état, `reponse` compris : une
   * question dé-traitée n'a plus de `reponse` dans le payload, et un simple spread
   * garderait l'ancienne. */
  function appliquer(mise_a_jour: TentativeInediteQuestion) {
    const { notation: nouvelle, ...question } = mise_a_jour
    setQuestions((prev) =>
      prev.map((q) => (q.id === question.id ? { ...q, ...question, reponse: question.reponse } : q)),
    )
    if (nouvelle !== undefined) setNotation(nouvelle)
  }

  function remplacer(questionId: number, fabrique: (q: FlatQuestion) => FlatQuestion) {
    setQuestions((prev) => prev.map((q) => (q.id === questionId ? fabrique(q) : q)))
  }

  async function refetchAfterLock(autoLocked: boolean) {
    const data = await api.charger(tentative!.id)
    charger(data)
    setShowCorrection(true)
    setRendueAutomatiquement(autoLocked)
    window.scrollTo({ top: 0, behavior: "smooth" })
    trackEvent("inedit_tentative_completed", { epreuve_id: data.epreuve, auto_locked: autoLocked })
  }

  /** Écriture sur une question ouverte avec mise à jour optimiste : le geste de l'élève
   * (cocher, ajuster) répond instantanément, même sur une connexion lente ; en cas
   * d'échec on rétablit l'état d'avant et on le lui dit, sans casser la page. */
  async function ecrire(
    question: FlatQuestion,
    corps: NoterTentativeQuestionParams,
    optimiste: (q: FlatQuestion) => FlatQuestion,
    messageErreur: string,
  ) {
    const numero = (sequences.current.get(question.id) ?? 0) + 1
    sequences.current.set(question.id, numero)
    remplacer(question.id, optimiste)
    try {
      const mise_a_jour = await api.noter(tentative!.id, question.id, corps)
      if (sequences.current.get(question.id) === numero) appliquer(mise_a_jour)
    } catch (err) {
      if (sequences.current.get(question.id) !== numero) return
      if (!(err instanceof ApiError)) {
        // Pas de réponse du tout : le réseau est coupé. On GARDE le geste de l'élève (revenir en
        // arrière lui ferait perdre une case cochée en pleine épreuve) et on l'enverra au retour.
        fileHorsLigne.current.set(question.id, corps)
        setEnAttente(fileHorsLigne.current.size)
        if (fileHorsLigne.current.size === 1) {
          toast("Hors connexion", { description: "Tes changements sont gardés et partiront au retour du réseau." })
        }
        return
      }
      remplacer(question.id, () => question)
      if (err instanceof ApiError && err.status === 409) {
        // Verrouillée entre-temps (chrono écoulé) : recharger l'état réel plutôt que d'insister.
        await refetchAfterLock(true)
      } else {
        toast.error(messageErreur)
      }
    }
  }

  function handleToggleTraitee(question: FlatQuestion) {
    const traitee = !question.traitee
    ecrire(
      question,
      { traitee },
      (q) => ({ ...q, traitee, reponse: traitee ? (q.reponse ?? REPONSE_VIDE) : undefined }),
      "Impossible d'enregistrer cette question. Réessaie.",
    )
  }

  function handleCriteres(question: FlatQuestion, indices: number[]) {
    const total = indices.reduce((somme, i) => somme + (question.criteres_notation?.[i]?.points ?? 0), 0)
    ecrire(
      question,
      { criteres_valides: indices },
      (q) => ({
        ...q,
        traitee: true,
        reponse: { ...(q.reponse ?? REPONSE_VIDE), notee: true, criteres_valides: indices, points_obtenus: total },
      }),
      "Impossible d'enregistrer ta note. Réessaie.",
    )
  }

  function handlePoints(question: FlatQuestion, points: number) {
    ecrire(
      question,
      { points_obtenus: points },
      (q) => ({ ...q, traitee: true, reponse: { ...(q.reponse ?? REPONSE_VIDE), notee: true, points_obtenus: points } }),
      "Impossible d'enregistrer ta note. Réessaie.",
    )
  }

  function handleCause(question: FlatQuestion, cause: string) {
    ecrire(
      question,
      { cause_perte: cause },
      (q) => ({ ...q, reponse: { ...(q.reponse ?? REPONSE_VIDE), cause_perte: cause } }),
      "Impossible d'enregistrer cette précision. Réessaie.",
    )
  }

  async function handleAnswerQcm(question: FlatQuestion, lettre: string) {
    if (submitting || showCorrection) return
    setSubmitting(true)
    try {
      const updated = await answerTentativeQuestion(tentative!.id, question.id, { reponse_choisie: lettre })
      appliquer(updated)
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        await refetchAfterLock(true)
      } else {
        toast.error("Impossible d'enregistrer ta réponse. Réessaie.")
      }
    } finally {
      setSubmitting(false)
    }
  }

  async function handleToggleFlag(question: FlatQuestion) {
    try {
      const result = await api.marquer(tentative!.id, question.id)
      setFlaggedIds(new Set(result.questions_marquees))
    } catch {
      toast.error("Impossible de marquer cette question. Réessaie.")
    }
  }

  async function handleStartExamMode() {
    const papier = modeAConfirmer === "papier"
    setStartingExam(true)
    try {
      const updated = await api.lancerExamen(tentative!.id, { papier })
      charger(updated)
      setModeAConfirmer(null)
      window.scrollTo({ top: 0 })
    } catch (err) {
      setModeAConfirmer(null)
      toast.error(err instanceof ApiError ? err.message : "Impossible d'activer le mode examen.")
    } finally {
      setStartingExam(false)
    }
  }

  async function handleDownloadSujet() {
    if (!tentative || downloadingSujet) return
    setDownloadingSujet(true)
    try {
      if (source === "officielle") window.open(tentative.sujet_pdf_url ?? "", "_blank", "noopener,noreferrer")
      else await downloadSujetPdf(tentative.epreuve)
    } catch {
      toast.error("Impossible d'ouvrir l'épreuve pour le moment. Réessaie.")
    } finally {
      setDownloadingSujet(false)
    }
  }

  async function handleFinish() {
    setFinishing(true)
    try {
      await api.terminer(tentative!.id)
      setTerminerOuvert(false)
      await refetchAfterLock(false)
    } catch {
      toast.error("Impossible de terminer l'épreuve. Réessaie.")
    } finally {
      setFinishing(false)
    }
  }

  // Sauter la confirmation quand il n'y a rien à perdre : tout est traité, pas de chrono.
  function handleTerminerClick() {
    if (enExamen || nonTraitees.length > 0) setTerminerOuvert(true)
    else handleFinish()
  }

  function allerALaProchaineANoter() {
    const prochaine = questions.find(estANoter)
    if (prochaine) scrollToQuestion(prochaine.id)
  }

  return (
    <div className={cn("mx-auto max-w-6xl animate-fade-up px-4 sm:px-6", enExamen ? "py-4" : "py-8")}>
      {/* Toujours présent, même en salle d'examen : c'est ce qui dit au lecteur d'écran qu'un
          repère de temps vient de passer, sans interrompre la lecture d'une question. */}
      <p role="status" className="sr-only">
        {annonce}
      </p>

      <Link
        to={cheminRetour(source, tentative.country)}
        onClick={(event) => {
          // En plein chrono, quitter n'arrête rien : on le dit avant de laisser partir.
          if (enExamen) {
            event.preventDefault()
            setQuitterOuvert(true)
          }
        }}
        className="mb-4 inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-primary"
      >
        <ArrowLeft className="size-4" />
        Quitter l'épreuve
      </Link>

      {/* Le briefing porte déjà le titre (son h1) ; ensuite plus rien ne le disait : en plein examen, le site
          autour de l'épreuve a disparu et on ne savait plus laquelle on composait. */}
      {!briefingVisible && (
        <div className="mb-4">
          <h1 className="font-display text-xl font-semibold leading-tight sm:text-2xl">{tentative.epreuve_titre}</h1>
          <p className="mt-0.5 text-sm text-muted-foreground">{tentative.cursus_display}</p>
        </div>
      )}

      {briefingVisible && (
        <ChoixModeEpreuve
          titre={tentative.epreuve_titre}
          dureeMinutes={tentative.duree_minutes}
          dureeEstimee={tentative.duree_estimee}
          bareme={tentative.bareme}
          nbExercices={tentative.exercices.length}
          nbQuestions={questions.length}
          unite={unite}
          papierDisponible={tentative.sujet_pdf_disponible}
          onExamen={() => setModeAConfirmer("examen")}
          onPapier={() => setModeAConfirmer("papier")}
          onLibre={choisirLibre}
        />
      )}

      {/* Barre d'actions "flottante" : carte sticky arrondie plutôt qu'un bandeau
          plein-bleed - deux rangées (identité/utilitaires en haut, progression en bas)
          au lieu d'un unique flex-wrap où badges et boutons se mélangeaient sans
          hiérarchie visuelle. Sur mobile les libellés secondaires disparaissent (icône
          seule) pour que la rangée du haut tienne sur une ligne à 375 px. En salle d'examen
          l'en-tête du site a disparu : la barre se colle tout en haut. */}
      <div
        className={cn(
          "sticky z-10 mb-6 rounded-xl border border-border bg-background/95 px-3 py-3 shadow-sm backdrop-blur-sm sm:px-5",
          enExamen ? "top-2" : "top-[72px]",
        )}
      >
        {/* Rappel du titre dans la barre qui reste à l'écran pendant le défilement. */}
        {!briefingVisible && (
          <p className="mb-1.5 truncate text-xs font-medium text-muted-foreground" title={tentative.epreuve_titre}>
            {tentative.epreuve_titre}
          </p>
        )}
        <div className="flex items-center justify-between gap-2">
          <div className="flex min-w-0 items-center gap-1 sm:gap-2">
            <Badge variant="secondary" className="hidden max-w-[16rem] truncate md:inline-flex">
              {tentative.cursus_display}
            </Badge>
            {/* Inédite : pas avant d'avoir choisi son mode - le briefing promet un sujet inédit
                jusqu'au départ, un PDF complet à un clic de là le contredirait. Une annale
                officielle, elle, est publique : rien à protéger. */}
            {tentative.sujet_pdf_disponible && !(briefingVisible && source === "inedit") && (
              <Button
                size="sm"
                variant="ghost"
                disabled={downloadingSujet}
                onClick={handleDownloadSujet}
                title="Ouvrir l'épreuve en PDF"
                aria-label="Ouvrir l'épreuve en PDF"
              >
                <FileDown className="size-3.5" />
                <span className="hidden sm:inline">{downloadingSujet ? "Ouverture..." : "PDF"}</span>
              </Button>
            )}
            {tentative.correction_disponible && (
              <Button
                size="sm"
                variant="ghost"
                aria-pressed={showCorrection}
                onClick={() => setShowCorrection((v) => !v)}
                title={showCorrection ? "Masquer la correction" : "Afficher la correction"}
              >
                {showCorrection ? <EyeOff className="size-3.5" /> : <Eye className="size-3.5" />}
                <span className="hidden sm:inline">{showCorrection ? "Masquer la correction" : "Afficher la correction"}</span>
                <span className="sm:hidden">Correction</span>
              </Button>
            )}
          </div>

          <div className="flex shrink-0 items-center gap-1.5 sm:gap-2">
            {!tentative.exam_mode_started_at && !rendue && tentative.duree_minutes && !briefingVisible && (
              <Button
                size="sm"
                variant="outline"
                disabled={traiteesCount > 0}
                onClick={() => setModeAConfirmer("examen")}
                title={traiteesCount > 0 ? "Disponible avant ta première réponse" : "Passer l'épreuve en conditions réelles"}
              >
                <Timer className="size-3.5" />
                <span className="hidden sm:inline">Mode examen ({tentative.duree_minutes} min)</span>
                <span className="sm:hidden">Examen</span>
              </Button>
            )}

            {remainingSeconds !== null && (
              <Badge
                role="timer"
                aria-label="Temps restant"
                variant={remainingSeconds <= 300 ? "warning" : "outline"}
                className={cn(
                  "flex items-center gap-1 text-sm tabular-nums",
                  remainingSeconds <= 60 && "motion-safe:animate-pulse",
                )}
              >
                <Timer className="size-3.5" />
                {formatDuration(remainingSeconds)}
              </Badge>
            )}

            {!rendue ? (
              <Button size="sm" disabled={finishing} onClick={handleTerminerClick}>
                Terminer<span className="hidden sm:inline">&nbsp;l'épreuve</span>
              </Button>
            ) : (
              <Button asChild size="sm">
                <Link to={cheminResultat(source, tentative.id)}>Voir mon résultat</Link>
              </Button>
            )}
          </div>
        </div>

        <div className="mt-3 flex items-center gap-2.5">
          <div
            role="progressbar"
            aria-label={`${m.pluriel[0].toUpperCase()}${m.pluriel.slice(1)} ${m.traites}`}
            aria-valuemin={0}
            aria-valuemax={questions.length}
            aria-valuenow={traiteesCount}
            className="h-1.5 min-w-12 flex-1 overflow-hidden rounded-full bg-secondary"
          >
            <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${pourcentageTraitees}%` }} />
          </div>
          <span className="shrink-0 text-xs font-medium tabular-nums text-muted-foreground">
            {traiteesCount} / {questions.length} {m.traites}
          </span>
          {notation && (
            <span
              aria-live="polite"
              title={notation.definitive ? "Note définitive" : "Note provisoire : elle évolue à mesure que tu notes tes questions"}
              className="shrink-0 rounded-md bg-secondary px-2 py-0.5 text-xs font-semibold tabular-nums"
            >
              {notation.definitive ? "Note" : "Provisoire"} {formatNote(notation.note, notation.bareme)}
            </span>
          )}
        </div>

        {enAttente > 0 && (
          <p role="status" className="mt-2 flex items-center gap-1.5 text-xs text-muted-foreground">
            <CloudOff className="size-3.5 shrink-0" aria-hidden="true" />
            {enAttente} changement{enAttente > 1 ? "s" : ""} en attente : envoyé{enAttente > 1 ? "s" : ""} dès que le
            réseau revient.
          </p>
        )}

        <div className="mt-3 lg:hidden">
          <BoutonPalette
            groupes={groupesPalette}
            courante={courante}
            rendue={rendue}
            onAller={scrollToQuestion}
            resume={`${traiteesCount}/${questions.length}`}
            unite={unite}
          />
        </div>
      </div>

      {rendue && notation && (
        <BandeauNotation
          notation={notation}
          tentativeId={tentative.id}
          rendueAutomatiquement={rendueAutomatiquement}
          onProchaine={allerALaProchaineANoter}
          unite={unite}
          resultatPath={cheminResultat(source, tentative.id)}
        />
      )}

      {tentative.bareme_estime && (
        <p className="mb-6 flex items-start gap-2 text-xs text-muted-foreground">
          <Info className="mt-0.5 size-3.5 shrink-0" />
          {unite === "exercice"
            ? "Barème estimé : les points de cette épreuve n'étant pas tous indiqués, chaque exercice pèse autant."
            : "Barème estimé : les points de chaque exercice sont répartis à parts égales entre ses questions"}
          {unite === "exercice" ? "" : ` (total : ${formatPoints(tentative.bareme)} points).`}
        </p>
      )}

      {enPapier && (
        <div className="mb-8 rounded-2xl border border-primary/30 bg-primary/5 px-4 py-4">
          <p className="flex items-start gap-2 text-sm">
            <FileText className="mt-0.5 size-5 shrink-0 text-primary" aria-hidden="true" />
            <span>
              <strong>Tu composes sur papier.</strong> Les énoncés sont dans ton sujet imprimé. Ici, coche chaque question
              au moment où tu l'as {m.traite} : c'est ce qui compte pour ta note.
            </span>
          </p>
          {tentative.sujet_pdf_disponible && (
            <Button className="mt-3" size="sm" disabled={downloadingSujet} onClick={handleDownloadSujet}>
              <FileDown />
              {downloadingSujet ? "Ouverture..." : "Ouvrir le sujet (PDF)"}
            </Button>
          )}
        </div>
      )}

      <div className="lg:grid lg:grid-cols-[minmax(0,1fr)_15rem] lg:gap-10">
        <div className="min-w-0">
          {questions.map((question, index) => {
            const isNewExercice = index === 0 || question.numero_exercice !== questions[index - 1].numero_exercice
            // Sous-partie locale (voir QuestionInedite.groupe_local côté backend) - peut
            // changer PLUSIEURS fois au sein d'un même exercice, contrairement à `groupes`
            // ci-dessous (un seul en-tête par exercice). Comparée à la question précédente,
            // pas seulement à isNewExercice : sans ça un exercice scindé en deux sous-parties
            // ("Vérification des savoirs" puis "des savoir-faire") afficherait les deux
            // repères d'un coup en tête, avant sa toute première question.
            const isNewGroupeLocal =
              !!question.groupe_local && (isNewExercice || question.groupe_local !== questions[index - 1].groupe_local)
            const isFlagged = flaggedIds.has(question.id)
            const corrigeVisible = showCorrection && !!question.corrige_markdown
            return (
              <div
                key={question.id}
                id={`question-${question.id}`}
                className={cn("scroll-mt-52", !isNewExercice && !isNewGroupeLocal && "mt-8")}
              >
                {isNewExercice && (
                  <>
                    {/* En-tête de groupe (Partie/section/matière) - affiché uniquement quand
                        l'épreuve est structurée en groupes (voir ExerciceInedite.groupes,
                        [] pour la grande majorité des épreuves). Purement informatif. */}
                    {question.groupes.length > 0 && (
                      <p className={cn("text-xs font-semibold uppercase tracking-wide text-muted-foreground", index > 0 && "mt-8")}>
                        {question.groupes.join(" · ")}
                      </p>
                    )}
                    <div className={cn("mb-3 flex items-center gap-1.5", index > 0 && "mt-8 border-t border-border pt-6", index > 0 && question.groupes.length > 0 && "mt-3 border-t-0 pt-0")}>
                      <Badge variant="outline">Exercice {question.numero_exercice}</Badge>
                      {question.points_exercice && <Badge variant="outline">{question.points_exercice} pts</Badge>}
                    </div>
                    {/* Support commun aux questions de l'exercice - rendu une seule fois,
                        ici et pas dans chaque question (voir ExerciceInedite.enonce_intro_markdown).
                        Sur papier, il est dans le sujet imprimé : masqué à l'écran. */}
                    {question.exercice_intro_markdown && !(enPapier) && (
                      <article className="mb-5 rounded-md border border-border bg-muted/40 px-4 py-3 prose prose-neutral max-w-none text-justify prose-sm dark:prose-invert">
                        <EpreuveMarkdown markdown={question.exercice_intro_markdown} />
                      </article>
                    )}
                  </>
                )}

                {isNewGroupeLocal && !enPapier && (
                  <p
                    className={cn(
                      "mb-3 text-sm font-semibold text-foreground",
                      isNewExercice ? "mt-0" : "mt-8 border-t border-dashed border-border pt-6",
                    )}
                  >
                    {question.groupe_local}
                  </p>
                )}

                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0 flex-1">
                    <span className="mb-1 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                      {unite === "exercice" ? "" : `Question ${question.numero}`}
                      {/* Un exercice porte déjà ses points dans son en-tête : le répéter serait du bruit,
                          sauf quand ils sont estimés (l'en-tête n'en montre alors aucun). */}
                      {(unite !== "exercice" || question.bareme_estime) && (
                        <span
                          className="rounded bg-secondary px-1.5 py-0.5 font-medium normal-case tracking-normal tabular-nums"
                          title={question.bareme_estime ? "Barème estimé" : undefined}
                        >
                          {question.bareme_estime ? "≈ " : ""}
                          {formatPoints(question.points)} pt{question.points >= 2 ? "s" : ""}
                          {unite === "exercice" ? " pour cet exercice" : ""}
                        </span>
                      )}
                    </span>
                    {enPapier ? (
                      // L'énoncé est sur la feuille imprimée : ici il ne reste qu'un accès de secours.
                      <details className="text-sm">
                        <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
                          Voir l'énoncé à l'écran
                        </summary>
                        <article className="prose prose-neutral mt-2 max-w-none dark:prose-invert">
                          <EpreuveMarkdown markdown={question.enonce_markdown} />
                        </article>
                      </details>
                    ) : (
                      <article className="prose prose-neutral max-w-none dark:prose-invert sm:text-justify">
                        <EpreuveMarkdown markdown={question.enonce_markdown} />
                      </article>
                    )}
                  </div>
                  <button
                    type="button"
                    onClick={() => handleToggleFlag(question)}
                    aria-pressed={isFlagged}
                    aria-label="Marquer à revoir"
                    title="Marquer cette question pour y revenir plus tard"
                    className={cn(
                      "mt-1 shrink-0 rounded-md p-2 transition-colors focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none",
                      isFlagged ? "text-gold-text" : "text-muted-foreground hover:text-foreground",
                    )}
                  >
                    <Flag className={cn("size-4", isFlagged && "fill-current")} />
                  </button>
                </div>

                {question.type_reponse === "QCM" ? (
                  <div className="mt-3 flex flex-col gap-2">
                    {question.choix.map((choix) => {
                      const isSelected = question.reponse?.reponse_choisie === choix.lettre
                      const isCorrectChoice = showCorrection && question.reponse_correcte === choix.lettre
                      const isWrongSelected = showCorrection && isSelected && !isCorrectChoice
                      return (
                        <button
                          key={choix.lettre}
                          type="button"
                          disabled={submitting || showCorrection}
                          onClick={() => handleAnswerQcm(question, choix.lettre)}
                          className={cn(
                            "flex min-h-11 items-center justify-between gap-2 rounded-md border px-3.5 py-2.5 text-left text-sm transition-colors focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none disabled:cursor-default",
                            isCorrectChoice && "border-success bg-success/10",
                            isWrongSelected && "border-destructive bg-destructive/10",
                            !showCorrection && isSelected && "border-primary bg-primary/5",
                            !showCorrection && !isSelected && "border-border hover:bg-accent/40",
                            showCorrection && !isSelected && !isCorrectChoice && "border-border opacity-60",
                          )}
                        >
                          <span>
                            <span className="font-medium">{choix.lettre.toUpperCase()}.</span> <ChoixText texte={choix.texte} />
                          </span>
                          {isCorrectChoice && <Check className="size-4 shrink-0 text-success" />}
                          {isWrongSelected && <X className="size-4 shrink-0 text-destructive" />}
                        </button>
                      )
                    })}
                  </div>
                ) : (
                  <div className="mt-3 flex flex-col gap-3">
                    {/* Question ouverte : l'élève compose sur brouillon ou papier, puis le
                        déclare ici. Le corrigé (une fois disponible) précède la grille de
                        notation, pour comparer d'abord, se noter ensuite. */}
                    <div className="flex flex-wrap items-center gap-3">
                      <BoutonTraitee
                        unite={unite}
                        traitee={question.traitee}
                        rendue={rendue}
                        onToggle={() => handleToggleTraitee(question)}
                      />
                      {corrigeVisible && !question.traitee && (
                        <span className="text-sm text-muted-foreground">
                          {unite === "exercice" ? "Non traité" : "Non traitée"} : {m.cet} {m.singulier} vaut 0 point.
                        </span>
                      )}
                    </div>

                    {corrigeVisible && (
                      <article className="prose prose-neutral max-w-none border-l-2 border-border pl-4 dark:prose-invert sm:text-justify">
                        <EpreuveMarkdown markdown={question.corrige_markdown ?? ""} />
                      </article>
                    )}

                    {corrigeVisible && question.traitee && (
                      <GrilleNotation
                        question={question}
                        onCriteres={(indices) => handleCriteres(question, indices)}
                        onPoints={(points) => handlePoints(question, points)}
                      />
                    )}

                    {/* Le rapport de fin d'épreuve a besoin de savoir POURQUOI : facultatif, deux clics. */}
                    {corrigeVisible && question.traitee && question.reponse?.notee &&
                      (question.reponse.points_obtenus ?? 0) < question.points && (
                        <CausePerte
                          valeur={question.reponse.cause_perte ?? ""}
                          onChoisir={(cause) => handleCause(question, cause)}
                        />
                      )}
                    {corrigeVisible && !question.traitee && (
                      <CausePerte
                        nonTraitee
                        valeur={question.reponse?.cause_perte ?? ""}
                        onChoisir={(cause) => handleCause(question, cause)}
                      />
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* La carte de l'épreuve, à droite sur grand écran (sous la barre d'état, qui la
            précède dans le flux sur mobile : voir BoutonPalette). */}
        <aside className="hidden lg:block">
          <div className={cn("sticky", enExamen ? "top-40" : "top-60")}>
            <h2 className="mb-3 text-sm font-semibold">{`${m.pluriel[0].toUpperCase()}${m.pluriel.slice(1)}`}</h2>
            <PaletteQuestions
              groupes={groupesPalette}
              courante={courante}
              rendue={rendue}
              unite={unite}
              onAller={scrollToQuestion}
            />
          </div>
        </aside>
      </div>

      <DialogueTerminer
        open={terminerOuvert}
        onOpenChange={setTerminerOuvert}
        enExamen={enExamen}
        total={questions.length}
        traitees={traiteesCount}
        nonTraitees={nonTraitees}
        aRevoir={aRevoir}
        enCours={finishing}
        unite={unite}
        onAller={(questionId) => window.requestAnimationFrame(() => scrollToQuestion(questionId))}
        onConfirmer={handleFinish}
      />
      {tentative.duree_minutes && (
        <DialogueModeExamen
          open={modeAConfirmer !== null}
          onOpenChange={(ouvert) => !ouvert && setModeAConfirmer(null)}
          dureeMinutes={tentative.duree_minutes}
          dureeEstimee={tentative.duree_estimee}
          papier={modeAConfirmer === "papier"}
          enCours={startingExam}
          unite={unite}
          onConfirmer={handleStartExamMode}
        />
      )}
      <DialogueQuitter
        open={quitterOuvert}
        onOpenChange={setQuitterOuvert}
        onConfirmer={() => navigate(cheminRetour(source, tentative.country))}
      />
    </div>
  )
}
