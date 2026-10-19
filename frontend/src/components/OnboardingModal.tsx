import { useEffect, useId, useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { ChevronLeft } from "lucide-react"

import { listCursus, updateMe } from "@/api/endpoints"
import { trackEvent } from "@/lib/analytics"
import { libellePays } from "@/lib/pays"
import type { Cursus } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { catalogueHomePath } from "@/lib/countryPath"
import { memoriserCursusPrepareEnAttente } from "@/lib/cursusPrepare"
import { codeSerieAffiche, estGce, examCodesFor } from "@/lib/cursus"
import { cursusDeLangue } from "@/lib/cursusLangue"
import { langueDeListe } from "@/lib/discipline"
import { useI18n } from "@/lib/i18n"
import { countryFlagClassName } from "@/lib/countryFlag"
import { ChoixMatieres } from "@/components/ChoixMatieres"
import { InviteAutreSousSysteme } from "@/components/InviteAutreSousSysteme"
import { Button } from "@/components/ui/button"
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

type Step = "pays" | "examen" | "serie" | "confirmer" | "matieres"

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
  const { t } = useI18n()
  const langue = langueDeListe("", false)

  // Écarté PENDANT cette visite seulement. La décision durable est portée par
  // `questionReglee` ci-dessous : le compte pour un connecté, le drapeau local pour un
  // visiteur anonyme. Initialiser cet état depuis le drapeau local rendait l'écran
  // définitivement invisible à un élève connecté qui n'avait pourtant rien déclaré.
  const [dismissed, setDismissed] = useState(false)
  const [step, setStep] = useState<Step>("pays")
  const [selectedCountry, setSelectedCountry] = useState(country)
  const [cursusList, setCursusList] = useState<Cursus[]>([])
  // Le pays a-t-il des examens dans l'autre langue ? Conditionne l'invitation à changer de sous-système.
  const [autreSousSysteme, setAutreSousSysteme] = useState(false)
  const [selectedExamen, setSelectedExamen] = useState<string | null>(null)
  // Liste des examens introuvable (panne ou réponse vide) : sans ce signal, l'étape « examen »
  // restait sur « Chargement... » sans issue. `tentative` relance l'effet de chargement.
  const [cursusErreur, setCursusErreur] = useState(false)
  const [tentative, setTentative] = useState(0)
  // GCE général, élève CONNECTÉ : une fois son cursus déclaré, on lui demande ses matières avant de le laisser
  // partir (voir finish). Tant que cet état est posé, la fenêtre reste ouverte même si le compte porte déjà un
  // cursus - c'est ce qui la fermerait sinon (questionReglee).
  const [matieresEnCours, setMatieresEnCours] = useState<Cursus | null>(null)
  const titreId = useId()

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
    && (matieresEnCours !== null || (!questionReglee && CATALOGUE_HOME_RE.test(pathname)))
    && browsableCountries.length > 0

  useEffect(() => {
    if (!shouldShow) return
    let annule = false
    setCursusErreur(false)
    listCursus(selectedCountry)
      .then((toutes) => {
        if (annule) return
        // Les examens de la langue de l'interface seulement (voir lib/cursusLangue) : en anglais le GCE, en
        // français BEPC, Probatoire et BAC. Le visiteur change de langue depuis l'en-tête s'il prépare l'autre.
        const data = cursusDeLangue(toutes, langue)
        setCursusList(data)
        setAutreSousSysteme(toutes.some((c) => c.langue && c.langue !== langue))
        if (data.length === 0) setCursusErreur(true)
      })
      .catch(() => {
        if (annule) return
        setCursusList([])
        setCursusErreur(true)
      })
    return () => {
      annule = true
    }
  }, [shouldShow, selectedCountry, tentative, langue])

  useEffect(() => {
    if (!shouldShow) return
    function handleKey(event: KeyboardEvent) {
      if (event.key === "Escape") close()
    }
    window.addEventListener("keydown", handleKey)
    return () => window.removeEventListener("keydown", handleKey)
  }, [shouldShow])

  // Sert à Échap et au lien « Passer » : on ne redemande pas dans la visite en cours. Pour la
  // suite, tout dépend de `questionReglee` : un visiteur anonyme a posé le drapeau local et ne
  // revoit plus l'écran ; un élève connecté sans cursus déclaré le reverra à sa prochaine visite
  // (le drapeau local ne compte pas pour lui, voir plus haut) - reporter ne lui ferme donc jamais
  // le chemin pour déclarer son examen.
  function close() {
    markOnboardingDone()
    // Pendant le choix des matières, « Passer » / Échap veut dire « plus tard » : le cursus est déjà déclaré.
    if (matieresEnCours) {
      terminer()
      return
    }
    setDismissed(true)
  }

  /**
   * Fin de l'écran : on ferme et l'élève reste sur l'accueil, qui se personnalise d'après son examen
   * (voir useCursusAccueil). Il l'envoyait sur la liste d'épreuves : il n'avait ainsi jamais vu la
   * promesse du site, la réponse à « c'est quoi, ce site ? », avant d'avoir répondu à une question.
   */
  function terminer() {
    setMatieresEnCours(null)
    setDismissed(true)
    navigate(catalogueHomePath(selectedCountry), { replace: true })
  }

  function finish(cursus: Cursus) {
    trackEvent("onboarding_termine", { cursus_id: cursus.id })
    markOnboardingDone()
    setCountry(selectedCountry)
    // Élève connecté de la branche générale du GCE : pas de série qui fixe ses matières, il les choisit. L'API a
    // besoin de son cursus déclaré, donc on le déclare d'abord ; l'élève anonyme ne peut pas encore choisir (le choix
    // se fait après connexion, voir InvitationMatieres sur l'accueil).
    if (isAuthenticated && estGce(cursus) && cursus.series === null) {
      setMatieresEnCours(cursus)
      setStep("matieres")
      updateMe({ cursus_prepare: cursus.id })
        .then(updateUser)
        // Jamais bloquant : si la déclaration échoue, l'élève voit ses épreuves, comme avant.
        .catch(() => terminer())
      return
    }
    setDismissed(true)
    declarerCursusPrepare(cursus)
    navigate(catalogueHomePath(selectedCountry), { replace: true })
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
    // GCE : la branche générale n'a pas de série, la technique en a une - il faut donc choisir la
    // branche, y compris la générale, que le simple filtre « avec série » laisserait de côté.
    if (withSerie.length > 0 && matches.length > withSerie.length) {
      setStep("serie")
      return
    }
    if (withSerie.length === 0) {
      // Pas de série pour ce diplôme (ex. BEPC/BFEM) - un seul cursus possible, donc
      // pas de choix à faire, mais on ne termine pas sur un simple clic : ici finish()
      // règle la question pour de bon (écran marqué "fait", cursus déclaré) et un
      // élève sans abonnement n'a ensuite aucun endroit pour corriger. Une
      // confirmation, avec retour possible, coûte un clic de plus au bon choix.
      if (matches[0]) setStep("confirmer")
      return
    }
    setStep("serie")
  }

  function handleBack(precedent: Step) {
    // `selectedExamen` est conservé : revenir à "examen" doit montrer le choix qu'on
    // vient de faire, pas un écran vierge. Seul le choix de pays le réinitialise
    // (voir handlePickCountry), puisqu'un autre pays n'a pas les mêmes examens.
    setStep(precedent)
  }

  if (!shouldShow) return null

  const examOptions = examCodesFor(cursusList)
  const serieOptions = selectedExamen
    ? cursusList.filter((c) => {
        if (c.examen !== selectedExamen) return false
        // Une branche sans série n'est proposée que si l'examen en a aussi avec série (GCE).
        return c.series || cursusList.some((autre) => autre.examen === selectedExamen && autre.series)
      })
    : []

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
  const stepEffectif: Step = step === "pays" && browsableCountries.length <= 1 ? "examen" : step
  // La dernière étape est la série, ou la confirmation pour un diplôme qui n'en a pas.
  const derniereEtape: Step = stepEffectif === "confirmer" ? "confirmer" : "serie"
  // Un élève connecté du GCE a une étape de plus : ses matières (voir finish).
  const avecMatieres = stepEffectif === "matieres" || (isAuthenticated && estGce(selectedExamen ? { examen: selectedExamen } : null))
  const etapes: Step[] = [
    ...(browsableCountries.length > 1 ? (["pays"] as Step[]) : []),
    "examen",
    derniereEtape,
    ...(avecMatieres ? (["matieres"] as Step[]) : []),
  ]
  const stepIndex = etapes.indexOf(stepEffectif)
  const etapePrecedente = stepIndex > 0 ? etapes[stepIndex - 1] : null
  const cursusConfirme = selectedExamen ? cursusList.find((c) => c.examen === selectedExamen) : undefined

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby={titreId}
      className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 p-4 backdrop-blur-sm"
    >
      <Card className="w-full max-w-sm animate-fade-up shadow-lg shadow-primary/10">
        <CardHeader>
          {etapePrecedente && (
            <button
              type="button"
              onClick={() => handleBack(etapePrecedente)}
              className="-ml-1 mb-1 flex min-h-11 items-center gap-1 self-start text-sm text-muted-foreground transition-colors hover:text-primary"
            >
              <ChevronLeft aria-hidden="true" className="size-4" />
              {t("onboarding.retour")}
            </button>
          )}
          <div className="mb-2 flex gap-1.5">
            {etapes.map((etape, i) => (
              <span
                key={etape}
                className={`h-1 flex-1 rounded-full ${i <= stepIndex ? "bg-primary" : "bg-secondary"}`}
              />
            ))}
          </div>
          <CardTitle id={titreId} className="font-display text-xl font-semibold">
            {stepEffectif === "pays" && t("onboarding.titre_pays")}
            {stepEffectif === "examen" && t("onboarding.titre_examen")}
            {stepEffectif === "serie" && t("onboarding.titre_serie")}
            {stepEffectif === "matieres" && t("onboarding.titre_matieres")}
            {stepEffectif === "confirmer" &&
              t("onboarding.titre_confirmer", { examen: cursusConfirme?.examen_display ?? t("onboarding.diplome_choisi") })}
          </CardTitle>
          <CardDescription>
            {t("onboarding.description")}
          </CardDescription>
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
                {libellePays(c.code, c.label)}
              </button>
            ))}

          {stepEffectif === "examen" &&
            (examOptions.length === 0 ? (
              cursusErreur ? (
                <div role="alert" className="flex flex-col items-center gap-2 py-2 text-center">
                  <p className="text-sm text-muted-foreground">
                    {t("onboarding.erreur_examens")}
                  </p>
                  <div className="flex flex-wrap justify-center gap-2">
                    <Button size="sm" className="min-h-11 rounded-full" onClick={() => setTentative((n) => n + 1)}>
                      {t("erreur.reessayer")}
                    </Button>
                    {/* Sans markOnboardingDone : c'est la panne qui empêche de répondre, pas un
                        refus - la question doit revenir à la prochaine visite. */}
                    <Button size="sm" variant="ghost" className="min-h-11 rounded-full" onClick={() => setDismissed(true)}>
                      {t("onboarding.passer")}
                    </Button>
                  </div>
                </div>
              ) : (
                <p className="py-4 text-center text-sm text-muted-foreground">{t("onboarding.chargement")}</p>
              )
            ) : (
              examOptions.map((e, i) => (
                <button
                  key={e.code}
                  type="button"
                  autoFocus={selectedExamen ? e.code === selectedExamen : i === 0}
                  onClick={() => handlePickExamen(e.code)}
                  className="rounded-md border border-border px-3.5 py-2.5 text-left text-sm font-medium transition-colors hover:border-primary/50 hover:bg-accent/40"
                >
                  {e.label}
                </button>
              ))
            ))}

          {/* Un élève de l'autre sous-système ne voit pas son examen dans cette liste : l'invitation le
              lui dit, au lieu de le laisser chercher le sélecteur de langue. Sans effet sur la déclaration :
              la page est rechargée dans l'autre langue et cette fenêtre y revient. */}
          {stepEffectif === "examen" && <InviteAutreSousSysteme disponible={autreSousSysteme} variante="bloc" />}

          {stepEffectif === "serie" &&
            serieOptions.map((c, i) => (
              <button
                key={c.id}
                type="button"
                autoFocus={i === 0}
                onClick={() => finish(c)}
                className="rounded-md border border-border px-3.5 py-2.5 text-left text-sm font-medium transition-colors hover:border-primary/50 hover:bg-accent/40"
              >
                {c.series ? (c.series.code.startsWith("GCE_") ? codeSerieAffiche(c.series) : t("prix.serie", { code: c.series.code })) : t("onboarding.branche_generale")}
              </button>
            ))}

          {stepEffectif === "confirmer" && cursusConfirme && (
            <button
              type="button"
              autoFocus
              onClick={() => finish(cursusConfirme)}
              className="rounded-md border border-primary bg-primary px-3.5 py-2.5 text-left text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
            >
              {t("onboarding.confirmer")}
            </button>
          )}

          {stepEffectif === "matieres" && matieresEnCours && (
            // Le cursus vient d'être déclaré : tant que le compte ne le porte pas, ChoixMatieres n'a rien à interroger.
            user?.cursus_prepare?.id === matieresEnCours.id ? (
              <>
                <ChoixMatieres onEnregistre={() => terminer()} />
                <Button className="min-h-11 rounded-full" onClick={() => terminer()}>
                  {t("onboarding.continuer")}
                </Button>
              </>
            ) : (
              <p className="py-4 text-center text-sm text-muted-foreground">{t("onboarding.chargement")}</p>
            )
          )}

          {/* Pas pendant l'erreur de chargement : « Passer » y fait déjà la même chose. */}
          {!(stepEffectif === "examen" && examOptions.length === 0 && cursusErreur) && (
            <button
              type="button"
              onClick={close}
              className="mt-1 min-h-11 self-center px-3 text-sm text-muted-foreground underline-offset-4 transition-colors hover:text-primary hover:underline"
            >
              {t("onboarding.passer")}
            </button>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
