import { useEffect, useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"

import { listCursus, updateMe } from "@/api/endpoints"
import type { Cursus } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { epreuvesListPath } from "@/lib/countryPath"
import { memoriserCursusPrepareEnAttente } from "@/lib/cursusPrepare"
import { examCodesFor } from "@/lib/cursus"
import { countryFlagClassName } from "@/lib/countryFlag"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

// Mis en veilleuse le 2026-08-18, rétabli le 2026-09-22 : l'écran ne sert plus
// seulement à préfiltrer le catalogue, il est devenu le seul endroit où un visiteur
// déclare ce qu'il prépare (voir finish -> users.models.User.cursus_prepare). Sans
// lui, le compte à rebours jusqu'à l'examen ne s'affiche que pour les abonnés, dont
// la déclaration est déduite de leur achat - c'est-à-dire pour les seules personnes
// qui n'ont plus besoin d'être convaincues.
const ONBOARDING_ENABLED = true

const ONBOARDING_DONE_KEY = "edukamer_onboarding_done"

// Seule la page d'accueil catalogue d'un pays (/cm, /sn...) déclenche l'onboarding :
// jamais un lien profond partagé (fiche épreuve, corrigé, cours...), qui doit
// atterrir tel quel sans être interrompu par un écran de configuration.
const CATALOGUE_HOME_RE = /^\/[a-z]{2}\/?$/i

type Step = "pays" | "examen" | "serie"

function hasCompletedOnboarding(): boolean {
  try {
    return localStorage.getItem(ONBOARDING_DONE_KEY) === "1"
  } catch {
    return true // navigation privée - ne pas insister à chaque page vue
  }
}

function markOnboardingDone() {
  try {
    localStorage.setItem(ONBOARDING_DONE_KEY, "1")
  } catch {
    // stockage indisponible - tant pis, l'onboarding réapparaîtra simplement
  }
}


/**
 * Écran affiché une seule fois, à la première arrivée sur le catalogue d'un pays -
 * avant, un nouveau visiteur devait lui-même trouver les sélecteurs Matière/Cursus pour
 * retrouver son propre programme (voir l'audit UX, reco 1.1). Le résultat final n'est
 * qu'un raccourci vers un filtre `cursus` déjà supporté par EpreuvesListPage, jamais un
 * nouveau mécanisme de filtrage.
 *
 * Examen -> série, précédés du pays uniquement si plusieurs pays sont réellement
 * ouverts (voir `etapes` plus bas). La série elle-même est sautée pour un diplôme qui
 * n'en a pas, comme le BEPC : le nombre d'étapes s'adapte au référentiel, il n'est
 * jamais fixé d'avance.
 */
export function OnboardingModal() {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const { country, countries, setCountry } = useCountry()
  const { isAuthenticated, updateUser, user } = useAuth()

  // Écarté PENDANT cette visite seulement. La décision durable est portée par
  // `questionReglee` ci-dessous : le compte pour un connecté, le drapeau local pour un
  // visiteur anonyme. Initialiser cet état depuis le drapeau local rendait l'écran
  // définitivement invisible à un élève connecté qui n'avait pourtant rien déclaré.
  const [dismissed, setDismissed] = useState(false)
  const [step, setStep] = useState<Step>("pays")
  const [selectedCountry, setSelectedCountry] = useState(country)
  const [cursusList, setCursusList] = useState<Cursus[]>([])
  const [selectedExamen, setSelectedExamen] = useState<string | null>(null)

  // Comme le sélecteur de pays de l'en-tête (voir Header.tsx) : un Country peut
  // exister en base avant tout contenu réel ingéré, jamais proposé ici.
  const browsableCountries = countries.filter((c) => c.has_lessons)

  /**
   * Pour un utilisateur CONNECTÉ, c'est le serveur qui dit si la question est réglée,
   * pas un drapeau de navigateur : `User.cursus_prepare` renseigné = il a répondu, et
   * l'écran ne réapparaît plus, y compris sur un appareil neuf. Vide = on redemande,
   * même si ce navigateur porte encore le drapeau d'un ancien passage.
   *
   * Sans cette règle, un élève connecté sans cursus déclaré n'avait plus AUCUN chemin
   * pour le dire : l'écran ne revenait jamais (drapeau local posé une fois pour
   * toutes), la page Compte ne propose pas ce réglage, et la séance du jour se tait
   * faute de savoir quel examen il prépare - le coach devenait inatteignable, en
   * silence. Constaté en remettant un compte à zéro pour des tests.
   *
   * Un visiteur anonyme garde le drapeau local : on n'a nulle part d'autre où écrire
   * qu'il a déjà vu cet écran.
   */
  const questionReglee = isAuthenticated ? Boolean(user?.cursus_prepare) : hasCompletedOnboarding()
  const shouldShow =
    ONBOARDING_ENABLED
    && !dismissed
    && !questionReglee
    && CATALOGUE_HOME_RE.test(pathname)
    && browsableCountries.length > 0

  useEffect(() => {
    if (!shouldShow) return
    listCursus(selectedCountry)
      .then(setCursusList)
      .catch(() => setCursusList([]))
  }, [shouldShow, selectedCountry])

  useEffect(() => {
    if (!shouldShow) return
    function handleKey(event: KeyboardEvent) {
      if (event.key === "Escape") close()
    }
    window.addEventListener("keydown", handleKey)
    return () => window.removeEventListener("keydown", handleKey)
  }, [shouldShow])

  function close() {
    markOnboardingDone()
    setDismissed(true)
  }

  function finish(cursus: Cursus) {
    markOnboardingDone()
    setDismissed(true)
    setCountry(selectedCountry)
    declarerCursusPrepare(cursus)
    navigate(`${epreuvesListPath(selectedCountry)}?cursus=${cursus.id}`, { replace: true })
  }

  /**
   * Le choix ne sert plus seulement à préfiltrer la liste d'épreuves : il devient la
   * déclaration "voilà ce que je prépare", sur laquelle repose le compte à rebours.
   *
   * Jamais bloquant - ni attente, ni message d'erreur si l'enregistrement échoue :
   * l'utilisateur a demandé à voir ses épreuves, il les voit. Une déclaration perdue
   * se redemande, une navigation interrompue ne se rattrape pas.
   */
  function declarerCursusPrepare(cursus: Cursus) {
    if (!isAuthenticated) {
      memoriserCursusPrepareEnAttente(cursus.id)
      return
    }
    updateMe({ cursus_prepare: cursus.id })
      .then(updateUser)
      .catch(() => {})
  }

  function handlePickCountry(code: string) {
    // Si le pays choisi est déjà le pays courant, la liste de cursus a déjà été
    // récupérée par l'effet ci-dessus au montage - la vider ici la remettrait à zéro
    // sans jamais la re-remplir, puisque la dépendance `selectedCountry` de cet effet
    // ne changerait pas de valeur.
    if (code !== selectedCountry) {
      setCursusList([])
      setSelectedCountry(code)
    }
    setSelectedExamen(null)
    setStep("examen")
  }

  function handlePickExamen(code: string) {
    setSelectedExamen(code)
    const matches = cursusList.filter((c) => c.examen === code)
    const withSerie = matches.filter((c) => c.series)
    if (withSerie.length === 0) {
      // Pas de série pour ce diplôme (ex. BEPC/BFEM) - un seul cursus possible, on
      // termine directement plutôt que d'imposer une 3e étape sans réel choix.
      if (matches[0]) finish(matches[0])
      return
    }
    setStep("serie")
  }

  if (!shouldShow) return null

  const examOptions = examCodesFor(cursusList)
  const serieOptions = selectedExamen ? cursusList.filter((c) => c.examen === selectedExamen && c.series) : []

  /**
   * L'étape pays n'a de sens qu'avec au moins deux pays ouverts. Tant qu'un seul l'est
   * (le Cameroun au lancement), la demander revient à faire cliquer sur la seule réponse
   * possible - et ce, en plein écran, devant un hero qui annonce déjà "Cameroun" et une
   * URL qui le porte (/cm).
   *
   * Déduite du référentiel plutôt que retirée du code : le jour où un deuxième pays
   * s'ouvre (Country.actif + du contenu publié, voir browsableCountries), l'étape
   * revient d'elle-même, sans que personne n'ait à s'en souvenir. Calculée au rendu et
   * non dans l'état initial : `countries` arrive de l'API après le montage.
   */
  const etapes: Step[] = browsableCountries.length > 1 ? ["pays", "examen", "serie"] : ["examen", "serie"]
  const stepEffectif: Step = step === "pays" && browsableCountries.length <= 1 ? "examen" : step
  const stepIndex = etapes.indexOf(stepEffectif)

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Personnaliser le catalogue"
      className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 p-4 backdrop-blur-sm"
    >
      <Card className="w-full max-w-sm animate-fade-up shadow-lg shadow-primary/10">
        <CardHeader>
          <div className="mb-2 flex gap-1.5">
            {etapes.map((etape, i) => (
              <span
                key={etape}
                className={`h-1 flex-1 rounded-full ${i <= stepIndex ? "bg-primary" : "bg-secondary"}`}
              />
            ))}
          </div>
          <CardTitle className="font-display text-xl font-semibold">
            {stepEffectif === "pays" && "Dans quel pays prépares-tu ton examen ?"}
            {stepEffectif === "examen" && "Quel examen prépares-tu ?"}
            {stepEffectif === "serie" && "Quelle est ta série ?"}
          </CardTitle>
          <CardDescription>Pour n'afficher que ce qui te concerne, dès maintenant.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-2">
          {stepEffectif === "pays" &&
            browsableCountries.map((c) => (
              <button
                key={c.id}
                type="button"
                autoFocus={c.code.toLowerCase() === selectedCountry}
                onClick={() => handlePickCountry(c.code.toLowerCase())}
                className="flex items-center gap-2.5 rounded-md border border-border px-3.5 py-2.5 text-left text-sm font-medium transition-colors hover:border-primary/50 hover:bg-accent/40"
              >
                <span aria-hidden="true" className={countryFlagClassName(c.code)} />
                {c.label}
              </button>
            ))}

          {stepEffectif === "examen" &&
            (examOptions.length === 0 ? (
              <p className="py-4 text-center text-sm text-muted-foreground">Chargement...</p>
            ) : (
              examOptions.map((e, i) => (
                <button
                  key={e.code}
                  type="button"
                  autoFocus={i === 0}
                  onClick={() => handlePickExamen(e.code)}
                  className="rounded-md border border-border px-3.5 py-2.5 text-left text-sm font-medium transition-colors hover:border-primary/50 hover:bg-accent/40"
                >
                  {e.label}
                </button>
              ))
            ))}

          {stepEffectif === "serie" &&
            serieOptions.map((c, i) => (
              <button
                key={c.id}
                type="button"
                autoFocus={i === 0}
                onClick={() => finish(c)}
                className="rounded-md border border-border px-3.5 py-2.5 text-left text-sm font-medium transition-colors hover:border-primary/50 hover:bg-accent/40"
              >
                Série {c.series!.code}
              </button>
            ))}

          <button
            type="button"
            onClick={close}
            className="mt-2 text-center text-sm text-muted-foreground underline-offset-4 transition-colors hover:text-primary hover:underline"
          >
            Je préfère parcourir librement
          </button>
        </CardContent>
      </Card>
    </div>
  )
}
