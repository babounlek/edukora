import { useEffect, useState, type FormEvent, type ReactNode } from "react"
import { Link, useNavigate } from "react-router-dom"
import {
  Check, Copy, Crown, FileText, GraduationCap,
  MessageCircle, NotebookPen, Pencil, Settings2, Share2, Sparkles, TrendingUp, type LucideIcon,
} from "lucide-react"

import { getWhatsAppStatus, optInWhatsApp, optOutWhatsApp, updateMe } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { BilanDePeriode } from "@/components/BilanDePeriode"
import { formatCompteARebours, formatCursus } from "@/components/CompteAReboursBadge"
import { ConnexionMethodsCard } from "@/components/ConnexionMethodsCard"
import { InterrupteurRappelsEmail } from "@/components/RappelsEmail"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useSeo } from "@/lib/seo"
import { SITE_NAME } from "@/lib/site"
import { epreuvesListPath } from "@/lib/countryPath"
import { cn } from "@/lib/utils"

/** Une section : titre avec pastille d'icône, action à droite, contenu dans une carte discrète. */
function Section({
  icone: Icone, titre, action, children, className,
}: { icone: LucideIcon; titre: string; action?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <section className={cn("rounded-2xl border border-border bg-card p-4 sm:p-5", className)}>
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 className="flex items-center gap-2 font-display text-base font-semibold">
          <Icone className="size-4 text-primary" aria-hidden="true" />
          {titre}
        </h2>
        {action}
      </div>
      {children}
    </section>
  )
}

export function AccountPage() {
  useSeo({ title: "Mon compte" })

  const { user, isAuthenticated, isLoading, updateUser } = useAuth()
  const { country } = useCountry()
  const navigate = useNavigate()
  const [copied, setCopied] = useState(false)
  const [whatsappOptedIn, setWhatsappOptedIn] = useState<boolean | null>(null)
  const [whatsappLoading, setWhatsappLoading] = useState(false)

  const [isEditingProfile, setIsEditingProfile] = useState(false)
  const [fullNameDraft, setFullNameDraft] = useState("")
  const [pseudoDraft, setPseudoDraft] = useState("")
  const [profileError, setProfileError] = useState<string | null>(null)
  const [isSavingProfile, setIsSavingProfile] = useState(false)

  useEffect(() => {
    if (isLoading) return
    if (!isAuthenticated) {
      navigate("/connexion", { state: { from: "/compte" } })
      return
    }
    getWhatsAppStatus().then((status) => setWhatsappOptedIn(status.opted_in))
  }, [isLoading, isAuthenticated, navigate])

  async function handleToggleWhatsApp() {
    setWhatsappLoading(true)
    try {
      const status = whatsappOptedIn ? await optOutWhatsApp() : await optInWhatsApp()
      setWhatsappOptedIn(status.opted_in)
    } finally {
      setWhatsappLoading(false)
    }
  }

  function startEditingProfile() {
    setFullNameDraft(user?.full_name ?? "")
    setPseudoDraft(user?.pseudo ?? "")
    setProfileError(null)
    setIsEditingProfile(true)
  }

  async function handleSaveProfile(event: FormEvent) {
    event.preventDefault()
    setProfileError(null)
    setIsSavingProfile(true)
    try {
      const updated = await updateMe({ full_name: fullNameDraft, pseudo: pseudoDraft })
      updateUser(updated)
      setIsEditingProfile(false)
    } catch (err) {
      setProfileError(err instanceof ApiError ? err.message : "Une erreur est survenue.")
    } finally {
      setIsSavingProfile(false)
    }
  }

  if (isLoading || !user) return null

  const referralLink = `${window.location.origin}/?ref=${user.referral_code}`
  const whatsappMessage = `Salut ! Je révise sur ${SITE_NAME} (corrigés BEPC/Probatoire/BAC) - viens jeter un œil : ${referralLink}`

  function handleCopyLink() {
    navigator.clipboard.writeText(referralLink)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const nom = user.full_name || user.pseudo || user.phone_number || user.email || "Mon compte"
  const initiales = (user.full_name || user.pseudo || "?")
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((mot) => mot.charAt(0).toLocaleUpperCase("fr"))
    .join("")
  const compte = user.compte_a_rebours ? formatCompteARebours(user.compte_a_rebours) : ""

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:py-10 sm:px-6">
      {/* Le profil en tête : qui je suis, ce que je prépare - identité et modification restent
          atteignables en un coup d'œil, sans hero pleine largeur ni tableau de chiffres. */}
      {isEditingProfile ? (
        <section className="mb-5 rounded-2xl border border-border bg-card p-5 shadow-sm">
          <h1 className="font-display text-xl font-semibold">Modifier mon profil</h1>
          <form onSubmit={handleSaveProfile} className="mt-4 flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <Label htmlFor="full_name">Nom complet</Label>
              <Input
                id="full_name"
                value={fullNameDraft}
                onChange={(e) => setFullNameDraft(e.target.value)}
                maxLength={150}
                placeholder="Ton nom"
                autoFocus
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="pseudo">Pseudo (facultatif)</Label>
              <Input
                id="pseudo"
                value={pseudoDraft}
                onChange={(e) => setPseudoDraft(e.target.value)}
                maxLength={20}
                placeholder="3 à 20 caractères : lettres, chiffres, _"
              />
            </div>
            {profileError && <p role="alert" className="text-sm text-destructive">{profileError}</p>}
            <div className="flex gap-2">
              <Button type="submit" disabled={isSavingProfile} className="rounded-full">
                {isSavingProfile ? "Enregistrement..." : "Enregistrer"}
              </Button>
              <Button
                type="button"
                variant="ghost"
                onClick={() => setIsEditingProfile(false)}
                disabled={isSavingProfile}
                className="rounded-full"
              >
                Annuler
              </Button>
            </div>
          </form>
        </section>
      ) : (
        <section className="mb-5 flex items-center gap-3.5 rounded-2xl border border-border bg-card p-4 sm:p-5">
          <span
            aria-hidden
            className="flex size-12 shrink-0 items-center justify-center rounded-full bg-primary/10 font-display text-lg font-semibold text-primary"
          >
            {initiales}
          </span>
          <div className="min-w-0 flex-1">
            <h1 className="truncate font-display text-lg font-semibold leading-tight">{nom}</h1>
            <p className="truncate text-sm text-muted-foreground">
              {[user.pseudo && `@${user.pseudo}`, user.phone_number, user.email].filter(Boolean).join(" · ")}
            </p>
            {user.cursus_prepare && (
              <p className="mt-1 flex items-center gap-1.5 text-xs font-medium text-primary">
                <GraduationCap className="size-3.5" aria-hidden="true" />
                {formatCursus(user.cursus_prepare)}
                {compte && ` · ${compte}`}
              </p>
            )}
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={startEditingProfile}
            aria-label="Modifier le profil"
            className="shrink-0 text-muted-foreground"
          >
            <Pencil className="size-4" />
          </Button>
        </section>
      )}

      <div className="flex flex-col gap-4">
        {user.cursus_prepare && <BilanDePeriode cursusId={user.cursus_prepare.id} />}

        {/* Les raccourcis remplacent les anciens onglets Activité/Lectures/Fiches - chaque
            destination gère déjà elle-même son propre état (vide, verrouillé...), inutile de le
            dupliquer ici. "Mes accès" vit aussi dans le menu du header (voir Header.tsx), comme
            "Mon historique" et "Mes paiements" - présent ici en plus parce que c'est l'information
            la plus naturellement attendue en arrivant sur /compte. */}
        <nav aria-label="Raccourcis" className="grid grid-cols-3 gap-2 sm:grid-cols-5 sm:gap-3">
          <Raccourci to="/mes-acces" icone={Sparkles} libelle="Mes accès" />
          <Raccourci to="/carnet" icone={NotebookPen} libelle="Mon carnet" />
          <Raccourci to="/parcours" icone={TrendingUp} libelle="Ma progression" />
          <Raccourci to="/fiches" icone={FileText} libelle="Fiches" />
          <Raccourci to={`${epreuvesListPath(country)}?origine=INEDITE`} icone={Crown} libelle="Inédites" />
        </nav>

        {/* Parrainage : simple partage de lien avec des amis (décision du 2026-09-28, voir
            project_parrainage_eleve_recalibrage) - une carte discrète, l'action (copier/partager)
            reste immédiate, sans peser sur le reste de la page. */}
        <section className="flex items-center gap-3 rounded-2xl border border-border bg-card p-4">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-gold/15 text-gold-foreground dark:text-gold-text">
            <Share2 className="size-4.5" aria-hidden="true" />
          </span>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-semibold">Partage avec tes amis</p>
            <p className="text-xs text-muted-foreground">
              {user.filleuls_count > 0
                ? `${user.filleuls_count} ami${user.filleuls_count > 1 ? "s" : ""} déjà invité${user.filleuls_count > 1 ? "s" : ""}.`
                : "Invite tes amis à découvrir tes cours et corrigés."}
            </p>
          </div>
          <div className="flex shrink-0 gap-1.5">
            <Button onClick={handleCopyLink} variant="outline" size="icon" className="rounded-full" aria-label="Copier mon lien de parrainage">
              {copied ? <Check className="size-4 text-success" /> : <Copy className="size-4" />}
            </Button>
            <Button asChild size="icon" className="rounded-full">
              <a
                href={`https://wa.me/?text=${encodeURIComponent(whatsappMessage)}`}
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Partager mon lien sur WhatsApp"
              >
                <MessageCircle className="size-4" />
              </a>
            </Button>
          </div>
        </section>

        <Section icone={Settings2} titre="Réglages">
          {whatsappOptedIn === null ? (
            <p className="text-sm text-muted-foreground">Chargement…</p>
          ) : (
            <div className="flex items-center justify-between gap-4">
              <div className="min-w-0">
                <p className="flex items-center gap-2 text-sm font-medium">
                  <MessageCircle className="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
                  Rappels par WhatsApp
                </p>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  Un message par jour quand des thèmes t'attendent en révision.
                </p>
              </div>
              <button
                type="button"
                role="switch"
                aria-checked={whatsappOptedIn}
                aria-label="Rappels de révision par WhatsApp"
                onClick={handleToggleWhatsApp}
                disabled={whatsappLoading}
                className={cn(
                  "relative inline-flex h-6 w-11 shrink-0 items-center rounded-full border transition-colors disabled:opacity-60",
                  whatsappOptedIn ? "border-primary bg-primary" : "border-border bg-muted",
                )}
              >
                <span
                  aria-hidden
                  className={cn(
                    "inline-block size-4 rounded-full bg-background shadow transition-transform",
                    whatsappOptedIn ? "translate-x-5" : "translate-x-1",
                  )}
                />
              </button>
            </div>
          )}
          <div className="mt-4 border-t border-border pt-4">
            <InterrupteurRappelsEmail />
          </div>
        </Section>

        <ConnexionMethodsCard />
      </div>
    </div>
  )
}

function Raccourci({ to, icone: Icone, libelle }: { to: string; icone: LucideIcon; libelle: string }) {
  return (
    <Link
      to={to}
      className="flex flex-col items-center gap-1.5 rounded-2xl border border-border bg-card px-2 py-3.5 text-center text-xs font-medium transition-colors hover:border-primary/40"
    >
      <span className="flex size-9 items-center justify-center rounded-xl bg-primary/10 text-primary">
        <Icone className="size-4.5" aria-hidden="true" />
      </span>
      {libelle}
    </Link>
  )
}
