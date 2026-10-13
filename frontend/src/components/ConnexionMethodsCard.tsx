import { useState, type FormEvent } from "react"
import { KeyRound, Mail, Smartphone, Trash2 } from "lucide-react"

import { ApiError } from "@/api/client"
import {
  confirmEmailLink,
  confirmPhoneChange,
  linkGoogle,
  requestEmailLink,
  requestPhoneChange,
  unlinkIdentity,
} from "@/api/endpoints"
import { useAuth } from "@/context/AuthContext"
import { GoogleSignInButton } from "@/components/GoogleSignInButton"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { chiffresNumeroLocal } from "@/lib/telephone"
import { t, useI18n } from "@/lib/i18n"

/** Le nom d'une méthode de connexion rattachée, dans la langue courante. */
function libelleMethode(methode: string): string {
  if (methode === "phone") return t("login.numero")
  if (methode === "email") return t("login.email")
  if (methode === "passkey") return t("secu.passkey")
  if (methode === "google") return "Google"
  if (methode === "apple") return "Apple"
  return methode
}

type Etape = "repos" | "code"

/**
 * « Connexion et sécurité » : les méthodes rattachées au compte, le changement de
 * numéro, et le rattachement d'une seconde méthode.
 *
 * L'encart d'avertissement quand il n'y a qu'une seule méthode n'est pas décoratif :
 * c'est le seul moment où l'on peut encore agir. Une fois la puce perdue avec une
 * unique méthode rattachée, aucune récupération automatique n'est possible sans
 * ouvrir la porte à la prise de contrôle par un numéro recyclé (voir users.account
 * côté backend) - la prévention est donc tout ce qu'on peut offrir.
 */
export function ConnexionMethodsCard() {
  useI18n()
  const { user, updateUser } = useAuth()
  const [etape, setEtape] = useState<Etape>("repos")
  const [nouveauNumero, setNouveauNumero] = useState("")
  const [code, setCode] = useState("")
  // État séparé de celui du changement de numéro : les deux formulaires coexistent sur
  // la carte, et un état partagé ferait basculer l'un en saisissant dans l'autre.
  const [etapeEmail, setEtapeEmail] = useState<Etape>("repos")
  const [emailARattacher, setEmailARattacher] = useState("")
  const [codeEmail, setCodeEmail] = useState("")
  const [erreur, setErreur] = useState<string | null>(null)
  const [succes, setSucces] = useState<string | null>(null)
  const [enCours, setEnCours] = useState(false)

  if (!user) return null

  const methodes = user.auth_methods ?? []
  const seuleMethode = methodes.length <= 1

  function echoue(err: unknown) {
    setErreur(err instanceof ApiError ? err.message : t("login.erreur_generique"))
  }

  async function handleDemande(event: FormEvent) {
    event.preventDefault()
    setErreur(null)
    setSucces(null)

    if (!/^6\d{8}$/.test(nouveauNumero)) {
      setErreur(t("login.erreur_telephone"))
      return
    }

    setEnCours(true)
    try {
      await requestPhoneChange(nouveauNumero)
      setEtape("code")
    } catch (err) {
      echoue(err)
    } finally {
      setEnCours(false)
    }
  }

  async function handleConfirmation(event: FormEvent) {
    event.preventDefault()
    setErreur(null)
    setEnCours(true)
    try {
      updateUser(await confirmPhoneChange(nouveauNumero, code))
      setEtape("repos")
      setNouveauNumero("")
      setCode("")
      setSucces(t("secu.numero_change"))
    } catch (err) {
      echoue(err)
    } finally {
      setEnCours(false)
    }
  }

  async function handleLierGoogle(credential: string) {
    setErreur(null)
    setSucces(null)
    setEnCours(true)
    try {
      updateUser(await linkGoogle(credential))
      setSucces(t("secu.google_lie"))
    } catch (err) {
      echoue(err)
    } finally {
      setEnCours(false)
    }
  }

  async function handleDemandeEmail(event: FormEvent) {
    event.preventDefault()
    setErreur(null)
    setSucces(null)
    setEnCours(true)
    try {
      await requestEmailLink(emailARattacher)
      setEtapeEmail("code")
    } catch (err) {
      echoue(err)
    } finally {
      setEnCours(false)
    }
  }

  async function handleConfirmationEmail(event: FormEvent) {
    event.preventDefault()
    setErreur(null)
    setEnCours(true)
    try {
      updateUser(await confirmEmailLink(emailARattacher, codeEmail))
      setEtapeEmail("repos")
      setEmailARattacher("")
      setCodeEmail("")
      setSucces(t("secu.email_lie"))
    } catch (err) {
      echoue(err)
    } finally {
      setEnCours(false)
    }
  }

  async function handleDetacher(provider: string) {
    // Confirmation native faute de boîte de dialogue partagée dans ce fichier : détacher est
    // une action qui peut enfermer dehors (voir l'encart « une seule méthode » plus bas), un clic
    // sur une icône de corbeille ne doit pas suffire.
    const libelle = libelleMethode(provider)
    if (!window.confirm(t("secu.detacher_confirm", { libelle }))) {
      return
    }
    setErreur(null)
    setSucces(null)
    setEnCours(true)
    try {
      updateUser(await unlinkIdentity(provider))
      setSucces(t("secu.detache", { libelle }))
    } catch (err) {
      echoue(err)
    } finally {
      setEnCours(false)
    }
  }

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 font-display text-lg">
          <KeyRound className="size-4.5 text-primary" />
          {t("secu.titre")}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <ul className="flex flex-col gap-2">
          {methodes.map((methode) => (
            <li
              key={methode}
              className="flex items-center justify-between rounded-lg border px-3 py-2"
            >
              <span className="flex items-center gap-2 text-sm">
                {methode === "email" ? (
                  <Mail className="size-4 text-muted-foreground" />
                ) : (
                  <Smartphone className="size-4 text-muted-foreground" />
                )}
                {libelleMethode(methode)}
                {methode === "phone" && user.phone_number && (
                  <span className="font-mono text-muted-foreground">{user.phone_number}</span>
                )}
                {methode === "email" && user.email && (
                  <span className="truncate text-muted-foreground">{user.email}</span>
                )}
              </span>
              {!seuleMethode && (
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={enCours}
                  onClick={() => handleDetacher(methode)}
                  aria-label={t("secu.detacher_aria", { libelle: libelleMethode(methode) })}
                  className="min-h-11 min-w-11"
                >
                  <Trash2 className="size-4" />
                </Button>
              )}
            </li>
          ))}
        </ul>

        {seuleMethode && (
          <p className="rounded-lg bg-muted px-3 py-2 text-sm text-muted-foreground">
            {t("secu.une_methode")}
          </p>
        )}

        {!methodes.includes("google") && (
          <GoogleSignInButton onCredential={handleLierGoogle} disabled={enCours} />
        )}

        {/* Rien n'est proposé si l'adresse est déjà rattachée : la carte doit lister ce
            qui reste à faire, pas répéter ce qui est fait. Pour CHANGER d'adresse, il
            faut détacher la méthode puis la rattacher à nouveau - même geste que pour
            les autres fournisseurs, et une adresse laissée en place sans identité qui
            la prouve serait réservée pour rien (voir users.account.unlink_identity). */}
        {!methodes.includes("email") && (
          etapeEmail === "repos" ? (
            <form onSubmit={handleDemandeEmail} className="flex flex-col gap-2">
              <Label htmlFor="email-a-rattacher">{t("secu.rattacher_email")}</Label>
              <div className="flex gap-2">
                <Input
                  id="email-a-rattacher"
                  type="email"
                  inputMode="email"
                  autoComplete="email"
                  placeholder={t("login.email_placeholder")}
                  value={emailARattacher}
                  onChange={(event) => setEmailARattacher(event.target.value.trim())}
                />
                <Button type="submit" variant="outline" disabled={enCours}>
                  {enCours ? "..." : t("secu.envoyer_code")}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                {t("secu.email_aide")}
              </p>
            </form>
          ) : (
            <form onSubmit={handleConfirmationEmail} className="flex flex-col gap-2">
              <Label htmlFor="code-email">{t("secu.code_envoye_email", { dest: emailARattacher })}</Label>
              <div className="flex gap-2">
                <Input
                  id="code-email"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  maxLength={6}
                  placeholder="123456"
                  value={codeEmail}
                  onChange={(event) => setCodeEmail(event.target.value.replace(/\D/g, ""))}
                />
                <Button type="submit" disabled={enCours}>
                  {enCours ? "..." : t("secu.confirmer")}
                </Button>
                <Button type="button" variant="ghost" onClick={() => setEtapeEmail("repos")}>
                  {t("seance.annuler")}
                </Button>
              </div>
            </form>
          )
        )}

        {etape === "repos" ? (
          <form onSubmit={handleDemande} className="flex flex-col gap-2">
            <Label htmlFor="nouveau-numero">{t("login.changer_numero")}</Label>
            <div className="flex gap-2">
              <Input
                id="nouveau-numero"
                type="tel"
                inputMode="numeric"
                autoComplete="tel-national"
                placeholder="677123456"
                value={nouveauNumero}
                // Ramène un collage « +237 6… » aux 9 chiffres locaux attendus par l'API.
                onChange={(event) => setNouveauNumero(chiffresNumeroLocal(event.target.value))}
              />
              <Button type="submit" variant="outline" disabled={enCours}>
                {enCours ? "..." : t("secu.envoyer_code")}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              {t("secu.numero_aide")}
            </p>
          </form>
        ) : (
          <form onSubmit={handleConfirmation} className="flex flex-col gap-2">
            <Label htmlFor="code-changement">{t("secu.code_envoye_tel", { dest: nouveauNumero })}</Label>
            <div className="flex gap-2">
              <Input
                id="code-changement"
                inputMode="numeric"
                autoComplete="one-time-code"
                maxLength={6}
                placeholder="123456"
                value={code}
                onChange={(event) => setCode(event.target.value.replace(/\D/g, ""))}
              />
              <Button type="submit" disabled={enCours}>
                {enCours ? "..." : t("secu.confirmer")}
              </Button>
              <Button type="button" variant="ghost" onClick={() => setEtape("repos")}>
                {t("seance.annuler")}
              </Button>
            </div>
          </form>
        )}

        {erreur && <p role="alert" className="text-sm text-destructive">{erreur}</p>}
        {succes && <p role="status" className="text-sm text-primary">{succes}</p>}
      </CardContent>
    </Card>
  )
}
