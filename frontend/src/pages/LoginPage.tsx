import { useState, type FormEvent } from "react"
import { useNavigate, useLocation } from "react-router-dom"

import { requestOtp, verifyOtp } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
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

type Step = "phone" | "code"

/**
 * L'inscription (validation du numéro + paiement Campay) ne gère aujourd'hui que
 * le Cameroun côté backend (voir User.phone_validator et payments/campay_client.py).
 * Le sélecteur d'indicatif ci-dessous est réel, mais la soumission reste bloquée
 * pour tout autre pays tant que ce contrat backend n'est pas étendu.
 */
const SUPPORTED_REGISTRATION_COUNTRIES = ["cm"]

export function LoginPage() {
  useSeo({ title: "Connexion" })

  const { country: browsingCountry, countries } = useCountry()
  const [step, setStep] = useState<Step>("phone")
  const [dialCountry, setDialCountry] = useState(browsingCountry)
  const [phoneNumber, setPhoneNumber] = useState("")
  const [code, setCode] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

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
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Une erreur est survenue.")
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleVerifyOtp(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      const response = await verifyOtp(phoneNumber, code, consumeReferralCode())
      clearReferralCode()
      login(response.access, response.refresh, response.user)
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
                      <SelectTrigger className="w-[92px] shrink-0">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {countries.map((c) => (
                          <SelectItem key={c.id} value={c.code.toLowerCase()}>
                            +{c.dial_code || "?"}
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
          ) : (
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
                onClick={() => {
                  setStep("phone")
                  setCode("")
                  setError(null)
                }}
              >
                Changer de numéro
              </Button>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
