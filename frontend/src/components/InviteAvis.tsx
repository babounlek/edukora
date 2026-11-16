import { useId, useState } from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { CheckCircle2, Star } from "lucide-react"

import { envoyerAvis, getEtatAvis } from "@/api/endpoints"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useAuth } from "@/context/AuthContext"
import { t, useI18n } from "@/lib/i18n"
import { cn } from "@/lib/utils"

export type RoleAvis = "eleve" | "parent"

const LONGUEUR_MAX = 600

function cleEcarte(role: RoleAvis, profilId: number | undefined) {
  return `edukora:avis-ecarte:${role}:${profilId ?? 0}`
}

function lireEcarte(cle: string): boolean {
  try {
    return localStorage.getItem(cle) === "1"
  } catch {
    return false
  }
}

/**
 * « Ça t'a aidé ? » : l'avis d'un élève à la fin d'un quiz, ou d'un parent sur la page de ses paiements (audit de
 * l'accueil du 2026-11-15, R8 : preuve sociale réelle ou absente, jamais fabriquée).
 *
 * C'est le serveur qui dit s'il y a lieu de demander (voir catalog.avis côté backend) : à partir du troisième quiz
 * terminé, une seule fois, jamais à un compte invité. Un « Non merci » est retenu sur cet appareil.
 *
 * Les auteurs sont mineurs : rien n'est affiché sans la case de consentement, non cochée d'office, et seul un prénom
 * accompagne le texte. Tout avis est relu dans l'admin avant d'être public ; l'écran le dit.
 */
export function InviteAvis({ role, className }: { role: RoleAvis; className?: string }) {
  const { langue } = useI18n()
  const queryClient = useQueryClient()
  const { isAuthenticated, user } = useAuth()
  const cle = cleEcarte(role, user?.profil_actif?.id)
  const [ecarte, setEcarte] = useState(() => lireEcarte(cle))
  const [note, setNote] = useState(0)
  const [contenu, setContenu] = useState("")
  const [prenom, setPrenom] = useState<string | null>(null)
  const [consentement, setConsentement] = useState(false)
  const [enCours, setEnCours] = useState(false)
  const [erreur, setErreur] = useState("")
  const [envoye, setEnvoye] = useState<"" | "public" | "interne">("")
  const idTexte = useId()
  const idPrenom = useId()
  const idCase = useId()

  const { data: etat } = useQuery({
    queryKey: ["avis", "etat"],
    queryFn: ({ signal }) => getEtatAvis(signal),
    enabled: isAuthenticated && !ecarte && !envoye,
  })

  if (envoye) {
    return (
      <div role="status" className={cn("flex items-start gap-3 rounded-2xl border border-success/30 bg-success/5 p-4", className)}>
        <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-success" aria-hidden="true" />
        <p className="text-sm">
          <strong>{t(`avis.merci_${role}`)}</strong> {envoye === "public" ? t("avis.merci_relecture") : t("avis.merci_interne")}
        </p>
      </div>
    )
  }
  if (ecarte || !etat || !etat[role]) return null

  // Le prénom du profil sert de proposition à l'élève ; un parent écrit le sien (le profil porte celui de l'enfant).
  const prenomSaisi = prenom ?? (role === "eleve" ? etat.prenom : "")

  function ecarter() {
    try {
      localStorage.setItem(cle, "1")
    } catch {
      // Stockage indisponible : l'invitation reviendra, sans conséquence.
    }
    setEcarte(true)
  }

  async function envoyer() {
    if (!note || enCours) return
    if (consentement && !prenomSaisi.trim()) {
      setErreur(t(`avis.prenom_requis_${role}`))
      return
    }
    setEnCours(true)
    setErreur("")
    try {
      await envoyerAvis({
        origine: role === "eleve" ? "ELEVE" : "PARENT",
        note,
        contenu: contenu.trim(),
        prenom: prenomSaisi.trim(),
        consentement,
        langue,
      })
      setEnvoye(consentement && contenu.trim() ? "public" : "interne")
      queryClient.removeQueries({ queryKey: ["avis", "etat"] })
    } catch (e) {
      // 400 : le serveur refuse le prénom (chiffres, adresse), seul champ que cet écran ne borne pas lui-même. Le reste
      // est une panne.
      setErreur((e as { status?: number })?.status === 400 ? t(`avis.prenom_requis_${role}`) : t("avis.erreur"))
    } finally {
      setEnCours(false)
    }
  }

  return (
    <section
      aria-label={t(`avis.titre_${role}`)}
      className={cn("rounded-2xl border border-border bg-card p-4 sm:p-5", className)}
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          <p className="font-display font-semibold">{t(`avis.titre_${role}`)}</p>
          <p className="text-sm text-muted-foreground">{t(`avis.texte_${role}`)}</p>
        </div>
        <div role="radiogroup" aria-label={t("avis.note_aria")} className="flex shrink-0 items-center gap-1">
          {[1, 2, 3, 4, 5].map((n) => (
            <button
              key={n}
              type="button"
              role="radio"
              aria-checked={note === n}
              aria-label={t("temoignage.note", { n })}
              onClick={() => setNote(n)}
              className="flex size-11 items-center justify-center rounded-full transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <Star aria-hidden="true" className={cn("size-7", n <= note ? "fill-gold text-gold-text" : "text-muted-foreground/50")} />
            </button>
          ))}
        </div>
      </div>

      {note > 0 && (
        <div className="mt-4 flex flex-col gap-3 border-t border-border pt-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor={idTexte}>{t(`avis.contenu_${role}`)}</Label>
            <textarea
              id={idTexte}
              value={contenu}
              onChange={(e) => setContenu(e.target.value.slice(0, LONGUEUR_MAX))}
              rows={3}
              maxLength={LONGUEUR_MAX}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-base focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring sm:text-sm"
            />
          </div>

          <div className="flex items-start gap-2.5">
            <input
              id={idCase}
              type="checkbox"
              checked={consentement}
              onChange={(e) => setConsentement(e.target.checked)}
              className="mt-0.5 size-5 shrink-0 accent-primary"
            />
            <div className="min-w-0 text-sm">
              <label htmlFor={idCase} className="font-medium">
                {role === "eleve" && etat.examen
                  ? t("avis.case_eleve_examen", { examen: etat.examen })
                  : t(`avis.case_${role}`)}
              </label>
              <p className="text-muted-foreground">{t(`avis.case_aide_${role}`)}</p>
            </div>
          </div>

          {consentement && (
            <div className="flex flex-col gap-1.5 sm:max-w-xs">
              <Label htmlFor={idPrenom}>{t(`avis.prenom_${role}`)}</Label>
              <Input
                id={idPrenom}
                value={prenomSaisi}
                onChange={(e) => setPrenom(e.target.value.slice(0, 30))}
                autoComplete="given-name"
                maxLength={30}
              />
              <p className="text-xs text-muted-foreground">{t("avis.prenom_aide")}</p>
            </div>
          )}

          {erreur && (
            <p role="alert" className="text-sm text-destructive">
              {erreur}
            </p>
          )}

          <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
            <Button onClick={envoyer} disabled={enCours}>
              {t("avis.envoyer")}
            </Button>
            <Button variant="ghost" onClick={ecarter} disabled={enCours}>
              {t("avis.non_merci")}
            </Button>
          </div>
        </div>
      )}

      {note === 0 && (
        <button type="button" onClick={ecarter} className="mt-2 text-sm text-muted-foreground underline-offset-2 hover:underline">
          {t(`avis.ecarter_${role}`)}
        </button>
      )}
    </section>
  )
}
