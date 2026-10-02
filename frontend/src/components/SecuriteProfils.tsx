import { useState, type FormEvent } from "react"
import { KeyRound, Loader2, Lock, ShieldAlert, ShieldCheck, Smartphone } from "lucide-react"

import {
  confirmerConnexionProfil,
  definirPinParent,
  definirPinProfil,
  demanderConnexionProfil,
  retirerPinParent,
  retirerPinProfil,
  supprimerConnexionProfil,
} from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { Profil } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { ChampPin } from "@/components/PinDialogs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

function messageErreur(err: unknown, defaut: string): string {
  return err instanceof ApiError ? err.message : defaut
}

/** Petit formulaire « code à 4 chiffres » (avec le code actuel pour modifier/retirer le code parent). */
function FormulairePin({
  titre,
  avecActuel = false,
  soumettre,
  annuler,
}: {
  titre: string
  avecActuel?: boolean
  soumettre: (pin: string, actuel?: string) => Promise<void>
  annuler: () => void
}) {
  const [pin, setPin] = useState("")
  const [actuel, setActuel] = useState("")
  const [envoi, setEnvoi] = useState(false)
  const [erreur, setErreur] = useState<string | null>(null)

  async function valider(e: FormEvent) {
    e.preventDefault()
    if (pin.length !== 4 || (avecActuel && actuel.length !== 4)) return
    setEnvoi(true)
    setErreur(null)
    try {
      await soumettre(pin, avecActuel ? actuel : undefined)
    } catch (err) {
      setErreur(messageErreur(err, "Enregistrement impossible."))
      setEnvoi(false)
    }
  }

  return (
    <form onSubmit={valider} className="mt-2 flex flex-col gap-2.5 rounded-lg border border-border bg-muted/30 p-3">
      <p className="text-xs font-medium text-muted-foreground">{titre}</p>
      {avecActuel && <ChampPin id="pin-actuel" label="Code actuel" value={actuel} onChange={setActuel} />}
      <ChampPin id="pin-nouveau" label="Nouveau code" value={pin} onChange={setPin} autoFocus={!avecActuel} />
      {avecActuel && <p className="text-xs text-muted-foreground">Code actuel en haut, nouveau code en bas.</p>}
      {erreur && <p role="alert" className="text-xs text-destructive">{erreur}</p>}
      <div className="flex gap-2">
        <Button type="button" variant="outline" size="sm" onClick={annuler}>
          Annuler
        </Button>
        <Button type="submit" size="sm" disabled={envoi || pin.length !== 4 || (avecActuel && actuel.length !== 4)}>
          {envoi ? <Loader2 className="size-4 animate-spin" /> : "Enregistrer"}
        </Button>
      </div>
    </form>
  )
}

/** Retrait du code parent : demande le code actuel. */
function RetraitPinParent({ soumettre, annuler }: { soumettre: (actuel: string) => Promise<void>; annuler: () => void }) {
  const [actuel, setActuel] = useState("")
  const [envoi, setEnvoi] = useState(false)
  const [erreur, setErreur] = useState<string | null>(null)

  async function valider(e: FormEvent) {
    e.preventDefault()
    if (actuel.length !== 4) return
    setEnvoi(true)
    setErreur(null)
    try {
      await soumettre(actuel)
    } catch (err) {
      setErreur(messageErreur(err, "Retrait impossible."))
      setEnvoi(false)
    }
  }

  return (
    <form onSubmit={valider} className="mt-2 flex flex-col gap-2.5 rounded-lg border border-border bg-muted/30 p-3">
      <p className="text-xs font-medium text-muted-foreground">Saisis le code parent actuel pour le retirer.</p>
      <ChampPin id="pin-retrait" label="Code parent actuel" value={actuel} onChange={setActuel} autoFocus />
      {erreur && <p role="alert" className="text-xs text-destructive">{erreur}</p>}
      <div className="flex gap-2">
        <Button type="button" variant="outline" size="sm" onClick={annuler}>
          Annuler
        </Button>
        <Button type="submit" size="sm" disabled={envoi || actuel.length !== 4}>
          {envoi ? <Loader2 className="size-4 animate-spin" /> : "Retirer le code"}
        </Button>
      </div>
    </form>
  )
}

/** Numéro personnel de l'enfant : un code lui est envoyé, le parent le saisit pour confirmer. */
function FormulaireConnexionEnfant({
  profil,
  onDone,
  annuler,
}: {
  profil: Profil
  onDone: (profil: Profil) => void
  annuler: () => void
}) {
  const [numero, setNumero] = useState("")
  const [code, setCode] = useState("")
  const [etape, setEtape] = useState<"numero" | "code">("numero")
  const [envoi, setEnvoi] = useState(false)
  const [erreur, setErreur] = useState<string | null>(null)

  async function envoyer(e: FormEvent) {
    e.preventDefault()
    if (!/^6\d{8}$/.test(numero)) {
      setErreur("Entre un numéro valide (9 chiffres, commence par 6).")
      return
    }
    setEnvoi(true)
    setErreur(null)
    try {
      await demanderConnexionProfil(profil.id, numero)
      setEtape("code")
    } catch (err) {
      setErreur(messageErreur(err, "Envoi impossible."))
    } finally {
      setEnvoi(false)
    }
  }

  async function confirmer(e: FormEvent) {
    e.preventDefault()
    if (!/^\d{6}$/.test(code)) return
    setEnvoi(true)
    setErreur(null)
    try {
      onDone(await confirmerConnexionProfil(profil.id, numero, code))
    } catch (err) {
      setErreur(messageErreur(err, "Code invalide."))
      setEnvoi(false)
    }
  }

  return (
    <div className="mt-2 flex flex-col gap-2.5 rounded-lg border border-border bg-muted/30 p-3">
      {etape === "numero" ? (
        <form onSubmit={envoyer} className="flex flex-col gap-2.5">
          <p className="text-xs text-muted-foreground">
            Numéro de téléphone de {profil.prenom || "l'enfant"}. Un code de vérification lui est envoyé par SMS ; avec
            ce numéro, il pourra se connecter lui-même, sur son profil uniquement.
          </p>
          <Input
            aria-label="Numéro de l'enfant"
            inputMode="numeric"
            placeholder="677123456"
            maxLength={9}
            value={numero}
            onChange={(e) => setNumero(e.target.value.replace(/\D/g, ""))}
            autoFocus
          />
          {erreur && <p role="alert" className="text-xs text-destructive">{erreur}</p>}
          <div className="flex gap-2">
            <Button type="button" variant="outline" size="sm" onClick={annuler}>
              Annuler
            </Button>
            <Button type="submit" size="sm" disabled={envoi || numero.length !== 9}>
              {envoi ? <Loader2 className="size-4 animate-spin" /> : "Envoyer le code"}
            </Button>
          </div>
        </form>
      ) : (
        <form onSubmit={confirmer} className="flex flex-col gap-2.5">
          <p className="text-xs text-muted-foreground">Saisis le code à 6 chiffres reçu par SMS sur le numéro de l'enfant.</p>
          <Input
            aria-label="Code reçu par SMS"
            inputMode="numeric"
            autoComplete="one-time-code"
            placeholder="123456"
            maxLength={6}
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
            autoFocus
          />
          {erreur && <p role="alert" className="text-xs text-destructive">{erreur}</p>}
          <div className="flex gap-2">
            <Button type="button" variant="outline" size="sm" onClick={annuler}>
              Annuler
            </Button>
            <Button type="submit" size="sm" disabled={envoi || code.length !== 6}>
              {envoi ? <Loader2 className="size-4 animate-spin" /> : "Confirmer"}
            </Button>
          </div>
        </form>
      )}
    </div>
  )
}

type ActionOuverte =
  | { type: "pin-parent" }
  | { type: "retrait-pin-parent" }
  | { type: "pin-profil"; id: number }
  | { type: "connexion"; id: number }
  | null

/**
 * Sécurité des profils : code parent (facultatif), code PIN de chaque enfant et connexion
 * personnelle d'un enfant qui a son téléphone. Tout est facultatif - sans rien définir, rien
 * ne change. Les actions du compte, une fois un code parent défini, demandent ce code (le
 * serveur le réclame, voir api/client.ts) ; une session ouverte par l'enfant n'a pas accès à
 * cette section.
 */
export function SecuriteProfils({
  profils,
  onProfilChange,
}: {
  profils: Profil[]
  onProfilChange: (profil: Profil) => void
}) {
  const { user, updateUser } = useAuth()
  const [ouverte, setOuverte] = useState<ActionOuverte>(null)
  const [erreur, setErreur] = useState<string | null>(null)

  if (!user || user.session_restreinte) return null

  const parentActif = user.pin_parent_actif
  const aucunPin = !parentActif && profils.every((p) => !p.pin_actif)
  const plusieurs = profils.length > 1

  async function action(fn: () => Promise<void>) {
    setErreur(null)
    try {
      await fn()
      setOuverte(null)
    } catch (err) {
      setErreur(messageErreur(err, "Action impossible."))
    }
  }

  return (
    <div className="flex flex-col gap-4">
      {plusieurs && aucunPin && (
        <div className="flex items-start gap-2.5 rounded-lg border border-gold/30 bg-gold/[0.06] px-3.5 py-3 text-sm">
          <ShieldAlert className="mt-0.5 size-4 shrink-0 text-gold-text" />
          <p>
            Aujourd'hui, n'importe qui sur cet appareil peut ouvrir le profil d'un autre enfant. Pour protéger chaque
            profil, ajoute un code à 4 chiffres (facultatif) - tu peux aussi définir un code parent pour réserver
            paiements et gestion des enfants.
          </p>
        </div>
      )}

      {erreur && <p role="alert" className="text-sm text-destructive">{erreur}</p>}

      <div className="rounded-xl border border-border p-3.5">
        <div className="flex items-center gap-2">
          <ShieldCheck className="size-4 shrink-0 text-primary" />
          <p className="flex-1 font-display text-sm font-semibold">Code parent</p>
          <span className="text-xs text-muted-foreground">{parentActif ? "Activé" : "Non défini"}</span>
        </div>
        <p className="mt-1 text-xs text-muted-foreground">
          Réserve au parent les paiements, l'ajout d'enfants et la gestion des codes. Il ouvre aussi n'importe quel
          profil si un code enfant est oublié.
        </p>
        <div className="mt-2 flex flex-wrap gap-2">
          <Button
            size="sm"
            variant="outline"
            className="h-8 rounded-full text-xs"
            onClick={() => setOuverte({ type: "pin-parent" })}
          >
            {parentActif ? "Modifier le code" : "Définir un code parent"}
          </Button>
          {parentActif && (
            <Button
              size="sm"
              variant="ghost"
              className="h-8 rounded-full text-xs"
              onClick={() => setOuverte({ type: "retrait-pin-parent" })}
            >
              Retirer
            </Button>
          )}
        </div>
        {ouverte?.type === "pin-parent" && (
          <FormulairePin
            titre={parentActif ? "Choisis un nouveau code parent à 4 chiffres." : "Choisis un code parent à 4 chiffres."}
            avecActuel={parentActif}
            annuler={() => setOuverte(null)}
            soumettre={(pin, actuel) =>
              action(async () => updateUser(await definirPinParent(pin, actuel)))
            }
          />
        )}
        {ouverte?.type === "retrait-pin-parent" && (
          <RetraitPinParent
            annuler={() => setOuverte(null)}
            soumettre={(actuel) => action(async () => updateUser(await retirerPinParent(actuel)))}
          />
        )}
      </div>

      {profils.map((profil) => (
        <div key={profil.id} className="rounded-xl border border-border p-3.5">
          <p className="font-display text-sm font-semibold">{profil.prenom || "Profil sans nom"}</p>

          <div className="mt-2 flex items-center gap-2">
            <KeyRound className="size-4 shrink-0 text-muted-foreground" />
            <p className="flex-1 text-sm">Code du profil</p>
            <span className="text-xs text-muted-foreground">{profil.pin_actif ? "Activé" : "Aucun"}</span>
            <Button
              size="sm"
              variant="outline"
              className="h-8 rounded-full text-xs"
              onClick={() => setOuverte({ type: "pin-profil", id: profil.id })}
            >
              {profil.pin_actif ? "Modifier" : "Ajouter"}
            </Button>
            {profil.pin_actif && (
              <Button
                size="sm"
                variant="ghost"
                className="h-8 rounded-full text-xs"
                onClick={() => action(async () => onProfilChange(await retirerPinProfil(profil.id)))}
              >
                Retirer
              </Button>
            )}
          </div>
          {ouverte?.type === "pin-profil" && ouverte.id === profil.id && (
            <FormulairePin
              titre={`Choisis un code à 4 chiffres pour ${profil.prenom || "ce profil"}.`}
              annuler={() => setOuverte(null)}
              soumettre={(pin) => action(async () => onProfilChange(await definirPinProfil(profil.id, pin)))}
            />
          )}

          <div className="mt-2 flex items-center gap-2">
            <Smartphone className="size-4 shrink-0 text-muted-foreground" />
            <p className="flex-1 text-sm">Connexion avec son propre téléphone</p>
            <span className="text-xs text-muted-foreground">{profil.connexion_active ? "Activée" : "Aucune"}</span>
            {profil.connexion_active ? (
              <Button
                size="sm"
                variant="ghost"
                className="h-8 rounded-full text-xs"
                onClick={() => action(async () => onProfilChange(await supprimerConnexionProfil(profil.id)))}
              >
                Retirer
              </Button>
            ) : (
              <Button
                size="sm"
                variant="outline"
                className="h-8 rounded-full text-xs"
                onClick={() => setOuverte({ type: "connexion", id: profil.id })}
              >
                Ajouter
              </Button>
            )}
          </div>
          {ouverte?.type === "connexion" && ouverte.id === profil.id && (
            <FormulaireConnexionEnfant
              profil={profil}
              annuler={() => setOuverte(null)}
              onDone={(maj) => {
                onProfilChange(maj)
                setOuverte(null)
              }}
            />
          )}
          {profil.connexion_active && (
            <p className="mt-1 flex items-center gap-1.5 text-xs text-muted-foreground">
              <Lock className="size-3 shrink-0" />
              Depuis sa propre connexion, l'enfant ne voit que son profil : pas de changement d'enfant, ni de
              paiement.
            </p>
          )}
        </div>
      ))}
    </div>
  )
}
