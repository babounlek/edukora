import { useEffect, useMemo, useRef, useState } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { AlertCircle, CheckCircle2, Download, FileText, Loader2 } from "lucide-react"
import { toast } from "sonner"

import {
  createFiche,
  getFiche,
  getFicheEligibilite,
  downloadFicheCorrigePdf,
  downloadFicheSujetPdf,
  listCursus,
  listMyInscriptionsRepetiteur,
  listSubjects,
} from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { Cursus, Difficulte, Fiche, FicheThemeEligible, InscriptionRepetiteur, Subject } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { trackEvent } from "@/lib/analytics"
import { useSeo } from "@/lib/seo"
import { cn } from "@/lib/utils"

const TOUTES_DIFFICULTES = "toutes"
const DIFFICULTE_LABELS: Record<Difficulte, string> = {
  FAIBLE: "Faible",
  MOYENNE: "Moyenne",
  ELEVEE: "Élevée",
}

// ~2.5s, même ordre de grandeur que le sondage de paiement (SubscribePage) - la
// génération PDF tourne dans un processus détaché (Playwright hors ligne), quelques
// secondes en pratique pour deux PDF courts.
const POLL_INTERVAL_MS = 2500

function defaultTitre(subject: Subject | undefined): string {
  if (!subject) return ""
  const date = new Date().toLocaleDateString("fr-FR", { day: "numeric", month: "long" })
  return `Fiche ${subject.label} - ${date}`
}

export function FichesPage() {
  useSeo({
    title: "Fiches pour répétiteurs",
    description: "L'outil des répétiteurs et enseignants edukora : génère une fiche d'exercices personnalisée, prête à imprimer, pour tes élèves.",
  })

  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const { country } = useCountry()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const [inscriptions, setInscriptions] = useState<InscriptionRepetiteur[]>([])
  const [inscriptionsLoaded, setInscriptionsLoaded] = useState(false)
  const [cursusList, setCursusList] = useState<Cursus[]>([])
  const [selectedCursus, setSelectedCursus] = useState("")
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [selectedSubject, setSelectedSubject] = useState("")
  const [eligibleThemes, setEligibleThemes] = useState<FicheThemeEligible[]>([])
  const [selectedThemeIds, setSelectedThemeIds] = useState<Set<number>>(new Set())
  const [difficulte, setDifficulte] = useState<Difficulte | typeof TOUTES_DIFFICULTES>(TOUTES_DIFFICULTES)
  const [n, setN] = useState(10)
  const [titre, setTitre] = useState("")
  const [titreEdited, setTitreEdited] = useState(false)

  const [creating, setCreating] = useState(false)
  const [error, setError] = useState("")
  const [fiche, setFiche] = useState<Fiche | null>(null)
  const pollRef = useRef<number | null>(null)

  useEffect(() => {
    if (authLoading) return
    if (!isAuthenticated) {
      // searchParams.toString() plutôt que juste "/fiches" : préserve ?ref=pdf_fiche_corrige
      // (posé par le QR code du PDF corrigé, voir fiches.pdf._corrige_deep_link) au retour de
      // connexion - sinon un répétiteur qui scanne son corrigé sans être déjà connecté sur cet
      // appareil perd le paramètre avant même que l'effet de tracking ci-dessous ne le voie.
      const suffix = searchParams.toString()
      navigate("/connexion", { state: { from: suffix ? `/fiches?${suffix}` : "/fiches" } })
      return
    }
    listMyInscriptionsRepetiteur().then((data) => {
      setInscriptions(data.filter((i) => i.is_active))
      setInscriptionsLoaded(true)
    })
    listCursus(country).then(setCursusList)
  }, [authLoading, isAuthenticated, navigate, country, searchParams])

  useEffect(() => {
    // ?ref=pdf_fiche_corrige : posé par le PDF corrigé d'une fiche (voir
    // fiches.pdf._corrige_deep_link) sur son propre CTA - ce PDF reste entre les mains
    // du répétiteur (jamais distribué, voir la mention "réservé à l'usage personnel"
    // dans son template), donc /fiches (générer la prochaine) est la destination
    // pertinente. Seule façon de mesurer combien de répétiteurs reviennent réellement
    // depuis un corrigé imprimé plutôt que de le supposer sans donnée.
    if (!isAuthenticated) return
    if (searchParams.get("ref") !== "pdf_fiche_corrige") return
    trackEvent("pdf_fiche_corrige_landing", {})
  }, [isAuthenticated, searchParams])

  const hasAccessForCursus = inscriptions.some((i) => String(i.cursus.id) === selectedCursus)

  useEffect(() => {
    const cursusObj = cursusList.find((c) => String(c.id) === selectedCursus)
    if (!cursusObj || !hasAccessForCursus) {
      setSubjects([])
      return
    }
    setSelectedSubject("")
    listSubjects(cursusObj.country.code).then(setSubjects)
  }, [selectedCursus, cursusList, hasAccessForCursus])

  useEffect(() => {
    if (!selectedCursus || !selectedSubject) {
      setEligibleThemes([])
      setSelectedThemeIds(new Set())
      return
    }
    getFicheEligibilite(Number(selectedCursus), Number(selectedSubject)).then((themes) => {
      setEligibleThemes(themes)
      setSelectedThemeIds(new Set())
    })
    const subject = subjects.find((s) => String(s.id) === selectedSubject)
    if (!titreEdited) setTitre(defaultTitre(subject))
  }, [selectedCursus, selectedSubject]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current)
    }
  }, [])

  function disponiblePour(theme: FicheThemeEligible): number {
    if (difficulte === TOUTES_DIFFICULTES) return theme.total
    return theme.par_difficulte[difficulte] ?? 0
  }

  const maxN = useMemo(() => {
    return eligibleThemes
      .filter((t) => selectedThemeIds.has(t.theme_id))
      .reduce((sum, t) => sum + (difficulte === TOUTES_DIFFICULTES ? t.total : t.par_difficulte[difficulte] ?? 0), 0)
  }, [eligibleThemes, selectedThemeIds, difficulte])

  useEffect(() => {
    if (maxN > 0 && n > maxN) setN(maxN)
  }, [maxN]) // eslint-disable-line react-hooks/exhaustive-deps

  function toggleTheme(themeId: number) {
    setSelectedThemeIds((prev) => {
      const next = new Set(prev)
      if (next.has(themeId)) next.delete(themeId)
      else next.add(themeId)
      return next
    })
  }

  function pollFiche(ficheId: number) {
    pollRef.current = window.setInterval(async () => {
      try {
        const updated = await getFiche(ficheId)
        if (updated.statut !== "EN_COURS") {
          if (pollRef.current) window.clearInterval(pollRef.current)
          setFiche(updated)
          if (updated.statut === "PRETE") toast.success("Fiche prête", { description: updated.titre })
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
      pollFiche(created.id)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Impossible de générer la fiche pour le moment.")
    } finally {
      setCreating(false)
    }
  }

  function resetForm() {
    if (pollRef.current) window.clearInterval(pollRef.current)
    setFiche(null)
    setError("")
  }

  if (authLoading || !inscriptionsLoaded) {
    return (
      <div className="mx-auto max-w-xl px-4 py-10">
        <Skeleton className="mb-3 h-8 w-32" />
        <Skeleton className="mb-8 h-4 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-xl animate-fade-up px-4 py-10">
      <p className="mb-1 font-display text-sm italic text-primary">Pour les répétiteurs et les enseignants</p>
      <h1 className="mb-1 font-display text-3xl font-semibold">Fiches</h1>
      <p className="mb-8 text-muted-foreground">
        Compose une fiche d'exercices à partir de compétences déjà validées, et obtiens en quelques secondes un PDF
        énoncé (à distribuer à tes élèves) et un PDF corrigé (pour toi) - à ton nom.
      </p>

      {fiche ? (
        <Card>
          <CardHeader>
            <CardTitle className="font-display text-lg">{fiche.titre}</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-5">
            {fiche.statut === "EN_COURS" && (
              <div className="flex flex-col items-center gap-3 py-6 text-center">
                <Loader2 className="size-6 animate-spin text-primary" />
                <p className="text-sm text-muted-foreground">
                  Génération en cours (~15 secondes)... Tu peux rester sur cette page.
                </p>
              </div>
            )}
            {fiche.statut === "PRETE" && (
              <div className="flex flex-col gap-3">
                <p className="flex items-center gap-1.5 text-sm font-medium text-success">
                  <CheckCircle2 className="size-4 shrink-0" />
                  Fiche prête - {fiche.nombre_questions} question{fiche.nombre_questions > 1 ? "s" : ""}
                </p>
                <Button onClick={() => downloadFicheSujetPdf(fiche.id)} size="lg">
                  <FileText className="size-4" />
                  Télécharger l'énoncé (PDF)
                </Button>
                <Button onClick={() => downloadFicheCorrigePdf(fiche.id)} variant="outline" size="lg">
                  <Download className="size-4" />
                  Télécharger le corrigé (PDF)
                </Button>
              </div>
            )}
            {fiche.statut === "ECHEC" && (
              <div className="flex flex-col items-start gap-3">
                <p className="flex items-center gap-1.5 text-sm text-destructive">
                  <AlertCircle className="size-4 shrink-0" />
                  La génération a échoué. Réessaie, ou contacte le support si ça se reproduit.
                </p>
              </div>
            )}
            <Button variant="ghost" onClick={resetForm}>
              Nouvelle fiche
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle className="font-display text-lg">Configure ta fiche</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-5">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Cursus</label>
              <Select value={selectedCursus} onValueChange={setSelectedCursus}>
                <SelectTrigger>
                  <SelectValue placeholder="Choisis le cursus" />
                </SelectTrigger>
                <SelectContent>
                  {cursusList.map((c) => (
                    <SelectItem key={c.id} value={String(c.id)}>
                      {c.examen_display}
                      {c.series ? ` - Série ${c.series.code}` : ""}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {selectedCursus && !hasAccessForCursus && (
              <div className="flex flex-col items-start gap-3 rounded-md border border-primary/30 bg-primary/5 p-4">
                <p className="text-sm text-muted-foreground">
                  L'add-on Fiches n'est pas actif pour ce cursus - débloque-le pour générer des fiches illimitées
                  pendant sa durée.
                </p>
                <Button size="sm" onClick={() => navigate(`/abonnement?cursus=${selectedCursus}&require=repetiteur`)}>
                  Débloquer l'add-on Fiches
                </Button>
              </div>
            )}

            {selectedCursus && hasAccessForCursus && (
              <>
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Matière</label>
                  <Select value={selectedSubject} onValueChange={setSelectedSubject}>
                    <SelectTrigger>
                      <SelectValue placeholder="Choisis la matière" />
                    </SelectTrigger>
                    <SelectContent>
                      {subjects.map((subject) => (
                        <SelectItem key={subject.id} value={String(subject.id)}>
                          {subject.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {selectedSubject && (
                  <>
                    <div className="flex flex-col gap-1.5">
                      <label className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                        Difficulté
                      </label>
                      <Select
                        value={difficulte}
                        onValueChange={(value) => setDifficulte(value as Difficulte | typeof TOUTES_DIFFICULTES)}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value={TOUTES_DIFFICULTES}>Toutes difficultés</SelectItem>
                          {(Object.keys(DIFFICULTE_LABELS) as Difficulte[]).map((d) => (
                            <SelectItem key={d} value={d}>
                              {DIFFICULTE_LABELS[d]}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="flex flex-col gap-1.5">
                      <label className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                        Compétences
                      </label>
                      {eligibleThemes.length === 0 ? (
                        <p className="text-sm text-muted-foreground">
                          Aucune question disponible pour cette matière pour l'instant.
                        </p>
                      ) : (
                        <div className="flex flex-col gap-2">
                          {eligibleThemes.map((theme) => {
                            const disponible = disponiblePour(theme)
                            const disabled = disponible === 0
                            const checked = selectedThemeIds.has(theme.theme_id)
                            return (
                              <label
                                key={theme.theme_id}
                                className={cn(
                                  "flex cursor-pointer items-center justify-between rounded-lg border border-input px-3.5 py-2.5 text-sm transition-colors has-[:checked]:border-primary has-[:checked]:bg-accent",
                                  disabled && "cursor-not-allowed opacity-50",
                                )}
                              >
                                <span className="flex items-center gap-2.5">
                                  <input
                                    type="checkbox"
                                    checked={checked}
                                    disabled={disabled}
                                    onChange={() => toggleTheme(theme.theme_id)}
                                    className="accent-primary"
                                  />
                                  {theme.theme}
                                </span>
                                <span className="text-xs text-muted-foreground">
                                  {disponible} question{disponible > 1 ? "s" : ""}
                                </span>
                              </label>
                            )
                          })}
                        </div>
                      )}
                    </div>

                    <div className="flex flex-col gap-1.5">
                      <label className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                        Nombre de questions{maxN > 0 ? ` (max ${maxN})` : ""}
                      </label>
                      <Input
                        type="number"
                        min={1}
                        max={maxN || undefined}
                        value={n}
                        onChange={(e) => setN(Math.max(1, Number(e.target.value) || 1))}
                        disabled={maxN === 0}
                      />
                    </div>

                    <div className="flex flex-col gap-1.5">
                      <label className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Titre</label>
                      <Input
                        value={titre}
                        onChange={(e) => {
                          setTitre(e.target.value)
                          setTitreEdited(true)
                        }}
                        placeholder="Titre de la fiche"
                      />
                    </div>

                    {error && <p className="text-sm text-destructive">{error}</p>}

                    <Button
                      onClick={handleSubmit}
                      disabled={creating || selectedThemeIds.size === 0 || maxN === 0}
                      size="lg"
                    >
                      {creating ? "Préparation..." : "Générer la fiche"}
                    </Button>
                  </>
                )}
              </>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
