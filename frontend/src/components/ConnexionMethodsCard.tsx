import { useState, type FormEvent } from "react"
import { KeyRound, Smartphone, Trash2 } from "lucide-react"

import { ApiError } from "@/api/client"
import {
  confirmPhoneChange,
  linkGoogle,
  requestPhoneChange,
  unlinkIdentity,
} from "@/api/endpoints"
import { useAuth } from "@/context/AuthContext"
import { GoogleSignInButton } from "@/components/GoogleSignInButton"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

const LIBELLES: Record<string, string> = {
  phone: "Numéro de téléphone",
  google: "Google",
  apple: "Apple",
  email: "Adresse e-mail",
  passkey: "Clé d'accès",
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
  const { user, updateUser } = useAuth()
  const [etape, setEtape] = useState<Etape>("repos")
  const [nouveauNumero, setNouveauNumero] = useState("")
  const [code, setCode] = useState("")
  const [erreur, setErreur] = useState<string | null>(null)
  const [succes, setSucces] = useState<string | null>(null)
  const [enCours, setEnCours] = useState(false)

  if (!user) return null

  const methodes = user.auth_methods ?? []
  const seuleMethode = methodes.length <= 1

  function echoue(err: unknown) {
    setErreur(err instanceof ApiError ? err.message : "Une erreur est survenue.")
  }

  async function handleDemande(event: FormEvent) {
    event.preventDefault()
    setErreur(null)
    setSucces(null)

    if (!/^6\d{8}$/.test(nouveauNumero)) {
      setErreur("Entre un numéro camerounais valide (9 chiffres, commence par 6).")
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
      setSucces("Ton numéro a bien été changé.")
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
      setSucces("Google est maintenant rattaché à ton compte.")
    } catch (err) {
      echoue(err)
    } finally {
      setEnCours(false)
    }
  }

  async function handleDetacher(provider: string) {
    setErreur(null)
    setSucces(null)
    setEnCours(true)
    try {
      updateUser(await unlinkIdentity(provider))
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
          Connexion et sécurité
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
                <Smartphone className="size-4 text-muted-foreground" />
                {LIBELLES[methode] ?? methode}
                {methode === "phone" && user.phone_number && (
                  <span className="font-mono text-muted-foreground">{user.phone_number}</span>
                )}
              </span>
              {!seuleMethode && (
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={enCours}
                  onClick={() => handleDetacher(methode)}
                  aria-label={`Détacher ${LIBELLES[methode] ?? methode}`}
                >
                  <Trash2 className="size-4" />
                </Button>
              )}
            </li>
          ))}
        </ul>

        {seuleMethode && (
          <p className="rounded-lg bg-muted px-3 py-2 text-sm text-muted-foreground">
            Tu n'as qu'une seule méthode de connexion. Si tu perds ce moyen d'accès, ton
            compte et ton abonnement seront perdus avec lui. Rattache Google maintenant,
            pendant que tu as encore accès à ton compte.
          </p>
        )}

        {!methodes.includes("google") && (
          <GoogleSignInButton onCredential={handleLierGoogle} disabled={enCours} />
        )}

        {etape === "repos" ? (
          <form onSubmit={handleDemande} className="flex flex-col gap-2">
            <Label htmlFor="nouveau-numero">Changer de numéro</Label>
            <div className="flex gap-2">
              <Input
                id="nouveau-numero"
                inputMode="numeric"
                placeholder="677123456"
                value={nouveauNumero}
                onChange={(event) => setNouveauNumero(event.target.value)}
              />
              <Button type="submit" variant="outline" disabled={enCours}>
                {enCours ? "..." : "Envoyer le code"}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Le code part vers le nouveau numéro : garde-le à portée de main.
            </p>
          </form>
        ) : (
          <form onSubmit={handleConfirmation} className="flex flex-col gap-2">
            <Label htmlFor="code-changement">Code envoyé au {nouveauNumero}</Label>
            <div className="flex gap-2">
              <Input
                id="code-changement"
                inputMode="numeric"
                maxLength={6}
                placeholder="123456"
                value={code}
                onChange={(event) => setCode(event.target.value)}
              />
              <Button type="submit" disabled={enCours}>
                {enCours ? "..." : "Confirmer"}
              </Button>
              <Button type="button" variant="ghost" onClick={() => setEtape("repos")}>
                Annuler
              </Button>
            </div>
          </form>
        )}

        {erreur && <p className="text-sm text-destructive">{erreur}</p>}
        {succes && <p className="text-sm text-primary">{succes}</p>}
      </CardContent>
    </Card>
  )
}
