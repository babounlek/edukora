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
import { t, useI18n } from "@/lib/i18n"

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
      setErreur(messageErreur(err, t("sp.enregistrement_erreur")))
      setEnvoi(false)
    }
  }

  return (
    <form onSubmit={valider} className="mt-2 flex flex-col gap-2.5 rounded-lg border border-border bg-muted/30 p-3">
      <p className="text-xs font-medium text-muted-foreground">{titre}</p>
      {avecActuel && <ChampPin id="pin-actuel" label={t("sp.code_actuel")} value={actuel} onChange={setActuel} />}
      <ChampPin id="pin-nouveau" label={t("sp.nouveau_code")} value={pin} onChange={setPin} autoFocus={!avecActuel} />
      {avecActuel && <p className="text-xs text-muted-foreground">{t("sp.actuel_haut")}</p>}
      {erreur && <p role="alert" className="text-xs text-destructive">{erreur}</p>}
      <div className="flex gap-2">
        <Button type="button" variant="outline" size="sm" onClick={annuler}>
          {t("seance.annuler")}
        </Button>
        <Button type="submit" size="sm" disabled={envoi || pin.length !== 4 || (avecActuel && actuel.length !== 4)}>
          {envoi ? <Loader2 className="size-4 animate-spin" /> : t("matieres.enregistrer")}
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
      setErreur(messageErreur(err, t("sp.retrait_erreur")))
      setEnvoi(false)
    }
  }

  return (
    <form onSubmit={valider} className="mt-2 flex flex-col gap-2.5 rounded-lg border border-border bg-muted/30 p-3">
      <p className="text-xs font-medium text-muted-foreground">{t("sp.retrait_texte")}</p>
      <ChampPin id="pin-retrait" label={t("sp.code_parent_actuel")} value={actuel} onChange={setActuel} autoFocus />
      {erreur && <p role="alert" className="text-xs text-destructive">{erreur}</p>}
      <div className="flex gap-2">
        <Button type="button" variant="outline" size="sm" onClick={annuler}>
          {t("seance.annuler")}
        </Button>
        <Button type="submit" size="sm" disabled={envoi || actuel.length !== 4}>
          {envoi ? <Loader2 className="size-4 animate-spin" /> : t("sp.retirer_code")}
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
      setErreur(t("sp.numero_invalide"))
      return
    }
    setEnvoi(true)
    setErreur(null)
    try {
      await demanderConnexionProfil(profil.id, numero)
      setEtape("code")
    } catch (err) {
      setErreur(messageErreur(err, t("sp.envoi_erreur")))
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
      setErreur(messageErreur(err, t("sp.code_invalide")))
      setEnvoi(false)
    }
  }

  return (
    <div className="mt-2 flex flex-col gap-2.5 rounded-lg border border-border bg-muted/30 p-3">
      {etape === "numero" ? (
        <form onSubmit={envoyer} className="flex flex-col gap-2.5">
          <p className="text-xs text-muted-foreground">
            {t("sp.numero_texte", { nom: profil.prenom || t("sp.l_enfant") })}
          </p>
          <Input
            aria-label={t("sp.numero_aria")}
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
              {t("seance.annuler")}
            </Button>
            <Button type="submit" size="sm" disabled={envoi || numero.length !== 9}>
              {envoi ? <Loader2 className="size-4 animate-spin" /> : t("secu.envoyer_code")}
            </Button>
          </div>
        </form>
      ) : (
        <form onSubmit={confirmer} className="flex flex-col gap-2.5">
          <p className="text-xs text-muted-foreground">{t("sp.code_sms_texte")}</p>
          <Input
            aria-label={t("login.code_sms")}
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
              {t("seance.annuler")}
            </Button>
            <Button type="submit" size="sm" disabled={envoi || code.length !== 6}>
              {envoi ? <Loader2 className="size-4 animate-spin" /> : t("secu.confirmer")}
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
  useI18n()
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
      setErreur(messageErreur(err, t("sp.action_erreur")))
    }
  }

  return (
    <div className="flex flex-col gap-4">
      {plusieurs && aucunPin && (
        <div className="flex items-start gap-2.5 rounded-lg border border-gold/30 bg-gold/[0.06] px-3.5 py-3 text-sm">
          <ShieldAlert className="mt-0.5 size-4 shrink-0 text-gold-text" />
          <p>
            {t("sp.avertissement")}
          </p>
        </div>
      )}

      {erreur && <p role="alert" className="text-sm text-destructive">{erreur}</p>}

      <div className="rounded-xl border border-border p-3.5">
        <div className="flex items-center gap-2">
          <ShieldCheck className="size-4 shrink-0 text-primary" />
          <p className="flex-1 font-display text-sm font-semibold">{t("sp.code_parent")}</p>
          <span className="text-xs text-muted-foreground">{parentActif ? t("sp.active") : t("sp.non_defini")}</span>
        </div>
        <p className="mt-1 text-xs text-muted-foreground">
          {t("sp.parent_texte")}
        </p>
        <div className="mt-2 flex flex-wrap gap-2">
          <Button
            size="sm"
            variant="outline"
            className="h-8 rounded-full text-xs"
            onClick={() => setOuverte({ type: "pin-parent" })}
          >
            {parentActif ? t("sp.modifier_code") : t("sp.definir_code")}
          </Button>
          {parentActif && (
            <Button
              size="sm"
              variant="ghost"
              className="h-8 rounded-full text-xs"
              onClick={() => setOuverte({ type: "retrait-pin-parent" })}
            >
              {t("sp.retirer")}
            </Button>
          )}
        </div>
        {ouverte?.type === "pin-parent" && (
          <FormulairePin
            titre={parentActif ? t("sp.choisis_nouveau_parent") : t("sp.choisis_parent")}
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
          <p className="font-display text-sm font-semibold">{profil.prenom || t("compte.profil_sans_nom")}</p>

          <div className="mt-2 flex items-center gap-2">
            <KeyRound className="size-4 shrink-0 text-muted-foreground" />
            <p className="flex-1 text-sm">{t("sp.code_profil")}</p>
            <span className="text-xs text-muted-foreground">{profil.pin_actif ? t("sp.active") : t("sp.aucun")}</span>
            <Button
              size="sm"
              variant="outline"
              className="h-8 rounded-full text-xs"
              onClick={() => setOuverte({ type: "pin-profil", id: profil.id })}
            >
              {profil.pin_actif ? t("sp.modifier") : t("sp.ajouter")}
            </Button>
            {profil.pin_actif && (
              <Button
                size="sm"
                variant="ghost"
                className="h-8 rounded-full text-xs"
                onClick={() => action(async () => onProfilChange(await retirerPinProfil(profil.id)))}
              >
                {t("sp.retirer")}
              </Button>
            )}
          </div>
          {ouverte?.type === "pin-profil" && ouverte.id === profil.id && (
            <FormulairePin
              titre={t("sp.choisis_code", { nom: profil.prenom || t("sp.ce_profil") })}
              annuler={() => setOuverte(null)}
              soumettre={(pin) => action(async () => onProfilChange(await definirPinProfil(profil.id, pin)))}
            />
          )}

          <div className="mt-2 flex items-center gap-2">
            <Smartphone className="size-4 shrink-0 text-muted-foreground" />
            <p className="flex-1 text-sm">{t("sp.tel_propre")}</p>
            <span className="text-xs text-muted-foreground">{profil.connexion_active ? t("sp.activee") : t("sp.aucun")}</span>
            {profil.connexion_active ? (
              <Button
                size="sm"
                variant="ghost"
                className="h-8 rounded-full text-xs"
                onClick={() => action(async () => onProfilChange(await supprimerConnexionProfil(profil.id)))}
              >
                {t("sp.retirer")}
              </Button>
            ) : (
              <Button
                size="sm"
                variant="outline"
                className="h-8 rounded-full text-xs"
                onClick={() => setOuverte({ type: "connexion", id: profil.id })}
              >
                {t("sp.ajouter")}
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
              {t("sp.info_enfant")}
            </p>
          )}
        </div>
      ))}
    </div>
  )
}
