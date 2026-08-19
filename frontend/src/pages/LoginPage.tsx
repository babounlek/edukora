import { useEffect, useState, type FormEvent } from "react"
import { useNavigate, useLocation } from "react-router-dom"

import { googleSignIn, requestEmailCode, requestOtp, verifyEmailCode, verifyOtp } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { GoogleSignInButton } from "@/components/GoogleSignInButton"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useSeo } from "@/lib/seo"
import { clearReferralCode, consumeReferralCode } from "@/lib/referral"
import { catalogueHomePath } from "@/lib/countryPath"
import { countryFlagClassName } from "@/lib/countryFlag"

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

export function LoginPage() {
  useSeo({ title: "Connexion" })

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
  const [resendCooldownEndsAt, setResendCooldownEndsAt] = useState<number | null>(null)
  const [resendSecondsLeft, setResendSecondsLeft] = useState(0)

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

  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const navigationState = location.state as { from?: string; intent?: string } | null
  const redirectTo = navigationState?.from ?? catalogueHomePath(browsingCountry)
  // Phrase posée par la page d'origine (Quiz, Fiches...) : arriver ici sans savoir
  // pourquoi on demande de se connecter est la première raison d'abandonner.
  // Facultative - les autres entrées vers /connexion n'en passent pas.
  const intent = navigationState?.intent

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
  }

  async function handleRequestCode(event: FormEvent) {
    event.preventDefault()
    setError(null)

    if (methode === "phone" && !/^6\d{8}$/.test(phoneNumber)) {
      setError("Entre un numéro camerounais valide (9 chiffres, commence par 6).")
      return
    }

    setIsSubmitting(true)
    try {
      await envoyerCode()
      setStep("code")
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Une erreur est survenue.")
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleResendCode() {
    setError(null)
    setIsResending(true)
    try {
      await envoyerCode()
    } catch (err) {
      // Le 429 du cooldown serveur (voir OTP_RESEND_COOLDOWN_SECONDS) ne devrait
      // normalement jamais arriver ici tant que le bouton reste grisé pendant le
      // décompte - gardé quand même en filet pour une horloge client désynchronisée.
      setError(err instanceof ApiError ? err.message : "Une erreur est survenue.")
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
      navigate(redirectTo, { replace: true })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Une erreur est survenue.")
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
      navigate(redirectTo, { replace: true })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Une erreur est survenue.")
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
          <CardTitle className="font-display text-2xl">Connexion</CardTitle>
          {/* Ne nomme plus la méthode : cette page ne peut pas savoir si le bouton
              Google s'est affiché (il disparaît de lui-même quand VITE_GOOGLE_CLIENT_ID
              n'est pas configuré), donc toute phrase citant une méthode serait fausse
              dans l'une des deux configurations. Le libellé du champ et celui du bouton
              disent déjà ce qu'il faut faire. */}
          <CardDescription>
            {step === "identifiant"
              ? intent
                ? `${intent} Connecte-toi en quelques secondes.`
                : "Connecte-toi en quelques secondes."
              : `Code envoyé ${methode === "phone" ? "au" : "à"} ${destination}.`}
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
                  <Label htmlFor="phone">Numéro de téléphone</Label>
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
                                +{c.dial_code || "?"} · {c.label}
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
                      autoComplete="off"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value.replace(/\D/g, ""))}
                      maxLength={9}
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
                  <Label htmlFor="email">Adresse e-mail</Label>
                  <Input
                    id="email"
                    type="email"
                    inputMode="email"
                    placeholder="prenom@exemple.com"
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
                  L'inscription par téléphone est disponible uniquement pour les numéros
                  camerounais pour l'instant.
                  {selectedCountry ? ` ${selectedCountry.label} arrive bientôt.` : ""}
                </p>
              ) : (
                error && <p className="text-sm text-destructive">{error}</p>
              )}
              <Button
                type="submit"
                disabled={isSubmitting || (methode === "phone" && !isSupported)}
                className="w-full"
                size="lg"
              >
                {isSubmitting ? "Envoi..." : "Recevoir le code"}
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
                ? "Utiliser plutôt une adresse e-mail"
                : "Utiliser plutôt mon numéro de téléphone"}
            </Button>
          )}
          {step === "code" ? (
            <form onSubmit={handleVerifyCode} className="flex flex-col gap-4">
              <div className="flex flex-col gap-2">
                <Label htmlFor="code">
                  {methode === "phone" ? "Code reçu par SMS" : "Code reçu par e-mail"}
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
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              <Button type="submit" disabled={isSubmitting} className="w-full" size="lg">
                {isSubmitting ? "Vérification..." : "Valider"}
              </Button>
              <Button
                type="button"
                variant="ghost"
                disabled={resendSecondsLeft > 0 || isResending}
                onClick={handleResendCode}
              >
                {resendSecondsLeft > 0
                  ? `Renvoyer le code (${resendSecondsLeft}s)`
                  : isResending
                    ? "Envoi..."
                    : "Renvoyer le code"}
              </Button>
              <Button
                type="button"
                variant="ghost"
                onClick={() => {
                  setStep("identifiant")
                  setCode("")
                  setError(null)
                  setResendCooldownEndsAt(null)
                }}
              >
                {methode === "phone" ? "Changer de numéro" : "Changer d'adresse"}
              </Button>
            </form>
          ) : null}
        </CardContent>
      </Card>
    </div>
  )
}
