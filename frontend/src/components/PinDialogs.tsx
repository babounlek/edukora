import { useEffect, useState, type FormEvent } from "react"
import { KeyRound, Loader2, ShieldCheck } from "lucide-react"

import {
  confirmerReinitialisationPinParent,
  demanderReinitialisationPinParent,
  verifierPinParent,
} from "@/api/endpoints"
import { ApiError, setParentModeHandler, setParentToken } from "@/api/client"
import { useAuth } from "@/context/AuthContext"
import { setGestionnairePinProfil, type DemandePinProfil } from "@/lib/pinPrompts"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { t, useI18n } from "@/lib/i18n"

/** Champ de saisie d'un code à 4 chiffres (masqué, clavier numérique). */
export function ChampPin({
  value,
  onChange,
  id,
  label,
  autoFocus = false,
}: {
  value: string
  onChange: (v: string) => void
  id: string
  label: string
  autoFocus?: boolean
}) {
  return (
    <Input
      id={id}
      aria-label={label}
      type="password"
      inputMode="numeric"
      autoComplete="off"
      autoFocus={autoFocus}
      placeholder="••••"
      maxLength={4}
      value={value}
      onChange={(e) => onChange(e.target.value.replace(/\D/g, "").slice(0, 4))}
      className="h-12 text-center text-2xl tracking-[0.6em]"
    />
  )
}

type EtatProfil = (DemandePinProfil & { resoudre: (pin: string | null) => void }) | null
type EtatParent = { resoudre: (ok: boolean) => void } | null

/**
 * Les deux fenêtres de saisie de code, montées une seule fois dans l'application :
 * - code d'un PROFIL (enfant), demandé quand on tente de l'ouvrir (voir
 *   changerProfilActif.ts) ;
 * - code PARENT, demandé quand une action du compte (paiement, gestion des enfants...)
 *   exige le mode parent (voir api/client.ts) - avec « code oublié » : un code reçu par
 *   SMS ou e-mail le réinitialise.
 */
export function PinDialogs() {
  useI18n()
  const { updateUser } = useAuth()
  const [profil, setProfil] = useState<EtatProfil>(null)
  const [parent, setParent] = useState<EtatParent>(null)

  useEffect(() => {
    setGestionnairePinProfil(
      (demande) => new Promise<string | null>((resoudre) => setProfil({ ...demande, resoudre })),
    )
    setParentModeHandler(
      () =>
        new Promise<boolean>((resoudre) => {
          setParent({ resoudre })
        }),
    )
    return () => {
      setGestionnairePinProfil(null)
      setParentModeHandler(null)
    }
  }, [])

  return (
    <>
      <FenetrePinProfil etat={profil} fermer={() => setProfil(null)} />
      <FenetreModeParent
        etat={parent}
        fermer={() => {
          setParent(null)
        }}
        onUser={updateUser}
      />
    </>
  )
}

function FenetrePinProfil({ etat, fermer }: { etat: EtatProfil; fermer: () => void }) {
  const [pin, setPin] = useState("")

  useEffect(() => {
    setPin("")
  }, [etat])

  function valider(e: FormEvent) {
    e.preventDefault()
    if (pin.length !== 4 || !etat) return
    etat.resoudre(pin)
    fermer()
  }

  function annuler() {
    etat?.resoudre(null)
    fermer()
  }

  return (
    <Dialog open={etat !== null} onOpenChange={(ouvert) => !ouvert && annuler()}>
      <DialogContent>
        <form onSubmit={valider} className="flex flex-col gap-4">
          <div className="flex flex-col items-center gap-2 text-center">
            <span className="flex size-11 items-center justify-center rounded-full bg-primary/10 text-primary">
              <KeyRound className="size-5" />
            </span>
            <DialogTitle className="font-display text-lg font-semibold">
              {t("pin.code_de", { nom: etat?.prenom ?? t("sp.ce_profil") })}
            </DialogTitle>
            <DialogDescription className="text-sm text-muted-foreground">
              {t("pin.protege")}
            </DialogDescription>
          </div>
          <ChampPin id="pin-profil" label={t("sp.code_profil")} value={pin} onChange={setPin} autoFocus />
          {etat?.erreur && (
            <p role="alert" className="text-center text-sm text-destructive">
              {etat.erreur}
            </p>
          )}
          <div className="flex gap-2">
            <Button type="button" variant="outline" className="flex-1" onClick={annuler}>
              {t("seance.annuler")}
            </Button>
            <Button type="submit" className="flex-1" disabled={pin.length !== 4}>
              {t("pin.ouvrir")}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

type EtapeParent = "pin" | "oublie" | "code"

function FenetreModeParent({
  etat,
  fermer,
  onUser,
}: {
  etat: EtatParent
  fermer: () => void
  onUser: (user: Parameters<ReturnType<typeof useAuth>["updateUser"]>[0]) => void
}) {
  const [etape, setEtape] = useState<EtapeParent>("pin")
  const [pin, setPin] = useState("")
  const [code, setCode] = useState("")
  const [envoi, setEnvoi] = useState(false)
  const [erreur, setErreur] = useState<string | null>(null)

  useEffect(() => {
    setEtape("pin")
    setPin("")
    setCode("")
    setErreur(null)
    setEnvoi(false)
  }, [etat])

  function terminer(ok: boolean) {
    etat?.resoudre(ok)
    fermer()
  }

  async function valider(e: FormEvent) {
    e.preventDefault()
    if (pin.length !== 4) return
    setEnvoi(true)
    setErreur(null)
    try {
      const { jeton, expire_dans } = await verifierPinParent(pin)
      setParentToken(jeton, expire_dans)
      terminer(true)
    } catch (err) {
      setErreur(err instanceof ApiError ? err.message : t("pin.verification_erreur"))
      setPin("")
      setEnvoi(false)
    }
  }

  async function demanderCode() {
    setEnvoi(true)
    setErreur(null)
    try {
      await demanderReinitialisationPinParent()
      setEtape("code")
    } catch (err) {
      setErreur(err instanceof ApiError ? err.message : t("sp.envoi_erreur"))
    } finally {
      setEnvoi(false)
    }
  }

  async function confirmerCode(e: FormEvent) {
    e.preventDefault()
    if (!/^\d{6}$/.test(code)) return
    setEnvoi(true)
    setErreur(null)
    try {
      const user = await confirmerReinitialisationPinParent(code)
      onUser(user)
      // Le code parent est retiré : plus rien à saisir, l'action en attente peut repartir.
      terminer(true)
    } catch (err) {
      setErreur(err instanceof ApiError ? err.message : t("sp.code_invalide"))
      setEnvoi(false)
    }
  }

  return (
    <Dialog open={etat !== null} onOpenChange={(ouvert) => !ouvert && terminer(false)}>
      <DialogContent>
        <div className="flex flex-col items-center gap-2 text-center">
          <span className="flex size-11 items-center justify-center rounded-full bg-primary/10 text-primary">
            <ShieldCheck className="size-5" />
          </span>
          <DialogTitle className="font-display text-lg font-semibold">{t("sp.code_parent")}</DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground">
            {etape === "pin" && t("pin.reserve_parent")}
            {etape === "oublie" && t("pin.oublie_texte")}
            {etape === "code" && t("pin.code_texte")}
          </DialogDescription>
        </div>

        {etape === "pin" && (
          <form onSubmit={valider} className="mt-4 flex flex-col gap-4">
            <ChampPin id="pin-parent" label={t("sp.code_parent")} value={pin} onChange={setPin} autoFocus />
            {erreur && (
              <p role="alert" className="text-center text-sm text-destructive">
                {erreur}
              </p>
            )}
            <div className="flex gap-2">
              <Button type="button" variant="outline" className="flex-1" onClick={() => terminer(false)}>
                {t("seance.annuler")}
              </Button>
              <Button type="submit" className="flex-1" disabled={pin.length !== 4 || envoi}>
                {envoi ? <Loader2 className="size-4 animate-spin" /> : t("login.valider")}
              </Button>
            </div>
            <button
              type="button"
              onClick={() => {
                setErreur(null)
                setEtape("oublie")
              }}
              className="text-center text-sm text-muted-foreground underline-offset-4 hover:text-primary hover:underline"
            >
              {t("pin.oublie")}
            </button>
          </form>
        )}

        {etape === "oublie" && (
          <div className="mt-4 flex flex-col gap-3">
            {erreur && (
              <p role="alert" className="text-center text-sm text-destructive">
                {erreur}
              </p>
            )}
            <Button onClick={demanderCode} disabled={envoi}>
              {envoi ? <Loader2 className="size-4 animate-spin" /> : t("pin.envoyer_verification")}
            </Button>
            <Button variant="outline" onClick={() => setEtape("pin")}>
              {t("onboarding.retour")}
            </Button>
          </div>
        )}

        {etape === "code" && (
          <form onSubmit={confirmerCode} className="mt-4 flex flex-col gap-4">
            <Input
              aria-label={t("pin.verification_aria")}
              inputMode="numeric"
              autoComplete="one-time-code"
              autoFocus
              placeholder="123456"
              maxLength={6}
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
              className="h-12 text-center text-xl tracking-[0.4em]"
            />
            {erreur && (
              <p role="alert" className="text-center text-sm text-destructive">
                {erreur}
              </p>
            )}
            <Button type="submit" disabled={!/^\d{6}$/.test(code) || envoi}>
              {envoi ? <Loader2 className="size-4 animate-spin" /> : t("pin.reinitialiser")}
            </Button>
            <Button type="button" variant="outline" onClick={() => terminer(false)}>
              {t("seance.annuler")}
            </Button>
          </form>
        )}
      </DialogContent>
    </Dialog>
  )
}
