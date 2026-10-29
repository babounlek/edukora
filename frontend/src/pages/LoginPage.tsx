import { useEffect, useState, type FormEvent } from "react"
import { Link, useNavigate, useLocation } from "react-router-dom"

import { googleSignIn, listProfils, requestEmailCode, requestOtp, verifyEmailCode, verifyOtp } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { User } from "@/api/types"
import { dureeAttente } from "@/lib/messagesEnvoiCode"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { GoogleSignInButton } from "@/components/GoogleSignInButton"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useSeo } from "@/lib/seo"
import { libellePays } from "@/lib/pays"
import { clearReferralCode, consumeReferralCode } from "@/lib/referral"
import { destinationApresConnexion, ouvrirDestination } from "@/lib/apresConnexion"
import { countryFlagClassName } from "@/lib/countryFlag"
import { chiffresNumeroLocal } from "@/lib/telephone"
import { SITE_NAME } from "@/lib/site"
import { langueCourante, t, urlAnglaiseExplicite, useI18n } from "@/lib/i18n"

type Step = "identifiant" | "code"

/**
 * Canal par lequel le code est demandé puis vérifié. Google n'en fait pas partie : il
 * n'envoie aucun code et ouvre la session en un seul aller-retour, il n'a donc pas
 * d'étape "code" à traverser.
 */
type Methode = "phone" | "email"

/**
 * L'inscription (validation du numéro + paiement Campay) ne gère aujourd'hui que
 * le Cameroun côté backend (voir User.phone_validator et payments/campay_client.py).
 * Le sélecteur d'indicatif ci-dessous est réel, mais la soumission reste bloquée
 * pour tout autre pays tant que ce contrat backend n'est pas étendu.
 */
const SUPPORTED_REGISTRATION_COUNTRIES = ["cm"]

// Miroir du cooldown serveur (voir backend/users/otp_service.py,
// OTP_MIN_INTERVAL_SECONDS, et son équivalent EMAIL_CODE_MIN_INTERVAL_SECONDS côté
// e-mail - les deux valent 60 s) - affiché ici pour éviter qu'un clic prématuré sur
// "Renvoyer le code" ne se solde par une erreur 429 plutôt que par un simple bouton
// grisé avec un décompte. Les deux valeurs peuvent diverger sans casser quoi que ce
// soit (le serveur reste la seule source de vérité, cette constante n'est qu'un
// affichage), juste avec un bouton réactivé un peu trop tôt ou trop tard.
const OTP_RESEND_COOLDOWN_SECONDS = 60

// Miroir de OTP_VALIDITY_MINUTES / EMAIL_CODE_VALIDITY_MINUTES (backend/users/
// otp_service.py et email_service.py, les deux valent 5) - affiché sous le champ code
// pour ne pas laisser le décompte du cooldown ci-dessus (60s) passer pour la durée de
// vie du code : ce sont deux minuteurs différents, et seul celui-ci correspond à ce
// que dit réellement le mail/SMS reçu.
const OTP_CODE_VALIDITY_MINUTES = 5

// Au-delà, l'envoi du code (e-mail ou SMS, réalisé par un tiers) est annoncé comme un peu long.
const ENVOI_LENT_APRES_MS = 3000

export function LoginPage() {
  useI18n()
  useSeo({ title: t("login.seo") })

  const { country: browsingCountry, countries } = useCountry()
  const [step, setStep] = useState<Step>("identifiant")
  // E-mail par défaut, téléphone derrière la bascule : c'est le seul levier qui
  // fasse réellement baisser la facture SMS. Un canal se facture au message, pas à
  // la méthode - le supprimer n'économise rien, mais cesser de le proposer en
  // premier fait que la plupart des gens ne l'empruntent plus. L'OTP reste entier,
  // à un clic, pour qui n'a pas d'adresse ou ne la relève pas.
  const [methode, setMethode] = useState<Methode>("email")
  const [dialCountry, setDialCountry] = useState(browsingCountry)
  const [phoneNumber, setPhoneNumber] = useState("")
  const [email, setEmail] = useState("")
  const [code, setCode] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isResending, setIsResending] = useState(false)
  // Vrai quand l'élève est passé à l'étape "code" sans en demander un nouveau ici
  // (bouton "J'ai déjà un code") : l'en-tête ne doit alors pas affirmer qu'un code
  // vient d'être envoyé.
  const [codeDejaRecu, setCodeDejaRecu] = useState(false)
  const [resendCooldownEndsAt, setResendCooldownEndsAt] = useState<number | null>(null)
  const [resendSecondsLeft, setResendSecondsLeft] = useState(0)
  // Quand le code a été demandé ICI (pas avec « J'ai déjà un code », dont on ignore l'heure) : de quoi dire qu'il a expiré.
  const [codeEnvoyeLe, setCodeEnvoyeLe] = useState<number | null>(null)
  const [codeExpire, setCodeExpire] = useState(false)
  // Envoi qui traîne : le bouton restait en « Envoi… » une douzaine de secondes sans un mot (test élève Gogo).
  const [envoiLent, setEnvoiLent] = useState(false)

  // Recalcule chaque seconde plutôt qu'un simple setTimeout unique : la valeur
  // affichée doit rester correcte même si l'onglet passe en arrière-plan un moment
  // (throttling des timers navigateur) - se base sur l'horodatage cible
  // (resendCooldownEndsAt), jamais sur un compteur décrémenté à l'aveugle.
  useEffect(() => {
    if (!resendCooldownEndsAt) return
    const tick = () => setResendSecondsLeft(Math.max(0, Math.ceil((resendCooldownEndsAt - Date.now()) / 1000)))
    tick()
    const interval = setInterval(tick, 1000)
    return () => clearInterval(interval)
  }, [resendCooldownEndsAt])

  useEffect(() => {
    setCodeExpire(false)
    if (!codeEnvoyeLe) return
    const reste = codeEnvoyeLe + OTP_CODE_VALIDITY_MINUTES * 60_000 - Date.now()
    if (reste <= 0) {
      setCodeExpire(true)
      return
    }
    const minuteur = setTimeout(() => setCodeExpire(true), reste)
    return () => clearTimeout(minuteur)
  }, [codeEnvoyeLe])

  const envoiEnCours = (isSubmitting && step === "identifiant") || isResending
  useEffect(() => {
    if (!envoiEnCours) {
      setEnvoiLent(false)
      return
    }
    const minuteur = setTimeout(() => setEnvoiLent(true), ENVOI_LENT_APRES_MS)
    return () => clearTimeout(minuteur)
  }, [envoiEnCours])

  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const navigationState = location.state as { from?: string; intent?: string } | null
  const demandee = navigationState?.from
  // Phrase posée par la page d'origine (Quiz, Fiches...) : arriver ici sans savoir
  // pourquoi on demande de se connecter est la première raison d'abandonner.
  // Facultative - les autres entrées vers /connexion n'en passent pas.
  const intent = navigationState?.intent

  // Après une connexion réussie : direct vers la destination, sauf si le compte a
  // déjà déclaré 2+ enfants, auquel cas "Qui étudie ?" s'intercale une fois (voir
  // QuiEtudiePage.tsx) - comportement inchangé pour l'immense majorité des comptes
  // (un seul profil).
  async function naviguerApresConnexion(user: User, sessionEnfant = false) {
    // Destination, langue et pays se décident sur le compte qui vient de répondre, pas sur ce que le navigateur
    // affichait avant la connexion (voir lib/apresConnexion.ts).
    const destination = destinationApresConnexion({
      user,
      demandee,
      paysNavigation: browsingCountry,
      courante: langueCourante(),
      urlExplicite: urlAnglaiseExplicite(),
    })
    let versChoixDuProfil = false
    // Session ouverte par l'enfant avec son propre numéro : un seul profil possible, jamais « Qui étudie ? ».
    if (!sessionEnfant) {
      try {
        versChoixDuProfil = (await listProfils()).length > 1
      } catch {
        // Impossible de savoir : on part sur le chemin normal plutôt que de bloquer une
        // connexion qui vient de réussir pour un aléa secondaire.
      }
    }
    if (versChoixDuProfil) {
      navigate("/qui-etudie", { state: { from: destination.chemin }, replace: true })
      return
    }
    // Rechargement direct sur la destination si la langue du cursus l'exige, au lieu de laisser la synchronisation de
    // langue recharger /connexion.
    ouvrirDestination(destination, navigate)
  }

  const isSupported = SUPPORTED_REGISTRATION_COUNTRIES.includes(dialCountry)
  const selectedCountry = countries.find((c) => c.code.toLowerCase() === dialCountry)

  /** Ce à quoi le code a été envoyé, tel qu'on le réaffiche à l'étape suivante. */
  const destination = methode === "phone" ? phoneNumber : email

  async function envoyerCode() {
    if (methode === "phone") {
      await requestOtp(phoneNumber)
    } else {
      await requestEmailCode(email)
    }
    setResendCooldownEndsAt(Date.now() + OTP_RESEND_COOLDOWN_SECONDS * 1000)
    setCodeEnvoyeLe(Date.now())
  }

  /** Contrôle local de l'identifiant saisi ; renvoie le message d'erreur, ou null. */
  function erreurIdentifiant(): string | null {
    if (methode === "phone" && !/^6\d{8}$/.test(phoneNumber)) {
      return t("login.erreur_telephone")
    }
    if (methode === "email" && !/^\S+@\S+\.\S+$/.test(email)) {
      return t("login.erreur_email")
    }
    return null
  }

  // Saute l'envoi : pour qui a déjà reçu un code (encore valable 5 minutes) et a
  // perdu la page en allant le chercher dans sa messagerie - fréquent dans le
  // navigateur intégré de WhatsApp, qui recharge la page au retour. Redemander un code
  // l'obligerait à attendre le cooldown serveur et invaliderait celui qu'il tient.
  function passerAvecCodeExistant() {
    const message = erreurIdentifiant()
    if (message) {
      setError(message)
      return
    }
    setError(null)
    setCodeDejaRecu(true)
    setStep("code")
  }

  async function handleRequestCode(event: FormEvent) {
    event.preventDefault()
    setError(null)

    const message = erreurIdentifiant()
    if (message) {
      setError(message)
      return
    }

    setIsSubmitting(true)
    try {
      await envoyerCode()
      setCodeDejaRecu(false)
      setStep("code")
    } catch (err) {
      armerAttenteApresEchec(err)
      setError(err instanceof ApiError ? err.message : t("login.erreur_generique"))
    } finally {
      setIsSubmitting(false)
    }
  }

  /**
   * Après un échec d'envoi (429 trop tôt, 503 service en panne) : le bouton « Renvoyer » reste grisé avec un
   * décompte, pour la durée que donne le serveur. Un renvoi tenté aussitôt serait refusé (test élève 2026-10-24 :
   * le bouton se réactivait dès l'échec, le clic suivant donnait un 429).
   */
  function armerAttenteApresEchec(err: unknown) {
    if (!(err instanceof ApiError) || (err.status !== 429 && err.status !== 503)) return
    setResendCooldownEndsAt(Date.now() + (err.retryAfter ?? OTP_RESEND_COOLDOWN_SECONDS) * 1000)
  }

  async function handleResendCode() {
    setError(null)
    setIsResending(true)
    try {
      await envoyerCode()
    } catch (err) {
      armerAttenteApresEchec(err)
      setError(err instanceof ApiError ? err.message : t("login.erreur_generique"))
    } finally {
      setIsResending(false)
    }
  }

  async function handleVerifyCode(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      const referral = consumeReferralCode()
      const response = methode === "phone"
        ? await verifyOtp(phoneNumber, code, referral)
        : await verifyEmailCode(email, code, referral)
      clearReferralCode()
      login(response.access, response.user)
      await naviguerApresConnexion(response.user, response.user.session_restreinte)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("login.erreur_generique"))
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleGoogleCredential(credential: string) {
    setError(null)
    setIsSubmitting(true)
    try {
      const response = await googleSignIn(credential, consumeReferralCode())
      clearReferralCode()
      login(response.access, response.user)
      await naviguerApresConnexion(response.user)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("login.erreur_generique"))
    } finally {
      setIsSubmitting(false)
    }
  }

  function basculerMethode() {
    setMethode(methode === "phone" ? "email" : "phone")
    setError(null)
  }

  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4">
      <Card className="w-full max-w-sm animate-fade-up shadow-lg shadow-primary/5">
        <CardHeader>
          <h1 className="font-display text-2xl font-semibold leading-none tracking-tight">{t("login.titre")}</h1>
          {/* Ne nomme plus la méthode : cette page ne peut pas savoir si le bouton
              Google s'est affiché (il disparaît de lui-même quand VITE_GOOGLE_CLIENT_ID
              n'est pas configuré), donc toute phrase citant une méthode serait fausse
              dans l'une des deux configurations. Le libellé du champ et celui du bouton
              disent déjà ce qu'il faut faire. */}
          <CardDescription>
            {step === "identifiant"
              ? intent
                ? t("login.description_intent", { intent })
                : t("login.description")
              : codeDejaRecu
                ? t("login.code_recu_pour", { destination })
                : t(methode === "phone" ? "login.code_envoye_tel" : "login.code_envoye_email", { destination })}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* En premier, et hors du <form> : le bouton est rendu par Google et déclenche
              sa propre soumission, l'imbriquer ferait aussi partir la demande de code.

              Ordre des trois méthodes, arrêté après essai des variantes : Google, puis
              e-mail, puis téléphone. Google d'abord parce qu'il est le seul à ouvrir la
              session sans code à recopier, en un geste sur un Android déjà connecté.
              L'e-mail ensuite parce qu'il ne coûte rien lui non plus et qu'il fonctionne
              là où Google échoue - le bouton ne s'affiche pas dans le navigateur intégré
              de WhatsApp, d'où arrive une bonne part du trafic. Le SMS en dernier, seul
              canal facturé : il reste entier et atteignable en un clic, parce que le
              retirer n'économiserait rien (un SMS se facture au message, pas à la
              méthode) et enfermerait dehors les comptes qui n'ont que lui. */}
          {step === "identifiant" && (
            <GoogleSignInButton onCredential={handleGoogleCredential} disabled={isSubmitting} withSeparator />
          )}
          {step === "identifiant" ? (
            <form onSubmit={handleRequestCode} className="flex flex-col gap-4">
              {methode === "phone" ? (
                <div className="flex flex-col gap-2">
                  <Label htmlFor="phone">{t("login.numero")}</Label>
                  <div className="flex gap-2">
                    {countries.length > 0 && (
                      <Select value={dialCountry} onValueChange={setDialCountry}>
                        <SelectTrigger className="w-[108px] shrink-0">
                          {/* Replié : drapeau + indicatif seulement (place limitée à côté
                              du numéro). Liste ouverte : + le nom du pays - avec 14 pays,
                              l'indicatif seul ("+221") ne dit rien à personne. */}
                          <SelectValue>
                            <span className="flex items-center gap-1.5">
                              <span aria-hidden className={countryFlagClassName(dialCountry)} />
                              +{selectedCountry?.dial_code || "?"}
                            </span>
                          </SelectValue>
                        </SelectTrigger>
                        <SelectContent>
                          {countries.map((c) => (
                            <SelectItem key={c.id} value={c.code.toLowerCase()}>
                              <span className="flex items-center gap-1.5">
                                <span aria-hidden className={countryFlagClassName(c.code)} />
                                +{c.dial_code || "?"} · {libellePays(c.code, c.label)}
                              </span>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    )}
                    <Input
                      id="phone"
                      inputMode="numeric"
                      placeholder="677123456"
                      type="tel"
                      autoComplete="tel-national"
                      value={phoneNumber}
                      // Pas de maxLength : il tronquait un collage « +237 6… » ; le helper retire
                      // l'indicatif et ramène à 9 chiffres (format attendu par l'API).
                      onChange={(e) => setPhoneNumber(chiffresNumeroLocal(e.target.value))}
                      // Pas d'autoFocus : sur mobile il ouvre le clavier et fait défiler
                      // la carte, ce qui pousserait hors de l'écran le bouton Google
                      // placé juste au-dessus - exactement ce qu'on cherche à mettre en
                      // avant. L'autoFocus reste sur le champ code, où il est utile.
                      disabled={!isSupported}
                    />
                  </div>
                </div>
              ) : (
                <div className="flex flex-col gap-2">
                  <Label htmlFor="email">{t("login.email")}</Label>
                  <Input
                    id="email"
                    type="email"
                    inputMode="email"
                    placeholder={t("login.email_placeholder")}
                    // Le seul champ de cette page où l'autocomplétion du navigateur aide
                    // vraiment : une adresse se retape mal sur un clavier de téléphone,
                    // et une faute de frappe ici envoie le code dans le vide sans que
                    // rien ne le signale (l'endpoint ne dit jamais si l'adresse existe).
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value.trim())}
                  />
                </div>
              )}
              {methode === "phone" && !isSupported ? (
                <p className="text-sm text-muted-foreground">
                  {t("login.tel_cameroun_seulement")}
                  {selectedCountry ? t("login.pays_bientot", { pays: libellePays(selectedCountry.code, selectedCountry.label) }) : ""}
                </p>
              ) : (
                error && <p role="alert" className="text-sm text-destructive">{error}</p>
              )}
              <Button
                type="submit"
                disabled={isSubmitting || (methode === "phone" && !isSupported)}
                className="w-full"
                size="lg"
              >
                {isSubmitting ? t("login.envoi") : t("login.recevoir_code")}
              </Button>
              {envoiLent && (
                <p role="status" className="text-center text-xs text-muted-foreground">
                  {t("login.envoi_lent")}
                </p>
              )}
              <p className="text-center text-xs text-muted-foreground">
                {t("login.cgu_avant")}{" "}
                <Link to="/cgu" className="underline underline-offset-4 hover:text-primary">
                  {t("login.cgu_lien")}
                </Link>{" "}
                {t("login.cgu_et")}{" "}
                <Link to="/confidentialite" className="underline underline-offset-4 hover:text-primary">
                  {t("login.confidentialite_lien")}
                </Link>
                .
              </p>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="-mt-2 w-full"
                disabled={isSubmitting || (methode === "phone" && !isSupported)}
                onClick={passerAvecCodeExistant}
              >
                {t("login.deja_code")}
              </Button>
            </form>
          ) : null}
          {/* Tout en bas, et volontairement discrète dans les deux sens : elle donne accès
              à une méthode de repli, pas à un choix qu'on demande à l'élève de trancher.
              Le numéro reste atteignable en un clic - c'est l'identifiant que connaissent
              ceux qui n'ont ni compte Google ni adresse relevée, et le seul que portent
              tous les comptes créés avant cette refonte. */}
          {step === "identifiant" && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="mt-3 w-full"
              onClick={basculerMethode}
            >
              {methode === "phone"
                ? t("login.utiliser_email")
                : t("login.utiliser_tel")}
            </Button>
          )}
          {step === "code" ? (
            <form onSubmit={handleVerifyCode} className="flex flex-col gap-4">
              <div className="flex flex-col gap-2">
                <Label htmlFor="code">
                  {methode === "phone" ? t("login.code_sms") : t("login.code_email")}
                </Label>
                <Input
                  id="code"
                  autoComplete="one-time-code"
                  inputMode="numeric"
                  placeholder="123456"
                  value={code}
                  onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
                  maxLength={6}
                  autoFocus
                />
                <p className="text-xs text-muted-foreground">
                  {t("login.code_validite", { n: OTP_CODE_VALIDITY_MINUTES })}
                </p>
                {/* Où chercher : l'écran du code ne disait ni la boîte à regarder ni de qui vient le message (test élève Gogo). */}
                <p className="text-xs text-muted-foreground">
                  {t(methode === "phone" ? "login.pas_recu_tel" : "login.pas_recu_email", { site: SITE_NAME })}
                </p>
              </div>
              {codeExpire && (
                <p role="alert" className="text-sm text-destructive">
                  {t("login.code_expire")}
                </p>
              )}
              {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
              {/* Désactivé tant que le code est incomplet : un envoi à 3 chiffres ne pouvait
                  que revenir en erreur (le code fait toujours 6 chiffres). */}
              <Button type="submit" disabled={isSubmitting || code.length < 6} className="w-full" size="lg">
                {isSubmitting ? t("login.verification") : t("login.valider")}
              </Button>
              <Button
                type="button"
                variant="ghost"
                disabled={resendSecondsLeft > 0 || isResending}
                onClick={handleResendCode}
              >
                {resendSecondsLeft >= 120
                  ? t("login.renvoyer_dans", { duree: dureeAttente(resendSecondsLeft) })
                  : resendSecondsLeft > 0
                  ? t("login.renvoyer_attente", { s: resendSecondsLeft })
                  : isResending
                    ? t("login.envoi")
                    : t("login.renvoyer")}
              </Button>
              {isResending && envoiLent && (
                <p role="status" className="text-center text-xs text-muted-foreground">
                  {t("login.envoi_lent")}
                </p>
              )}
              <Button
                type="button"
                variant="ghost"
                onClick={() => {
                  setStep("identifiant")
                  setCode("")
                  setError(null)
                  setResendCooldownEndsAt(null)
                  setCodeEnvoyeLe(null)
                }}
              >
                {methode === "phone" ? t("login.changer_numero") : t("login.changer_adresse")}
              </Button>
            </form>
          ) : null}
        </CardContent>
      </Card>
    </div>
  )
}
