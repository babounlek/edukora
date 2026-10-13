import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { Link, useNavigate, useSearchParams } from "react-router-dom"
import {
  AlertCircle,
  ArrowRight,
  Check,
  CheckCircle2,
  Download,
  FileText,
  GraduationCap,
  History,
  Lock,
  Minus,
  Plus,
  Printer,
  RefreshCw,
  Search,
  Sparkles,
  X,
} from "lucide-react"
import { toast } from "sonner"

import {
  createFiche,
  getFiche,
  getFicheEligibilite,
  downloadFicheCorrigePdf,
  downloadFicheSujetPdf,
  listCursus,
  listMyFiches,
  listMyInscriptionsRepetiteur,
  listQuizSubjects,
} from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { Cursus, Difficulte, Fiche, FicheThemeEligible, InscriptionRepetiteur, Subject } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { ApercuFichesPdf } from "@/components/ApercuFichesPdf"
import { ErreurChargement } from "@/components/ErreurChargement"
import { Etape, EtapesPresentation, Eyebrow, LigneRecap, RecapVide, StatChip } from "@/components/Configurateur"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { trackEvent } from "@/lib/analytics"
import { useSeo } from "@/lib/seo"
import { capitaliserTheme, cn } from "@/lib/utils"
import { localeCourante, t, tn, useI18n } from "@/lib/i18n"
import { traduireLibelleSerie } from "@/lib/cursus"

const TOUTES_DIFFICULTES = "toutes"
const DIFFICULTE_LABELS: Record<Difficulte, string> = {
  get FAIBLE() { return t("fi.diff_FAIBLE") },
  get MOYENNE() { return t("fi.diff_MOYENNE") },
  get ELEVEE() { return t("fi.diff_ELEVEE") },
}
const DIFFICULTE_OPTIONS = [TOUTES_DIFFICULTES, "FAIBLE", "MOYENNE", "ELEVEE"] as const
type DifficulteChoix = (typeof DIFFICULTE_OPTIONS)[number]

// Au-delà de ce nombre de compétences, la liste passe en zone défilante avec un champ
// de filtre : sur une matière bien fournie (maths Terminale C dépasse la vingtaine de
// thèmes), la liste brute poussait le bouton "Générer" hors de l'écran et obligeait à
// parcourir tout le formulaire pour retrouver le récapitulatif.
const SEUIL_RECHERCHE_THEMES = 8

// Nombre de fiches passées affichées avant le bouton "Tout afficher" - la colonne
// latérale est collante (sticky) sur desktop, une liste sans limite la ferait dépasser
// la hauteur de l'écran et perdre tout l'intérêt du collage.
const FICHES_RECENTES_VISIBLES = 4

// ~2.5s, même ordre de grandeur que le sondage de paiement (SubscribePage) - la
// génération PDF tourne dans un processus détaché (Playwright hors ligne), quelques
// secondes en pratique pour deux PDF courts.
const POLL_INTERVAL_MS = 2500

function defaultTitre(subject: Subject | undefined): string {
  if (!subject) return ""
  const date = new Date().toLocaleDateString(localeCourante(), { day: "numeric", month: "long" })
  return t("fi.titre_defaut", { matiere: subject.label, date })
}

function formatDateCourte(iso: string): string {
  return new Date(iso).toLocaleDateString(localeCourante(), { day: "numeric", month: "short" })
}

/** Nombre de questions réellement disponibles pour un jeu de thèmes à une difficulté donnée. */
function compterDisponibles(themes: FicheThemeEligible[], difficulte: DifficulteChoix): number {
  return themes.reduce(
    (sum, t) => sum + (difficulte === TOUTES_DIFFICULTES ? t.total : t.par_difficulte[difficulte] ?? 0),
    0,
  )
}

export function FichesPage() {
  useI18n()
  useSeo({
    title: t("fi.seo_titre"),
    description: t("fi.seo_description"),
  })

  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const { country } = useCountry()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const [inscriptions, setInscriptions] = useState<InscriptionRepetiteur[]>([])
  const [inscriptionsLoaded, setInscriptionsLoaded] = useState(false)
  const [erreurChargement, setErreurChargement] = useState(false)
  // Incrémenté par « Réessayer » : relance l'effet de chargement initial.
  const [essai, setEssai] = useState(0)
  const [cursusList, setCursusList] = useState<Cursus[]>([])
  const [selectedCursus, setSelectedCursus] = useState("")
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [selectedSubject, setSelectedSubject] = useState("")
  const [eligibleThemes, setEligibleThemes] = useState<FicheThemeEligible[]>([])
  const [themesLoading, setThemesLoading] = useState(false)
  const [themeQuery, setThemeQuery] = useState("")
  const [selectedThemeIds, setSelectedThemeIds] = useState<Set<number>>(new Set())
  const [difficulte, setDifficulte] = useState<DifficulteChoix>(TOUTES_DIFFICULTES)
  const [n, setN] = useState(10)
  const [titre, setTitre] = useState("")
  const [titreEdited, setTitreEdited] = useState(false)

  const [creating, setCreating] = useState(false)
  const [error, setError] = useState("")
  const [fiche, setFiche] = useState<Fiche | null>(null)
  const [mesFiches, setMesFiches] = useState<Fiche[]>([])
  const [toutesFichesVisibles, setToutesFichesVisibles] = useState(false)
  const pollRef = useRef<number | null>(null)
  const resultatRef = useRef<HTMLDivElement | null>(null)

  const rafraichirMesFiches = useCallback(() => {
    // Best-effort : l'historique est un confort (retrouver le PDF de la semaine
    // dernière sans le régénérer), jamais un prérequis pour composer une fiche.
    listMyFiches().then(setMesFiches).catch(() => {})
  }, [])

  useEffect(() => {
    if (authLoading) return
    if (!isAuthenticated) {
      // Aperçu public plutôt que redirection vers /connexion. C'est ici que le mur coûtait
      // le plus cher : Fiches est un add-on qui vise les répétiteurs et enseignants, un
      // public qui ne se sait pas concerné tant qu'on ne le lui a pas dit. Renvoyer un
      // formulaire OTP laissait l'élève curieux repartir sans comprendre que ce n'était
      // pas pour lui, et le répétiteur sans jamais découvrir que l'outil existe.
      setInscriptionsLoaded(true)
      return
    }
    // Sans .catch, un échec laissait `inscriptionsLoaded` à false : le squelette de page ne
    // partait jamais. Les deux requêtes conditionnent l'écran (accès + cursus), donc un échec de
    // l'une ou l'autre passe par le même état d'erreur avec « Réessayer ».
    let annule = false
    setErreurChargement(false)
    listMyInscriptionsRepetiteur()
      .then((data) => {
        if (annule) return
        setInscriptions(data.filter((i) => i.is_active))
        setInscriptionsLoaded(true)
      })
      .catch(() => {
        if (!annule) setErreurChargement(true)
      })
    listCursus(country)
      .then((data) => {
        if (!annule) setCursusList(data)
      })
      .catch(() => {
        if (!annule) setErreurChargement(true)
      })
    rafraichirMesFiches()
    return () => {
      annule = true
    }
  }, [authLoading, isAuthenticated, country, rafraichirMesFiches, essai])

  useEffect(() => {
    // ?ref=pdf_fiche_corrige : posé par le PDF corrigé d'une fiche (voir
    // fiches.pdf._corrige_deep_link) sur son propre CTA - ce PDF reste entre les mains
    // du répétiteur (jamais distribué, voir la mention "réservé à l'usage personnel"
    // dans son template), donc /fiches (générer la prochaine) est la destination
    // pertinente. Seule façon de mesurer combien de répétiteurs reviennent réellement
    // depuis un corrigé imprimé plutôt que de le supposer sans donnée.
    // Le garde-fou déconnecté survit à l'aperçu public : sans lui, un répétiteur non
    // connecté compterait deux fois (une fois en arrivant, une fois de retour de
    // /connexion via le state.from ci-dessous, paramètre ?ref inclus). La visite reste
    // donc comptée une seule fois, au moment où elle aboutit.
    if (!isAuthenticated) return
    if (searchParams.get("ref") !== "pdf_fiche_corrige") return
    trackEvent("pdf_fiche_corrige_landing", {})
  }, [isAuthenticated, searchParams])

  // searchParams.toString() plutôt que juste "/fiches" : préserve ?ref=pdf_fiche_corrige
  // (posé par le QR code du PDF corrigé, voir fiches.pdf._corrige_deep_link) au retour de
  // connexion - sinon un répétiteur qui scanne son corrigé sans être déjà connecté sur cet
  // appareil perd le paramètre avant même que l'effet de tracking ci-dessus ne le voie.
  const loginFrom = searchParams.toString() ? `/fiches?${searchParams.toString()}` : "/fiches"

  const inscriptionCourante = inscriptions.find((i) => String(i.cursus.id) === selectedCursus)
  const hasAccessForCursus = Boolean(inscriptionCourante)

  // Un répétiteur n'a le plus souvent qu'un seul cursus avec l'add-on actif :
  // le présélectionner supprime un choix qui n'en est pas un et fait apparaître
  // directement l'étape utile (la matière) dès le chargement.
  useEffect(() => {
    if (selectedCursus || inscriptions.length === 0 || cursusList.length === 0) return
    const accessibles = cursusList.filter((c) => inscriptions.some((i) => i.cursus.id === c.id))
    if (accessibles.length === 1) setSelectedCursus(String(accessibles[0].id))
  }, [inscriptions, cursusList, selectedCursus])

  // Uniquement les matières ayant déjà une banque de CompetenceItem VALIDE pour CE
  // cursus (voir quiz.views.list_quiz_subjects) - une fiche est tirée dans cette même
  // banque (fiches.services.generer_fiche), donc lister tout le référentiel du pays
  // laissait choisir une matière dont l'étape 2 ne pouvait que répondre "aucune question
  // disponible" : un aller-retour par matière pour deviner lesquelles sont servies.
  useEffect(() => {
    const cursusObj = cursusList.find((c) => String(c.id) === selectedCursus)
    if (!cursusObj || !hasAccessForCursus) {
      setSubjects([])
      return
    }
    setSelectedSubject("")
    listQuizSubjects(cursusObj.id)
      .then(setSubjects)
      .catch(() => toast.error(t("fi.err_matieres")))
  }, [selectedCursus, cursusList, hasAccessForCursus])

  useEffect(() => {
    setThemeQuery("")
    if (!selectedCursus || !selectedSubject) {
      setEligibleThemes([])
      setSelectedThemeIds(new Set())
      setThemesLoading(false)
      return
    }
    // Drapeau d'annulation : sans lui, un enchaînement rapide de matières laissait la
    // réponse la plus lente écraser la plus récente (liste de compétences appartenant
    // à la matière précédente, sans aucun signal à l'écran).
    let annule = false
    setThemesLoading(true)
    getFicheEligibilite(Number(selectedCursus), Number(selectedSubject))
      .then((themes) => {
        if (annule) return
        setEligibleThemes(themes)
        setSelectedThemeIds(new Set())
      })
      .catch(() => {
        if (!annule) toast.error(t("fi.err_competences"))
      })
      .finally(() => {
        if (!annule) setThemesLoading(false)
      })
    const subject = subjects.find((s) => String(s.id) === selectedSubject)
    if (!titreEdited) setTitre(defaultTitre(subject))
    return () => {
      annule = true
    }
  }, [selectedCursus, selectedSubject]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current)
    }
  }, [])

  const disponiblePour = useCallback(
    (theme: FicheThemeEligible): number => compterDisponibles([theme], difficulte),
    [difficulte],
  )

  // Une compétence sélectionnée peut tomber à zéro question quand on resserre la
  // difficulté : la désélectionner plutôt que la laisser cochée-mais-grisée, état
  // contradictoire qui faisait afficher un maximum de questions sans rapport avec les
  // cases visiblement cochées.
  useEffect(() => {
    setSelectedThemeIds((prev) => {
      const next = new Set(
        [...prev].filter((id) => {
          const theme = eligibleThemes.find((t) => t.theme_id === id)
          return Boolean(theme) && disponiblePour(theme as FicheThemeEligible) > 0
        }),
      )
      return next.size === prev.size ? prev : next
    })
  }, [difficulte, eligibleThemes, disponiblePour])

  const selectedThemes = useMemo(
    () => eligibleThemes.filter((t) => selectedThemeIds.has(t.theme_id)),
    [eligibleThemes, selectedThemeIds],
  )

  const maxN = useMemo(() => compterDisponibles(selectedThemes, difficulte), [selectedThemes, difficulte])

  // Compteur par difficulté affiché sur chaque bouton du sélecteur : sur les
  // compétences déjà cochées s'il y en a, sinon sur toute la matière - la question
  // "est-ce qu'il reste des questions difficiles ici ?" se posait jusqu'ici en
  // changeant de difficulté puis en lisant le maximum, un aller-retour par essai.
  const baseComptage = selectedThemes.length > 0 ? selectedThemes : eligibleThemes
  const themesFiltres = useMemo(() => {
    const q = themeQuery.trim().toLowerCase()
    if (!q) return eligibleThemes
    return eligibleThemes.filter((t) => t.theme.toLowerCase().includes(q))
  }, [eligibleThemes, themeQuery])

  const themesSelectionnables = useMemo(
    () => eligibleThemes.filter((t) => disponiblePour(t) > 0),
    [eligibleThemes, disponiblePour],
  )

  useEffect(() => {
    if (maxN > 0 && n > maxN) setN(maxN)
  }, [maxN]) // eslint-disable-line react-hooks/exhaustive-deps

  const presetsN = useMemo(() => {
    const valeurs = [5, 10, 15, 20, maxN].filter((v) => v >= 1 && v <= maxN)
    return [...new Set(valeurs)].sort((a, b) => a - b)
  }, [maxN])

  function toggleTheme(themeId: number) {
    setSelectedThemeIds((prev) => {
      const next = new Set(prev)
      if (next.has(themeId)) next.delete(themeId)
      else next.add(themeId)
      return next
    })
  }

  function pollFiche(ficheId: number) {
    if (pollRef.current) window.clearInterval(pollRef.current)
    pollRef.current = window.setInterval(async () => {
      try {
        const updated = await getFiche(ficheId)
        if (updated.statut !== "EN_COURS") {
          if (pollRef.current) window.clearInterval(pollRef.current)
          setFiche(updated)
          rafraichirMesFiches()
          if (updated.statut === "PRETE") toast.success(t("fi.prete_toast"), { description: updated.titre })
        }
      } catch {
        // une erreur ponctuelle du réseau ne doit pas interrompre l'attente
      }
    }, POLL_INTERVAL_MS)
  }

  async function handleSubmit() {
    if (!selectedCursus || !selectedSubject || selectedThemeIds.size === 0 || maxN === 0) return
    setCreating(true)
    setError("")
    try {
      const created = await createFiche({
        cursus: Number(selectedCursus),
        subject: Number(selectedSubject),
        themes: Array.from(selectedThemeIds),
        difficulte: difficulte === TOUTES_DIFFICULTES ? undefined : difficulte,
        n,
        titre: titre || defaultTitre(subjects.find((s) => String(s.id) === selectedSubject)),
      })
      setFiche(created)
      rafraichirMesFiches()
      pollFiche(created.id)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("fi.err_generer"))
    } finally {
      setCreating(false)
    }
  }

  // Le résultat s'ajoute au-dessus du configurateur au lieu de le remplacer : les
  // réglages restent en place, générer la fiche suivante (autre difficulté, quelques
  // questions de plus) ne repart plus du choix du cursus à chaque fois.
  function fermerResultat() {
    if (pollRef.current) window.clearInterval(pollRef.current)
    setFiche(null)
    setError("")
  }

  const ficheId = fiche?.id
  useEffect(() => {
    if (!ficheId) return
    resultatRef.current?.scrollIntoView({ behavior: "smooth", block: "center" })
  }, [ficheId])

  if (!authLoading && isAuthenticated && erreurChargement) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        <ErreurChargement objet={t("fi.objet_acces")} onRetry={() => setEssai((n) => n + 1)} />
      </div>
    )
  }

  if (authLoading || !inscriptionsLoaded) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        <Skeleton className="mb-6 h-40 w-full rounded-2xl" />
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1.55fr)_minmax(0,1fr)]">
          <Skeleton className="h-96 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    )
  }

  const cursusChoisi = cursusList.find((c) => String(c.id) === selectedCursus)
  const subjectChoisi = subjects.find((s) => String(s.id) === selectedSubject)
  const pretAGenerer = Boolean(selectedCursus && selectedSubject && selectedThemeIds.size > 0 && maxN > 0)
  const fichesAffichees = toutesFichesVisibles ? mesFiches : mesFiches.slice(0, FICHES_RECENTES_VISIBLES)

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-10 sm:px-6">
      <div className="relative mb-8 overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-primary/[0.07] via-transparent to-transparent p-6 sm:p-8 lg:p-12">
        {/* Filets horizontaux façon copie double plutôt que la trame à points : le
            décor du hero rappelle le papier imprimé, cohérent avec ce que produit
            réellement cette page (deux PDF), sans copier le pointillé de Quiz. */}
        <div
          className="absolute inset-0 opacity-[0.05]"
          style={{
            backgroundImage:
              "repeating-linear-gradient(to bottom, var(--foreground) 0, var(--foreground) 1px, transparent 1px, transparent 28px)",
          }}
        />
        <div className="relative grid gap-10 lg:grid-cols-[1.2fr_0.8fr] lg:items-center lg:gap-16">
          <div>
            <div className="mb-3 flex size-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <GraduationCap className="size-5" />
            </div>
            <Eyebrow>{t("fi.eyebrow")}</Eyebrow>
            <h1 className="font-display text-4xl font-semibold tracking-tight sm:text-5xl">{t("fi.h1")}</h1>
            <p className="mt-3 max-w-md text-lg font-medium leading-snug text-foreground/90">
              {t("fi.accroche")}
            </p>
            <p className="mt-2 max-w-md text-muted-foreground">
              {t("fi.hero_texte")}
            </p>

            <div className="mt-5 flex flex-wrap gap-2">
              <StatChip icon={<Printer className="size-3.5 text-primary" />}>
                <span className="font-medium">{t("fi.chip_pdf")}</span>
                <span className="text-muted-foreground">{t("fi.chip_pdf_detail")}</span>
              </StatChip>
              {mesFiches.length > 0 && (
                <StatChip icon={<FileText className="size-3.5 text-gold-text" />}>
                  <span className="font-medium">{mesFiches.length}</span>
                  <span className="text-muted-foreground">
                    {tn("fi.generees", mesFiches.length)}
                  </span>
                </StatChip>
              )}
              {inscriptionCourante && (
                <StatChip icon={<CheckCircle2 className="size-3.5 text-success" />}>
                  <span className="text-muted-foreground">{t("fi.addon_actif")}</span>
                  <span className="font-medium">{formatDateCourte(inscriptionCourante.expires_at)}</span>
                </StatChip>
              )}
            </div>
          </div>

          {/* Accessoire décoratif façon "fiche imprimée", même procédé que la copie
              annotée "18/20" de la page À propos (étiquette or + carte inclinée) -
              un aperçu concret plutôt qu'une simple icône. */}
          <div aria-hidden className="relative mx-auto w-full max-w-[18rem] select-none lg:mx-0 lg:justify-self-end">
            <span className="absolute -top-3 right-6 z-10 rotate-2 rounded-md bg-gold px-3 py-1 text-[0.65rem] font-bold uppercase tracking-wider text-gold-foreground shadow-md">
              {t("fi.pret_imprimer")}
            </span>
            <div className="-rotate-2 rounded-lg border border-border bg-card p-6 shadow-xl transition-transform duration-300 hover:rotate-0">
              <div className="flex items-center gap-2.5">
                <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <FileText className="size-4" />
                </span>
                <div className="min-w-0">
                  <p className="truncate font-display text-sm font-semibold">{t("fi.carte_titre")}</p>
                  <p className="text-xs text-muted-foreground">Terminale C · 10 questions</p>
                </div>
              </div>
              <div className="mt-4 flex flex-col gap-2">
                <div className="h-2 w-full rounded-full bg-muted" />
                <div className="h-2 w-4/5 rounded-full bg-muted" />
                <div className="h-2 w-full rounded-full bg-muted" />
                <div className="h-2 w-3/5 rounded-full bg-muted" />
              </div>
              <div className="my-4 h-px bg-gradient-to-r from-gold/0 via-gold/70 to-gold/0" />
              <div className="flex items-center justify-between text-xs">
                <span className="flex items-center gap-1.5 font-medium text-success">
                  <CheckCircle2 className="size-3.5" />
                  {t("fi.corrige_inclus")}
                </span>
                <span className="flex items-center gap-1.5 text-muted-foreground">
                  <Printer className="size-3.5" />
                  A4
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Pas de lg:items-start : la colonne latérale doit s'étirer sur toute la
          hauteur de la ligne pour servir de bloc contenant au conteneur collant
          qu'elle abrite (sans ça, le collage n'a aucune course utile). */}
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.55fr)_minmax(0,1fr)]">
        {/* min-w-0 : sans lui, une piste de grille vaut min-content et le moindre
            contenu insécable (titre de fiche long, libellé de compétence) élargit la
            colonne au-delà de l'écran - défilement horizontal de toute la page sur
            mobile, constaté à 375px. */}
        <div className="flex min-w-0 flex-col gap-6">
          {fiche && (
            <div ref={resultatRef}>
              <Card className="overflow-hidden border-primary/35 bg-gradient-to-br from-primary/[0.07] via-transparent to-transparent">
                <CardHeader className="flex-row items-start justify-between gap-3 space-y-0">
                  <div className="flex min-w-0 items-start gap-3">
                    <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                      <FileText className="size-5" />
                    </span>
                    <div className="min-w-0">
                      <CardTitle className="font-display text-lg leading-tight">{fiche.titre}</CardTitle>
                      <p className="mt-1 truncate text-sm text-muted-foreground">
                        {fiche.subject_label} - {traduireLibelleSerie(fiche.cursus_display)}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="size-8 shrink-0 text-muted-foreground"
                    onClick={fermerResultat}
                    aria-label={t("fi.fermer_resultat")}
                  >
                    <X className="size-4" />
                  </Button>
                </CardHeader>
                <CardContent className="flex flex-col gap-4" aria-live="polite">
                  {fiche.statut === "EN_COURS" && (
                    <div className="flex flex-col gap-3">
                      <div className="h-1.5 w-full overflow-hidden rounded-full bg-primary/15">
                        <div className="h-full w-1/3 rounded-full bg-primary animate-progress-indeterminate" />
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {t("fi.en_cours_texte")}
                      </p>
                    </div>
                  )}

                  {fiche.statut === "PRETE" && (
                    <>
                      <div className="flex flex-wrap items-center gap-2">
                        <Badge variant="success" className="gap-1">
                          <CheckCircle2 className="size-3" />
                          {t("fi.prete")}
                        </Badge>
                        <Badge variant="outline">
                          {tn("rc.n_questions", fiche.nombre_questions)}
                        </Badge>
                        {fiche.difficulte && <Badge variant="outline">{DIFFICULTE_LABELS[fiche.difficulte]}</Badge>}
                        {fiche.themes.slice(0, 2).map((theme) => (
                          <Badge key={theme} variant="secondary" className="max-w-[14rem] truncate">
                            {theme}
                          </Badge>
                        ))}
                        {fiche.themes.length > 2 && <Badge variant="secondary">+{fiche.themes.length - 2}</Badge>}
                      </div>
                      <div className="grid gap-2 sm:grid-cols-2">
                        <Button onClick={() => downloadFicheSujetPdf(fiche.id)} size="lg">
                          <FileText className="size-4" />
                          {t("fi.enonce_eleves")}
                        </Button>
                        <Button onClick={() => downloadFicheCorrigePdf(fiche.id)} variant="outline" size="lg">
                          <Download className="size-4" />
                          {t("fi.corrige_toi")}
                        </Button>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {t("fi.note_corrige")}
                      </p>
                    </>
                  )}

                  {fiche.statut === "ECHEC" && (
                    <div className="flex flex-col items-start gap-3">
                      <p className="flex items-start gap-1.5 text-sm text-destructive">
                        <AlertCircle className="mt-0.5 size-4 shrink-0" />
                        {t("fi.echec_texte")}
                      </p>
                      <Button variant="outline" size="sm" onClick={handleSubmit} disabled={creating || !pretAGenerer}>
                        <RefreshCw className="size-3.5" />
                        {t("erreur.reessayer")}
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}

          {inscriptions.length === 0 ? (
            <Card className="overflow-hidden border-primary/25 bg-gradient-to-br from-primary/5 via-transparent to-transparent">
              <CardContent className="flex flex-col items-start gap-4 pt-6">
                {/* Le cadenas ne s'affiche que s'il dit vrai : à un répétiteur sans add-on,
                    il nomme un accès à débloquer. Au visiteur déconnecté, il annonçait une
                    interdiction avant même d'avoir dit ce que sont les Fiches - mauvaise
                    première impression pour la seule page qui doit l'expliquer. */}
                <span className="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary ring-4 ring-primary/5">
                  {isAuthenticated ? <Lock className="size-5" /> : <GraduationCap className="size-5" />}
                </span>
                <div>
                  <p className="font-display text-base font-semibold">
                    {isAuthenticated ? t("fi.debloque_addon") : t("fi.comment")}
                  </p>
                  {/* Rien de plus quand la page est publique : le hero au-dessus porte déjà
                      la promesse (et son surtitre dit déjà à qui l'outil s'adresse). La
                      répéter ici, puis une troisième fois en puces, faisait relire au lieu
                      d'avancer. Les étapes ci-dessous disent le "comment", pas le "quoi". */}
                  {isAuthenticated && (
                    <p className="mt-1 text-sm text-muted-foreground">
                      {t("fi.reserve_texte")}
                    </p>
                  )}
                </div>
                <EtapesPresentation
                  etapes={[
                    t("fi.etape1"),
                    t("fi.etape2"),
                    t("fi.etape3"),
                  ]}
                />
                {/* Déconnecté, la connexion passe devant les tarifs : le répétiteur qui
                    arrive ici depuis le QR code d'un corrigé imprimé a déjà l'add-on, il
                    lui manque seulement sa session sur cet appareil. Le w-full va sur le
                    conteneur des deux liens, pas seulement sur le bouton : sous un parent
                    items-start il se rétracterait à la largeur de son contenu, et le
                    w-full du bouton n'aurait plus que ça à remplir (269px au lieu de la
                    pleine largeur, constaté à 375px). */}
                {isAuthenticated ? (
                  <Button asChild size="lg" className="w-full sm:w-auto">
                    <Link to="/tarifs">
                      {t("ft.voir_prix")}
                      <ArrowRight className="size-4" />
                    </Link>
                  </Button>
                ) : (
                  <div className="flex w-full flex-col items-start gap-2">
                    <Button asChild size="lg" className="w-full sm:w-auto">
                      <Link
                        to="/connexion"
                        state={{ from: loginFrom, intent: t("fi.intent") }}
                      >
                        {t("fi.se_connecter")}
                        <ArrowRight className="size-4" />
                      </Link>
                    </Button>
                    <Link to="/tarifs" className="text-sm text-muted-foreground underline-offset-4 hover:underline">
                      {t("fi.pas_addon")}
                    </Link>
                  </div>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle className="font-display text-lg">{t("fi.composer")}</CardTitle>
              </CardHeader>
              <CardContent>
                <ol className="flex flex-col">
                  <Etape numero={1} titre={t("fi.etape_cursus")} fait={Boolean(selectedCursus && selectedSubject)}>
                    <div className="grid gap-4 sm:grid-cols-2">
                      <div className="flex flex-col gap-1.5">
                        <label
                          htmlFor="fiche-cursus"
                          className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
                        >
                          {t("fi.cursus")}
                        </label>
                        <Select value={selectedCursus} onValueChange={setSelectedCursus}>
                          <SelectTrigger id="fiche-cursus">
                            <SelectValue placeholder={t("fi.choisis_cursus")} />
                          </SelectTrigger>
                          <SelectContent>
                            {cursusList.map((c) => {
                              const accessible = inscriptions.some((i) => i.cursus.id === c.id)
                              return (
                                <SelectItem key={c.id} value={String(c.id)}>
                                  <span className="flex items-center gap-2">
                                    {c.examen_display}
                                    {c.series ? t("fi.serie", { code: c.series.code }) : ""}
                                    {!accessible && <Lock className="size-3 text-muted-foreground" />}
                                  </span>
                                </SelectItem>
                              )
                            })}
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="flex flex-col gap-1.5">
                        <label
                          htmlFor="fiche-matiere"
                          className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
                        >
                          {t("fi.matiere")}
                        </label>
                        <Select
                          value={selectedSubject}
                          onValueChange={setSelectedSubject}
                          disabled={!selectedCursus || !hasAccessForCursus || subjects.length === 0}
                        >
                          <SelectTrigger id="fiche-matiere">
                            <SelectValue placeholder={t("fi.choisis_matiere")} />
                          </SelectTrigger>
                          <SelectContent>
                            {subjects.map((subject) => (
                              <SelectItem key={subject.id} value={String(subject.id)}>
                                {subject.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        {/* La liste ne contient que les matières déjà servies : quand
                            elle est vide, le sélecteur désactivé ne dit pas pourquoi. */}
                        {selectedCursus && hasAccessForCursus && subjects.length === 0 && (
                          <p className="text-xs text-muted-foreground">
                            {t("fi.aucune_matiere")}
                          </p>
                        )}
                      </div>
                    </div>

                    {selectedCursus && !hasAccessForCursus && (
                      <div className="flex flex-col items-start gap-3 rounded-xl border border-primary/30 bg-primary/5 p-4">
                        <p className="flex items-start gap-2 text-sm text-muted-foreground">
                          <Lock className="mt-0.5 size-4 shrink-0 text-primary" />
                          {t("fi.addon_inactif")}
                        </p>
                        <Button
                          size="sm"
                          onClick={() => navigate(`/abonnement?cursus=${selectedCursus}&require=repetiteur`)}
                        >
                          {t("fi.debloquer")}
                          <ArrowRight className="size-3.5" />
                        </Button>
                      </div>
                    )}
                  </Etape>

                  <Etape
                    numero={2}
                    titre={t("fi.etape_competences")}
                    aide={t("fi.aide_competences")}
                    fait={selectedThemeIds.size > 0}
                    inactif={!selectedSubject}
                  >
                    {!selectedSubject ? (
                      <p className="text-sm text-muted-foreground">{t("fi.choisis_matiere_dabord")}</p>
                    ) : themesLoading ? (
                      <div className="flex flex-col gap-2">
                        <Skeleton className="h-11 w-full rounded-xl" />
                        <Skeleton className="h-11 w-full rounded-xl" />
                        <Skeleton className="h-11 w-full rounded-xl" />
                      </div>
                    ) : eligibleThemes.length === 0 ? (
                      <p className="rounded-xl border border-dashed border-border px-4 py-6 text-center text-sm text-muted-foreground">
                        {t("fi.aucune_question")}
                      </p>
                    ) : (
                      <>
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <p className="text-sm text-muted-foreground">
                            <span className="font-medium text-foreground">{selectedThemeIds.size}</span>
                            {tn("fi.sur_selection", themesSelectionnables.length)}
                          </p>
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-7 px-2 text-xs"
                              onClick={() => setSelectedThemeIds(new Set(themesSelectionnables.map((t) => t.theme_id)))}
                              disabled={selectedThemeIds.size === themesSelectionnables.length}
                            >
                              {t("fi.tout_selectionner")}
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-7 px-2 text-xs"
                              onClick={() => setSelectedThemeIds(new Set())}
                              disabled={selectedThemeIds.size === 0}
                            >
                              {t("fi.effacer")}
                            </Button>
                          </div>
                        </div>

                        {eligibleThemes.length > SEUIL_RECHERCHE_THEMES && (
                          <div className="relative">
                            <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                            <Input
                              value={themeQuery}
                              onChange={(e) => setThemeQuery(e.target.value)}
                              placeholder={t("fi.filtrer")}
                              className="pl-9"
                              aria-label={t("fi.filtrer_aria")}
                            />
                          </div>
                        )}

                        {/* Pas de hauteur maximale avec défilement interne ici : une
                            zone scrollable imbriquée dans une page déjà scrollable
                            piège la molette entre deux blocs (on croit faire défiler
                            la page, on fait défiler la liste). Les listes longues se
                            réduisent par le champ de filtre juste au-dessus. */}
                        <div className="flex flex-col gap-2">
                          {themesFiltres.length === 0 ? (
                            <p className="py-4 text-center text-sm text-muted-foreground">
                              {t("fi.aucune_competence", { q: themeQuery })}
                            </p>
                          ) : (
                            themesFiltres.map((theme) => {
                              const disponible = disponiblePour(theme)
                              const disabled = disponible === 0
                              const coche = selectedThemeIds.has(theme.theme_id)
                              return (
                                // État coché piloté par le state React plutôt que par
                                // les variantes CSS has-[:checked]/peer-checked : sur
                                // une case contrôlée (React pose la propriété
                                // .checked, jamais l'attribut), l'état visuel dépend
                                // alors d'une réinvalidation de style que le
                                // navigateur n'applique pas toujours - constaté ici,
                                // bordure et coche restées à l'état non coché. La
                                // source de vérité est déjà en JS, autant s'en servir.
                                <label
                                  key={theme.theme_id}
                                  className={cn(
                                    "flex items-center gap-3 rounded-xl border px-3.5 py-2.5 text-sm transition-all",
                                    disabled && "cursor-not-allowed border-border opacity-45",
                                    !disabled && coche && "cursor-pointer border-primary bg-primary/5 shadow-sm",
                                    !disabled &&
                                      !coche &&
                                      "cursor-pointer border-border hover:border-primary/40 hover:bg-accent/40",
                                  )}
                                >
                                  <input
                                    type="checkbox"
                                    checked={coche}
                                    disabled={disabled}
                                    onChange={() => toggleTheme(theme.theme_id)}
                                    aria-label={capitaliserTheme(theme.theme)}
                                    className="peer sr-only"
                                  />
                                  <span
                                    aria-hidden
                                    className={cn(
                                      "flex size-5 shrink-0 items-center justify-center rounded-md border transition-colors peer-focus-visible:ring-2 peer-focus-visible:ring-ring/50",
                                      coche
                                        ? "border-primary bg-primary text-primary-foreground"
                                        : "border-input bg-background text-transparent",
                                    )}
                                  >
                                    <Check className="size-3.5" strokeWidth={3} />
                                  </span>
                                  <span className="min-w-0 flex-1">{capitaliserTheme(theme.theme)}</span>
                                  <span className="shrink-0 rounded-full bg-muted px-2 py-0.5 text-xs tabular-nums text-muted-foreground">
                                    {disponible}
                                  </span>
                                </label>
                              )
                            })
                          )}
                        </div>
                      </>
                    )}
                  </Etape>

                  <Etape
                    numero={3}
                    titre={t("fi.etape_reglages")}
                    fait={selectedThemeIds.size > 0 && maxN > 0}
                    inactif={!selectedSubject || eligibleThemes.length === 0}
                    dernier
                  >
                    <div className="flex flex-col gap-1.5">
                      <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                        {t("fi.difficulte")}
                      </span>
                      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                        {DIFFICULTE_OPTIONS.map((option) => {
                          const actif = difficulte === option
                          const disponible = compterDisponibles(baseComptage, option)
                          return (
                            <button
                              key={option}
                              type="button"
                              onClick={() => setDifficulte(option)}
                              disabled={eligibleThemes.length === 0}
                              aria-pressed={actif}
                              className={cn(
                                "flex flex-col items-start gap-0.5 rounded-xl border px-3 py-2 text-left transition-all disabled:cursor-not-allowed disabled:opacity-50",
                                actif
                                  ? "border-primary bg-primary/5 shadow-sm"
                                  : "border-border hover:border-primary/40 hover:bg-accent/40",
                              )}
                            >
                              <span className="text-sm font-medium">
                                {option === TOUTES_DIFFICULTES ? t("fi.toutes") : DIFFICULTE_LABELS[option]}
                              </span>
                              <span className="text-xs tabular-nums text-muted-foreground">
                                {baseComptage.length === 0
                                  ? "-"
                                  : tn("rc.n_questions", disponible)}
                              </span>
                            </button>
                          )
                        })}
                      </div>
                    </div>

                    <div className="flex flex-col gap-1.5">
                      <label
                        htmlFor="fiche-n"
                        className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
                      >
                        {t("fi.nombre_questions")}{maxN > 0 ? t("fi.max_entre_parentheses", { n: maxN }) : ""}
                      </label>
                      <div className="flex flex-wrap items-center gap-2">
                        <div className="flex items-center gap-1">
                          <Button
                            type="button"
                            variant="outline"
                            size="icon"
                            className="size-10 shrink-0"
                            onClick={() => setN((v) => Math.max(1, v - 1))}
                            disabled={maxN === 0 || n <= 1}
                            aria-label={t("fi.moins")}
                          >
                            <Minus className="size-4" />
                          </Button>
                          <Input
                            id="fiche-n"
                            type="number"
                            min={1}
                            max={maxN || undefined}
                            value={n}
                            onChange={(e) => setN(Math.max(1, Math.min(maxN || 1, Number(e.target.value) || 1)))}
                            disabled={maxN === 0}
                            className="w-16 text-center tabular-nums"
                          />
                          <Button
                            type="button"
                            variant="outline"
                            size="icon"
                            className="size-10 shrink-0"
                            onClick={() => setN((v) => Math.min(maxN, v + 1))}
                            disabled={maxN === 0 || n >= maxN}
                            aria-label={t("fi.plus")}
                          >
                            <Plus className="size-4" />
                          </Button>
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {presetsN.map((valeur) => (
                            <button
                              key={valeur}
                              type="button"
                              onClick={() => setN(valeur)}
                              className={cn(
                                "rounded-full border px-3 py-1.5 text-xs font-medium tabular-nums transition-colors",
                                n === valeur
                                  ? "border-primary bg-primary/10 text-primary"
                                  : "border-border text-muted-foreground hover:border-primary/40 hover:bg-accent/40",
                              )}
                            >
                              {valeur === maxN && maxN > 5 ? t("fi.max_valeur", { n: valeur }) : valeur}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-col gap-1.5">
                      <label
                        htmlFor="fiche-titre"
                        className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
                      >
                        {t("fi.titre_fiche")}
                      </label>
                      <Input
                        id="fiche-titre"
                        value={titre}
                        onChange={(e) => {
                          setTitre(e.target.value)
                          setTitreEdited(true)
                        }}
                        placeholder={t("fi.titre_fiche")}
                      />
                      <p className="text-xs text-muted-foreground">{t("fi.titre_aide")}</p>
                    </div>
                  </Etape>
                </ol>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Récapitulatif ET historique collent ensemble, dans un même conteneur :
            rendre la seule carte du haut collante la faisait glisser par-dessus la
            carte suivante au défilement (un élément collant reste dans le flux, ses
            frères ne se décalent pas) - les deux blocs se chevauchaient. */}
        <aside className="min-w-0">
          <div className="flex flex-col gap-6 lg:sticky lg:top-20">
            {/* Sans add-on, cette colonne ne rendait rien : la présentation occupait 60 %
                de la largeur et les 40 % restants étaient blancs, ce qui se lisait comme
                une page inachevée plutôt que comme une page de présentation. */}
            {inscriptions.length === 0 && <ApercuFichesPdf />}

            {inscriptions.length > 0 && (
              <Card>
                <CardHeader className="pb-4">
                  <CardTitle className="flex items-center gap-2 font-display text-base">
                    <Sparkles className="size-4 text-primary" />
                    {t("fi.recap")}
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col gap-3">
                  <div className="flex flex-col gap-2.5">
                    <LigneRecap label={t("fi.cursus")}>
                      {cursusChoisi ? (
                        <>
                          {cursusChoisi.examen_display}
                          {cursusChoisi.series ? ` - ${cursusChoisi.series.code}` : ""}
                        </>
                      ) : (
                        <RecapVide />
                      )}
                    </LigneRecap>
                    <LigneRecap label={t("fi.matiere")}>
                      {subjectChoisi?.label ?? <RecapVide />}
                    </LigneRecap>
                    <LigneRecap label={t("fi.competences")}>
                      {selectedThemes.length > 0 ? selectedThemes.length : <RecapVide />}
                    </LigneRecap>
                    <LigneRecap label={t("fi.difficulte")}>
                      {difficulte === TOUTES_DIFFICULTES ? t("fi.toutes") : DIFFICULTE_LABELS[difficulte]}
                    </LigneRecap>
                    <LigneRecap label={t("fi.questions")}>
                      {maxN > 0 ? <span className="tabular-nums">{n}</span> : <RecapVide />}
                    </LigneRecap>
                  </div>

                  {selectedThemes.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 border-t border-border pt-3">
                      {selectedThemes.slice(0, 4).map((theme) => (
                        <Badge key={theme.theme_id} variant="secondary" className="max-w-full truncate font-normal">
                          {capitaliserTheme(theme.theme)}
                        </Badge>
                      ))}
                      {selectedThemes.length > 4 && (
                        <Badge variant="outline" className="font-normal">
                          +{selectedThemes.length - 4}
                        </Badge>
                      )}
                    </div>
                  )}

                  {error && (
                    <p className="flex items-start gap-1.5 text-sm text-destructive">
                      <AlertCircle className="mt-0.5 size-4 shrink-0" />
                      {error}
                    </p>
                  )}

                  <div className="h-px bg-gradient-to-r from-gold/0 via-gold/60 to-gold/0" />

                  <Button onClick={handleSubmit} disabled={creating || !pretAGenerer} size="lg" className="w-full">
                    {creating ? (
                      t("pc.preparation")
                    ) : (
                      <>
                        {fiche ? t("fi.generer_nouvelle") : t("fi.generer")}
                        <ArrowRight className="size-4" />
                      </>
                    )}
                  </Button>
                  {!pretAGenerer && (
                    <p className="text-center text-xs text-muted-foreground">
                      {!selectedCursus
                        ? t("fi.indice_cursus")
                        : !hasAccessForCursus
                          ? t("fi.indice_addon")
                          : !selectedSubject
                            ? t("fi.indice_matiere")
                            : t("fi.indice_competence")}
                    </p>
                  )}
                </CardContent>
              </Card>
            )}

            {mesFiches.length > 0 && (
              <Card>
                <CardHeader className="pb-4">
                  <CardTitle className="flex items-center gap-2 font-display text-base">
                    <History className="size-4 text-primary" />
                    {t("fi.mes_fiches")}
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col gap-2">
                  {fichesAffichees.map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center gap-2 rounded-xl border border-border px-3 py-2.5 transition-colors hover:border-primary/40 hover:bg-accent/40"
                    >
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium">{item.titre}</p>
                        <p className="truncate text-xs text-muted-foreground">
                          {item.subject_label} - {tn("rc.n_questions", item.nombre_questions)} -{" "}
                          {formatDateCourte(item.created_at)}
                        </p>
                      </div>
                      {item.statut === "PRETE" ? (
                        <div className="flex shrink-0 gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="size-8"
                            onClick={() => downloadFicheSujetPdf(item.id)}
                            disabled={!item.sujet_pdf_disponible}
                            title={t("fi.ouvrir_enonce")}
                            aria-label={t("fi.ouvrir_enonce_de", { titre: item.titre })}
                          >
                            <FileText className="size-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="size-8"
                            onClick={() => downloadFicheCorrigePdf(item.id)}
                            disabled={!item.corrige_pdf_disponible}
                            title={t("fi.ouvrir_corrige")}
                            aria-label={t("fi.ouvrir_corrige_de", { titre: item.titre })}
                          >
                            <Download className="size-4" />
                          </Button>
                        </div>
                      ) : (
                        <Badge variant={item.statut === "ECHEC" ? "outline" : "secondary"} className="shrink-0">
                          {item.statut === "ECHEC" ? t("fi.echec") : t("fi.en_cours")}
                        </Badge>
                      )}
                    </div>
                  ))}
                  {mesFiches.length > FICHES_RECENTES_VISIBLES && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="w-full"
                      onClick={() => setToutesFichesVisibles((v) => !v)}
                    >
                      {toutesFichesVisibles ? t("fi.reduire") : t("fi.tout_afficher", { n: mesFiches.length })}
                    </Button>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </aside>
      </div>
    </div>
  )
}
