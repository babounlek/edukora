import { useEffect, useState, type FormEvent } from "react"
import { useNavigate, useLocation } from "react-router-dom"

import { googleSignIn, requestOtp, verifyOtp } from "@/api/endpoints"
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

type Step = "phone" | "code"

/**
 * L'inscription (validation du numéro + paiement Campay) ne gère aujourd'hui que
 * le Cameroun côté backend (voir User.phone_validator et payments/campay_client.py).
 * Le sélecteur d'indicatif ci-dessous est réel, mais la soumission reste bloquée
 * pour tout autre pays tant que ce contrat backend n'est pas étendu.
 */
const SUPPORTED_REGISTRATION_COUNTRIES = ["cm"]

// Miroir du cooldown serveur (voir backend/users/otp_service.py,
// OTP_MIN_INTERVAL_SECONDS) - affiché ici pour éviter qu'un clic prématuré sur
// "Renvoyer le code" ne se solde par une erreur 429 plutôt que par un simple bouton
// grisé avec un décompte. Les deux valeurs peuvent diverger sans casser quoi que ce
// soit (le serveur reste la seule source de vérité, cette constante n'est qu'un
// affichage), juste avec un bouton réactivé un peu trop tôt ou trop tard.
const OTP_RESEND_COOLDOWN_SECONDS = 60

export function LoginPage() {
  useSeo({ title: "Connexion" })

  const { country: browsingCountry, countries } = useCountry()
  const [step, setStep] = useState<Step>("phone")
  const [dialCountry, setDialCountry] = useState(browsingCountry)
  const [phoneNumber, setPhoneNumber] = useState("")
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
  const redirectTo = (location.state as { from?: string } | null)?.from ?? catalogueHomePath(browsingCountry)

  const isSupported = SUPPORTED_REGISTRATION_COUNTRIES.includes(dialCountry)
  const selectedCountry = countries.find((c) => c.code.toLowerCase() === dialCountry)

  async function handleRequestOtp(event: FormEvent) {
    event.preventDefault()
    setError(null)

    if (!/^6\d{8}$/.test(phoneNumber)) {
      setError("Entre un numéro camerounais valide (9 chiffres, commence par 6).")
      return
    }

    setIsSubmitting(true)
    try {
      await requestOtp(phoneNumber)
      setStep("code")
      setResendCooldownEndsAt(Date.now() + OTP_RESEND_COOLDOWN_SECONDS * 1000)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Une erreur est survenue.")
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleResendOtp() {
    setError(null)
    setIsResending(true)
    try {
      await requestOtp(phoneNumber)
      setResendCooldownEndsAt(Date.now() + OTP_RESEND_COOLDOWN_SECONDS * 1000)
    } catch (err) {
      // Le 429 du cooldown serveur (voir OTP_RESEND_COOLDOWN_SECONDS) ne devrait
      // normalement jamais arriver ici tant que le bouton reste grisé pendant le
      // décompte - gardé quand même en filet pour une horloge client désynchronisée.
      setError(err instanceof ApiError ? err.message : "Une erreur est survenue.")
    } finally {
      setIsResending(false)
    }
  }

  async function handleVerifyOtp(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      const response = await verifyOtp(phoneNumber, code, consumeReferralCode())
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

  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4">
      <Card className="w-full max-w-sm animate-fade-up shadow-lg shadow-primary/5">
        <CardHeader>
          <CardTitle className="font-display text-2xl">Connexion</CardTitle>
          <CardDescription>
            {step === "phone"
              ? "Entre ton numéro de téléphone pour recevoir un code."
              : `Code envoyé au ${phoneNumber}.`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {step === "phone" ? (
            <form onSubmit={handleRequestOtp} className="flex flex-col gap-4">
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
                    autoFocus
                    disabled={!isSupported}
                  />
                </div>
              </div>
              {!isSupported ? (
                <p className="text-sm text-muted-foreground">
                  L'inscription est disponible uniquement pour les numéros camerounais pour l'instant.
                  {selectedCountry ? ` ${selectedCountry.label} arrive bientôt.` : ""}
                </p>
              ) : (
                error && <p className="text-sm text-destructive">{error}</p>
              )}
              <Button type="submit" disabled={isSubmitting || !isSupported} className="w-full" size="lg">
                {isSubmitting ? "Envoi..." : "Recevoir le code"}
              </Button>
            </form>
          ) : null}
          {/* Hors du <form> : le bouton Google est rendu par Google et déclenche sa
              propre soumission, l'imbriquer ferait aussi partir la demande d'OTP.
              Volontairement une seule alternative visible en plus du téléphone -
              au-delà de trois boutons, un écran de connexion cesse d'être un choix. */}
          {step === "phone" && (
            <GoogleSignInButton onCredential={handleGoogleCredential} disabled={isSubmitting} withSeparator />
          )}
          {step === "code" ? (
            <form onSubmit={handleVerifyOtp} className="flex flex-col gap-4">
              <div className="flex flex-col gap-2">
                <Label htmlFor="code">Code reçu par SMS</Label>
                <Input
                  id="code"
                  autoComplete="off"
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
                onClick={handleResendOtp}
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
                  setStep("phone")
                  setCode("")
                  setError(null)
                  setResendCooldownEndsAt(null)
                }}
              >
                Changer de numéro
              </Button>
            </form>
          ) : null}
        </CardContent>
      </Card>
    </div>
  )
}
