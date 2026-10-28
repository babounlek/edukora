import { useEffect, useState, type FormEvent } from "react"
import { Check, Loader2, Store } from "lucide-react"

import { ApiError } from "@/api/client"
import { getRattachementRevendeur, postRattachementRevendeur } from "@/api/endpoints"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { t, useI18n } from "@/lib/i18n"
import { codeRevendeurMemorise, oublierCodeRevendeur } from "@/lib/referral"

type Etat =
  | { phase: "chargement" | "masque" }
  | { phase: "saisie" }
  | { phase: "fait"; nom: string }
  | { phase: "info"; texte: string }

/**
 * Saisie d'un code revendeur avant le premier paiement, pour un compte déjà ouvert (celui qui s'inscrit avec
 * un lien `?rev=` n'a rien à saisir). Le champ est ouvert d'emblée (un lien replié passait inaperçu), facultatif,
 * et ne gêne jamais le paiement si le serveur ne répond pas. Dès que le compte a un revendeur ou un paiement
 * validé, il laisse place à une phrase qui dit pourquoi. Un code déjà mémorisé par un lien est proposé,
 * jamais envoyé sans que la personne valide.
 */
export function CodeRevendeur() {
  useI18n()
  const [etat, setEtat] = useState<Etat>({ phase: "chargement" })
  const [saisie, setSaisie] = useState("")
  const [envoi, setEnvoi] = useState(false)
  const [erreur, setErreur] = useState<string | null>(null)

  useEffect(() => {
    const controle = new AbortController()
    getRattachementRevendeur(controle.signal)
      .then((reponse) => {
        if (!reponse.peut_saisir_code) {
          // Déjà rattaché (ou déjà client) : le code mémorisé ne sert plus, et ne doit pas suivre la personne suivante.
          oublierCodeRevendeur()
          // Dire pourquoi il n'y a pas de champ, plutôt que de laisser croire qu'il manque.
          setEtat({ phase: "info", texte: reponse.revendeur ? t("rev.code_ok", { nom: reponse.revendeur.nom_affiche }) : t("rev.code_trop_tard") })
          return
        }
        setSaisie(codeRevendeurMemorise())
        setEtat({ phase: "saisie" })
      })
      .catch(() => setEtat({ phase: "masque" }))
    return () => controle.abort()
  }, [])

  async function valider(evenement: FormEvent) {
    evenement.preventDefault()
    if (!saisie.trim()) return
    setErreur(null)
    setEnvoi(true)
    try {
      const reponse = await postRattachementRevendeur(saisie.trim())
      oublierCodeRevendeur()
      setEtat({ phase: "fait", nom: reponse.revendeur.nom_affiche })
    } catch (err) {
      setErreur(err instanceof ApiError && err.code !== "code_invalide" ? err.message : t("rev.code_invalide"))
    } finally {
      setEnvoi(false)
    }
  }

  if (etat.phase === "chargement" || etat.phase === "masque") return null

  if (etat.phase === "fait") {
    return (
      <p role="status" className="flex items-center gap-2 rounded-lg border border-success/30 bg-success/[0.06] px-3.5 py-2.5 text-sm">
        <Check className="size-4 shrink-0 text-success" aria-hidden="true" />
        {t("rev.code_ok", { nom: etat.nom })}
      </p>
    )
  }

  if (etat.phase === "info") {
    return (
      <p className="flex items-center gap-2 text-sm text-muted-foreground">
        <Store className="size-4 shrink-0" aria-hidden="true" />
        {etat.texte}
      </p>
    )
  }

  return (
    <form onSubmit={valider} className="flex flex-col gap-2 rounded-lg border border-border bg-muted/30 px-3.5 py-3">
      <label htmlFor="code-revendeur" className="text-sm font-medium">
        {t("rev.code_question")}
      </label>
      <div className="flex gap-2">
        <Input
          id="code-revendeur"
          value={saisie}
          onChange={(e) => setSaisie(e.target.value.toUpperCase())}
          placeholder={t("rev.code_placeholder")}
          maxLength={10}
          autoCapitalize="characters"
          autoComplete="off"
          spellCheck={false}
          aria-label={t("rev.code_label")}
          aria-invalid={erreur ? true : undefined}
          aria-describedby={erreur ? "code-revendeur-erreur" : undefined}
          className="font-mono uppercase tracking-wider"
        />
        <Button type="submit" disabled={envoi || !saisie.trim()} className="shrink-0 rounded-full">
          {envoi ? <Loader2 className="size-4 animate-spin" aria-hidden="true" /> : t("rev.code_valider")}
        </Button>
      </div>
      {erreur ? (
        <p id="code-revendeur-erreur" role="alert" className="text-sm text-destructive">
          {erreur}
        </p>
      ) : (
        <p className="text-xs text-muted-foreground">{t("rev.code_info")}</p>
      )}
    </form>
  )
}
