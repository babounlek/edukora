import { useEffect, useState, type FormEvent, type ReactNode } from "react"
import { Link, useNavigate } from "react-router-dom"
import {
  ArrowRight, BookOpen, CalendarClock, Check, CheckCircle2, Copy, Crown, FileText, GraduationCap, LogOut,
  MessageCircle, NotebookPen, Pencil, Receipt, Settings2, Share2, Sparkles, TrendingUp, type LucideIcon,
} from "lucide-react"

import {
  getMyProgression,
  getWhatsAppStatus,
  listMyInscriptionsInedites,
  listMyInscriptionsRepetiteur,
  listMySubscriptions,
  listMyTentativesInedites,
  optInWhatsApp,
  optOutWhatsApp,
  updateMe,
} from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type {
  InscriptionInedite, InscriptionRepetiteur, Progression, Subscription, TentativeInediteListItem,
} from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { BilanDePeriode } from "@/components/BilanDePeriode"
import { formatCompteARebours, formatCursus } from "@/components/CompteAReboursBadge"
import { ConnexionMethodsCard } from "@/components/ConnexionMethodsCard"
import { InterrupteurRappelsEmail } from "@/components/RappelsEmail"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { formatNote } from "@/lib/notation"
import { useSeo } from "@/lib/seo"
import { SITE_NAME } from "@/lib/site"
import { catalogueHomePath, coursReaderPath, epreuveReaderPath, epreuvesListPath } from "@/lib/countryPath"
import { cn } from "@/lib/utils"

// Au-delà de ce nombre, une liste (tentatives, lectures) passe derrière un "voir plus" - un
// compte actif de longue date peut accumuler des dizaines d'entrées ; les afficher toutes
// d'un bloc est la source concrète du "très touffu" signalé sur cette page.
const PREVIEW_COUNT = 3

// En dessous, la fin de l'abonnement se voit : la jauge passe à l'orange et "Prolonger" devient
// l'action principale de la ligne. Assez tôt pour renouveler sans coupure, assez tard pour ne pas
// harceler quelqu'un qui vient de payer.
const JOURS_AVANT_RENOUVELLEMENT = 14

/**
 * Tronque une liste à PREVIEW_COUNT éléments avec un bouton "voir plus" - un composant dédié
 * plutôt qu'un hook appelé inline dans un .map() du parent : les Hooks React ne peuvent pas être
 * appelés dans une boucle, alors qu'une instance de composant créée par .map() porte sans
 * problème son propre état - chaque liste garde son expansion indépendante des autres.
 */
function ExpandableList<T>({
  items, renderItem, previewCount = PREVIEW_COUNT,
}: { items: T[]; renderItem: (item: T) => ReactNode; previewCount?: number }) {
  const [expanded, setExpanded] = useState(false)
  const visible = expanded ? items : items.slice(0, previewCount)
  return (
    <ul className="flex flex-col gap-2">
      {visible.map(renderItem)}
      {items.length > previewCount && (
        <li>
          <button
            type="button"
            onClick={() => setExpanded((e) => !e)}
            className="text-sm font-medium text-primary hover:underline"
          >
            {expanded ? "Voir moins" : `Voir les ${items.length - previewCount} autres`}
          </button>
        </li>
      )}
    </ul>
  )
}

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

/** Un état vide qui propose la suite plutôt que de constater le vide. */
function EtatVide({
  texte, lien, libelleLien,
}: { texte: string; lien: string; libelleLien: string }) {
  return (
    <div className="rounded-xl border border-dashed border-border bg-muted/30 px-4 py-4 text-center">
      <p className="text-sm text-muted-foreground">{texte}</p>
      <Link to={lien} className="mt-1.5 inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline">
        {libelleLien}
        <ArrowRight className="size-3.5" />
      </Link>
    </div>
  )
}

function joursRestants(expiresAt: string): number {
  return Math.ceil((new Date(expiresAt).getTime() - Date.now()) / 86_400_000)
}

function dateFr(iso: string): string {
  return new Date(iso).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" })
}

function libelleCursus(cursus: Subscription["cursus"]): string {
  return `${cursus.examen_display}${cursus.series ? ` - Série ${cursus.series.code}` : ""}`
}

/**
 * Un accès (abonnement ou add-on) : ce qu'il donne, jusqu'à quand, et - surtout - ce qu'il faut faire.
 * Les jours restants se lisent d'un coup d'œil (jauge sur 30 jours, orange à l'approche de la fin) et
 * "Prolonger" apparaît AVANT l'expiration : renouveler quand on est encore en pleine révision, pas
 * après avoir perdu l'accès. Une prolongation repart de l'échéance existante (voir
 * Subscription.extend) : rien n'est perdu à le faire tôt.
 */
function LigneAcces({
  titre, sous_titre, expiresAt, actif, cursusId, renouvelable = true,
}: {
  titre: string
  sous_titre?: string
  expiresAt: string
  actif: boolean
  cursusId: number
  renouvelable?: boolean
}) {
  const jours = joursRestants(expiresAt)
  const bientot = actif && jours <= JOURS_AVANT_RENOUVELLEMENT
  return (
    <li className="rounded-xl border border-border bg-background/60 p-3.5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-semibold leading-snug">{titre}</p>
          {sous_titre && <p className="text-xs text-muted-foreground">{sous_titre}</p>}
        </div>
        {actif ? (
          <Badge variant="success" className="shrink-0 gap-1">
            <Check className="size-3" strokeWidth={3} />
            Actif
          </Badge>
        ) : (
          <Badge variant="outline" className="shrink-0">Expiré</Badge>
        )}
      </div>

      {actif ? (
        <div className="mt-2 flex flex-wrap items-center justify-between gap-x-3 gap-y-0.5 text-xs">
          <span className={cn("inline-flex items-center gap-1.5 whitespace-nowrap", bientot ? "font-medium text-warning-foreground dark:text-warning" : "text-muted-foreground")}>
            <CalendarClock className="size-3.5" aria-hidden="true" />
            {jours > 1 ? `${jours} jours restants` : jours === 1 ? "Dernier jour" : "Expire aujourd'hui"}
          </span>
          <span className="text-muted-foreground">jusqu'au {dateFr(expiresAt)}</span>
        </div>
      ) : (
        <p className="mt-2 text-xs text-muted-foreground">Expiré le {dateFr(expiresAt)}.</p>
      )}

      {renouvelable && (!actif || bientot) && (
        <Button asChild size="sm" variant={actif ? "default" : "outline"} className="mt-3 h-8 rounded-full text-xs">
          <Link to={`/abonnement?cursus=${cursusId}`}>
            {actif ? "Prolonger" : "Se réabonner"}
            <ArrowRight className="size-3.5" />
          </Link>
        </Button>
      )}
    </li>
  )
}

export function AccountPage() {
  useSeo({ title: "Mon compte" })

  const { user, logout, isAuthenticated, isLoading, updateUser } = useAuth()
  const { country } = useCountry()
  const navigate = useNavigate()
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [progression, setProgression] = useState<Progression | null>(null)
  const [tentativesInedites, setTentativesInedites] = useState<TentativeInediteListItem[] | null>(null)
  const [inscriptionsInedites, setInscriptionsInedites] = useState<InscriptionInedite[] | null>(null)
  const [inscriptionsRepetiteur, setInscriptionsRepetiteur] = useState<InscriptionRepetiteur[] | null>(null)
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
    listMySubscriptions().then(setSubscriptions)
    getMyProgression().then(setProgression)
    listMyTentativesInedites().then(setTentativesInedites)
    listMyInscriptionsInedites().then(setInscriptionsInedites)
    listMyInscriptionsRepetiteur().then(setInscriptionsRepetiteur)
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

  function handleLogout() {
    logout()
    navigate(catalogueHomePath(country))
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

  const totalRead = (progression?.lessons.length ?? 0) + (progression?.cours.length ?? 0)
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

  // Les trois sources d'accès (abonnement, add-on inédites, add-on répétiteur) partagent la même
  // forme (cursus/expires_at/is_active) : une seule liste "Mes accès" plutôt que trois blocs
  // distincts qui répètent chacun leur propre état vide - la duplication constatée sur l'ancienne
  // version de cette page. null = pas encore chargé, on n'affiche rien avant de savoir.
  const accesCharges = inscriptionsInedites !== null && inscriptionsRepetiteur !== null
  const acces = [
    ...subscriptions.map((sub) => ({
      key: `sub-${sub.id}`,
      titre: libelleCursus(sub.cursus),
      sous_titre: sub.plan_name ?? (sub.duration_mode === "JUSQUA_EXAMEN" ? "Jusqu'à l'Examen" : "Mensuel"),
      expiresAt: sub.expires_at,
      actif: sub.is_active,
      cursusId: sub.cursus.id,
      // Un accès "Jusqu'à l'Examen" couvre déjà l'échéance : lui proposer de prolonger n'aurait
      // aucun sens tant qu'il est actif.
      renouvelable: sub.duration_mode !== "JUSQUA_EXAMEN" || !sub.is_active,
    })),
    ...(inscriptionsInedites ?? []).map((i) => ({
      key: `inedit-${i.id}`,
      titre: libelleCursus(i.cursus),
      sous_titre: "Épreuves inédites",
      expiresAt: i.expires_at,
      actif: i.is_active,
      cursusId: i.cursus.id,
      renouvelable: true,
    })),
    ...(inscriptionsRepetiteur ?? []).map((i) => ({
      key: `repet-${i.id}`,
      titre: libelleCursus(i.cursus),
      sous_titre: "Add-on Fiches",
      expiresAt: i.expires_at,
      actif: i.is_active,
      cursusId: i.cursus.id,
      renouvelable: true,
    })),
  ]

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
        <Section icone={Sparkles} titre="Mes accès">
          {acces.length > 0 ? (
            <ul className="flex flex-col gap-2.5">
              {acces.map(({ key, ...props }) => <LigneAcces key={key} {...props} />)}
            </ul>
          ) : accesCharges ? (
            <EtatVide
              texte="Aucun accès actif pour le moment. Choisis ton examen pour débloquer les corrigés, les cours et ta séance du jour."
              lien="/tarifs"
              libelleLien="Voir les formules"
            />
          ) : null}
        </Section>

        {user.cursus_prepare && <BilanDePeriode cursusId={user.cursus_prepare.id} />}

        {/* Les raccourcis remplacent les anciens onglets Activité/Lectures/Fiches - chaque
            destination gère déjà elle-même son propre état (vide, verrouillé...), inutile de le
            dupliquer ici. */}
        <nav aria-label="Raccourcis" className="grid grid-cols-3 gap-2 sm:gap-3">
          <Raccourci to="/carnet" icone={NotebookPen} libelle="Mon carnet" />
          <Raccourci to="/parcours" icone={TrendingUp} libelle="Ma progression" />
          <Raccourci to="/mes-paiements" icone={Receipt} libelle="Mes paiements" />
          <Raccourci to="/fiches" icone={FileText} libelle="Fiches" />
          <Raccourci to={`${epreuvesListPath(country)}?origine=INEDITE`} icone={Crown} libelle="Inédites" />
        </nav>

        {tentativesInedites && tentativesInedites.length > 0 && (
          <Section icone={Crown} titre="Dernières tentatives inédites">
            <ExpandableList
              items={tentativesInedites}
              renderItem={(tentative) => (
                <li key={tentative.id}>
                  <Link
                    to={
                      tentative.submitted_at
                        ? `/inedit/tentative/${tentative.id}/resultat`
                        : `/inedit/tentative/${tentative.id}`
                    }
                    className="flex items-center justify-between gap-3 rounded-xl border border-border bg-background/60 px-3.5 py-2.5 text-sm transition-colors hover:border-primary/40"
                  >
                    <span className="flex min-w-0 flex-col">
                      <span className="truncate font-medium">{tentative.epreuve_titre}</span>
                      <span className="text-xs text-muted-foreground">
                        {tentative.cursus_display} · {new Date(tentative.started_at).toLocaleDateString("fr-FR")}
                      </span>
                    </span>
                    {tentative.submitted_at ? (
                      <Badge variant={tentative.score_obtenu !== null && tentative.score_obtenu >= 50 ? "success" : "outline"}>
                        {tentative.note_obtenue !== null && tentative.bareme_snapshot !== null
                          ? formatNote(tentative.note_obtenue, tentative.bareme_snapshot)
                          : `${tentative.score_obtenu}%`}
                      </Badge>
                    ) : (
                      <Badge variant="outline">En cours</Badge>
                    )}
                  </Link>
                </li>
              )}
            />
          </Section>
        )}

        {progression && totalRead > 0 && (
          <Section icone={BookOpen} titre="Ce que j'ai lu">
            <div className="flex flex-col gap-4">
              {progression.lessons.length > 0 && (
                <div>
                  <p className="mb-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">Épreuves</p>
                  <ExpandableList
                    items={progression.lessons}
                    renderItem={(epreuve) => (
                      <li key={epreuve.id}>
                        <Link
                          // progression.lessons vient de getMyProgression() (endpoint access, non
                          // modifié) - toujours une Lesson classique.
                          to={epreuveReaderPath(epreuve.subject.country.code.toLowerCase(), epreuve.slug as string)}
                          className="flex items-center gap-2 rounded-xl border border-border bg-background/60 px-3.5 py-2 text-sm transition-colors hover:border-primary/40"
                        >
                          <CheckCircle2 className="size-3.5 shrink-0 text-success" />
                          <span className="truncate">{epreuve.title}</span>
                        </Link>
                      </li>
                    )}
                  />
                </div>
              )}

              {progression.cours.length > 0 && (
                <div>
                  <p className="mb-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">Cours</p>
                  <ExpandableList
                    items={progression.cours}
                    renderItem={(cours) => (
                      <li key={cours.id}>
                        <Link
                          to={coursReaderPath(cours.slug)}
                          className="flex items-center gap-2 rounded-xl border border-border bg-background/60 px-3.5 py-2 text-sm transition-colors hover:border-primary/40"
                        >
                          <CheckCircle2 className="size-3.5 shrink-0 text-success" />
                          <span className="truncate">{cours.titre}</span>
                        </Link>
                      </li>
                    )}
                  />
                </div>
              )}
            </div>
          </Section>
        )}

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

        <div className="flex justify-center pt-1">
          <Button variant="ghost" onClick={handleLogout} className="rounded-full text-muted-foreground hover:text-destructive">
            <LogOut className="size-4" />
            Se déconnecter
          </Button>
        </div>
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
