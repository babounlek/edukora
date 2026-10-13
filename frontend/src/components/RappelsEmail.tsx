import { useState } from "react"
import { Link } from "react-router-dom"
import { toast } from "sonner"
import { BellRing, CalendarCheck, Mail } from "lucide-react"

import { updateMe } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/context/AuthContext"
import { cn } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/** Active ou coupe les rappels quotidiens par e-mail. Renvoie false si l'appel échoue. */
function useRappelsEmail() {
  useI18n()
  const { user, updateUser } = useAuth()
  const [enCours, setEnCours] = useState(false)

  async function modifier(params: Parameters<typeof updateMe>[0], succes?: string): Promise<boolean> {
    setEnCours(true)
    try {
      updateUser(await updateMe(params))
      if (succes) toast.success(succes)
      return true
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : t("rappels.erreur"))
      return false
    } finally {
      setEnCours(false)
    }
  }

  return { user, enCours, modifier }
}

/**
 * Le réglage durable, dans « Réglages > Notifications » : un interrupteur, et - quand il
 * ne peut pas s'allumer - la raison et le chemin pour y remédier, jamais un bouton mort.
 */
export function InterrupteurRappelsEmail() {
  const { user, enCours, modifier } = useRappelsEmail()
  if (!user) return null

  const peutActiver = user.email_verified
  const actif = user.rappels_actifs

  return (
    <div className="flex items-center justify-between gap-4">
      <div className="min-w-0">
        <p className="flex items-center gap-2 font-medium">
          <Mail className="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
          {t("rappels.seance_titre")}
        </p>
        <p className="mt-0.5 text-sm text-muted-foreground">
          {t("rappels.seance_texte")}
        </p>
        {!peutActiver && (
          <p className="mt-1 text-sm">
            {t("rappels.ajoute_email")}{" "}
            <Link to="/compte" className="text-primary underline underline-offset-2">
              {t("rappels.lien_connexion")}
            </Link>
            .
          </p>
        )}
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={actif}
        aria-label={t("rappels.seance_titre")}
        disabled={enCours || (!peutActiver && !actif)}
        onClick={() => modifier({ rappels_actifs: !actif })}
        className={cn(
          "relative inline-flex h-7 w-12 shrink-0 items-center rounded-full border transition-colors after:absolute after:-inset-2 after:content-[''] disabled:opacity-60",
          actif ? "border-primary bg-primary" : "border-border bg-muted",
        )}
      >
        <span
          aria-hidden
          className={cn(
            "inline-block size-5 rounded-full bg-background shadow transition-transform",
            actif ? "translate-x-6" : "translate-x-1",
          )}
        />
      </button>
    </div>
  )
}

/**
 * Le bilan du dimanche soir pour le parent : ce que chaque enfant du compte a fait dans la semaine.
 * Même mécanique que les rappels (adresse confirmée, un clic pour l'arrêter dans l'e-mail) ; réservé
 * au mode parent côté serveur, qui redemande le code parent si besoin.
 */
export function InterrupteurBilanParent() {
  const { user, enCours, modifier } = useRappelsEmail()
  if (!user) return null

  const peutActiver = user.email_verified
  const actif = user.bilan_parent_actif

  return (
    <div className="flex items-center justify-between gap-4">
      <div className="min-w-0">
        <p className="flex items-center gap-2 font-medium">
          <CalendarCheck className="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
          {t("rappels.bilan_titre")}
        </p>
        <p className="mt-0.5 text-sm text-muted-foreground">
          {t("rappels.bilan_texte")}
        </p>
        {!peutActiver && (
          <p className="mt-1 text-sm">
            {t("rappels.ajoute_email")}{" "}
            <Link to="/compte" className="text-primary underline underline-offset-2">
              {t("rappels.lien_connexion")}
            </Link>
            .
          </p>
        )}
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={actif}
        aria-label={t("rappels.bilan_titre")}
        disabled={enCours || (!peutActiver && !actif)}
        onClick={() => modifier({ bilan_parent_actif: !actif })}
        className={cn(
          "relative inline-flex h-7 w-12 shrink-0 items-center rounded-full border transition-colors after:absolute after:-inset-2 after:content-[''] disabled:opacity-60",
          actif ? "border-primary bg-primary" : "border-border bg-muted",
        )}
      >
        <span
          aria-hidden
          className={cn(
            "inline-block size-5 rounded-full bg-background shadow transition-transform",
            actif ? "translate-x-6" : "translate-x-1",
          )}
        />
      </button>
    </div>
  )
}

/**
 * L'invitation, une seule fois, au moment où elle a du sens : l'élève vient de terminer sa
 * première séance, il sait ce qu'on lui rappellerait. Écartée, elle ne revient plus (la
 * décision est portée par le compte, pas par le navigateur) ; le réglage reste dans le compte.
 */
export function InviteRappels() {
  const { user, enCours, modifier } = useRappelsEmail()
  if (!user || user.rappels_actifs || user.rappels_invite_refusee) return null

  return (
    <section className="mx-auto max-w-5xl px-4 pt-6 sm:px-6" aria-label={t("rappels.invite_aria")}>
      <div className="rounded-2xl border border-border bg-card px-5 py-4">
        <p className="flex items-center gap-2 font-display font-medium">
          <BellRing className="size-4 shrink-0 text-primary" aria-hidden="true" />
          {t("rappels.invite_titre")}
        </p>
        <p className="mt-1 text-sm text-muted-foreground">
          {t("rappels.invite_texte")}
        </p>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          {user.email_verified ? (
            <Button
              size="sm"
              disabled={enCours}
              onClick={() => modifier({ rappels_actifs: true }, t("rappels.active"))}
            >
              {t("rappels.activer")}
            </Button>
          ) : (
            <Button asChild size="sm">
              <Link to="/compte">{t("rappels.ajouter_email")}</Link>
            </Button>
          )}
          <Button
            size="sm"
            variant="ghost"
            disabled={enCours}
            onClick={() => modifier({ rappels_invite_refusee: true })}
          >
            {t("rappels.non_merci")}
          </Button>
        </div>
      </div>
    </section>
  )
}
