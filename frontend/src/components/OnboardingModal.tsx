import { useEffect, useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"

import { listCursus } from "@/api/endpoints"
import type { Cursus } from "@/api/types"
import { useCountry } from "@/context/CountryContext"
import { catalogueHomePath } from "@/lib/countryPath"
import { examCodesFor } from "@/lib/cursus"
import { countryFlagClassName } from "@/lib/countryFlag"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

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
 * Écran en 3 étapes (pays -> examen -> série) affiché une seule fois, à la première
 * arrivée sur le catalogue d'un pays - avant, un nouveau visiteur devait lui-même
 * trouver les sélecteurs Matière/Cursus pour retrouver son propre programme (voir
 * l'audit UX, reco 1.1). Le résultat final n'est qu'un raccourci vers un filtre
 * `cursus` déjà supporté par CataloguePage, jamais un nouveau mécanisme de filtrage.
 */
export function OnboardingModal() {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const { country, countries, setCountry } = useCountry()

  const [dismissed, setDismissed] = useState(hasCompletedOnboarding)
  const [step, setStep] = useState<Step>("pays")
  const [selectedCountry, setSelectedCountry] = useState(country)
  const [cursusList, setCursusList] = useState<Cursus[]>([])
  const [selectedExamen, setSelectedExamen] = useState<string | null>(null)

  // Comme le sélecteur de pays de l'en-tête (voir Header.tsx) : un Country peut
  // exister en base avant tout contenu réel ingéré, jamais proposé ici.
  const browsableCountries = countries.filter((c) => c.has_lessons)
  const shouldShow = !dismissed && CATALOGUE_HOME_RE.test(pathname) && browsableCountries.length > 0

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
    navigate(`${catalogueHomePath(selectedCountry)}?cursus=${cursus.id}`, { replace: true })
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
  const stepIndex = step === "pays" ? 0 : step === "examen" ? 1 : 2

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
            {[0, 1, 2].map((i) => (
              <span
                key={i}
                className={`h-1 flex-1 rounded-full ${i <= stepIndex ? "bg-primary" : "bg-secondary"}`}
              />
            ))}
          </div>
          <CardTitle className="font-display text-xl font-semibold">
            {step === "pays" && "Dans quel pays prépares-tu ton examen ?"}
            {step === "examen" && "Quel examen prépares-tu ?"}
            {step === "serie" && "Quelle est ta série ?"}
          </CardTitle>
          <CardDescription>Pour n'afficher que ce qui te concerne, dès maintenant.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-2">
          {step === "pays" &&
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

          {step === "examen" &&
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

          {step === "serie" &&
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
