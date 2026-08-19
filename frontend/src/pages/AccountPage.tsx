import { useEffect, useState, type FormEvent, type ReactNode } from "react"
import { Link, useNavigate } from "react-router-dom"
import { CheckCircle2, Copy, Crown, FileText, Gift, MessageCircle, Pencil, Target } from "lucide-react"

import {
  downloadFicheCorrigePdf,
  downloadFicheSujetPdf,
  getMaitrise,
  getMyProgression,
  getWhatsAppStatus,
  listMyFiches,
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
  Fiche, InscriptionInedite, InscriptionRepetiteur, MaitriseTheme, Progression, Subscription, TentativeInediteListItem,
} from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { ConnexionMethodsCard } from "@/components/ConnexionMethodsCard"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { tauxBarClassName } from "@/lib/maitrise"
import { useSeo } from "@/lib/seo"
import { SITE_NAME } from "@/lib/site"
import { catalogueHomePath, coursReaderPath, epreuveReaderPath, epreuvesListPath } from "@/lib/countryPath"

// Au-delà de ce nombre, une liste (thèmes de maîtrise, lectures, tentatives, fiches)
// passe derrière un "voir plus" - voir ExpandableList. Un compte actif de longue date
// peut accumuler des dizaines de sessions de quiz ou de lectures ; les afficher toutes
// d'un bloc est la source concrète du "très touffu" signalé sur cette page, pas
// seulement les 7 cartes elles-mêmes.
const PREVIEW_COUNT = 5

/** Regroupe une liste plate de thèmes par matière, en gardant l'ordre déjà trié
 * (le plus faible d'abord) de quiz.services.maitrise_par_theme à l'intérieur de
 * chaque groupe. */
function groupBySubject(maitrise: MaitriseTheme[]): { subject_label: string; themes: MaitriseTheme[] }[] {
  const groups: { subject_label: string; themes: MaitriseTheme[] }[] = []
  for (const theme of maitrise) {
    const group = groups.find((g) => g.subject_label === theme.subject_label)
    if (group) group.themes.push(theme)
    else groups.push({ subject_label: theme.subject_label, themes: [theme] })
  }
  return groups
}

/**
 * Tronque une liste à PREVIEW_COUNT éléments avec un bouton "voir plus" - un composant
 * dédié plutôt qu'un hook appelé inline dans un .map() du parent (ex. un groupe de
 * matière par matière pour "Ma maîtrise") : les Hooks React ne peuvent pas être appelés
 * à l'intérieur d'une boucle du composant appelant, alors qu'une instance de composant
 * créée par .map() porte sans problème son propre état - chaque liste garde son
 * expansion indépendante des autres.
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
            className="text-xs font-medium text-primary hover:underline"
          >
            {expanded ? "Voir moins" : `Voir les ${items.length - previewCount} autres`}
          </button>
        </li>
      )}
    </ul>
  )
}

export function AccountPage() {
  useSeo({ title: "Mon compte" })

  const { user, logout, isAuthenticated, isLoading, updateUser } = useAuth()
  const { country } = useCountry()
  const navigate = useNavigate()
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [progression, setProgression] = useState<Progression | null>(null)
  const [maitrise, setMaitrise] = useState<MaitriseTheme[] | null>(null)
  const [tentativesInedites, setTentativesInedites] = useState<TentativeInediteListItem[] | null>(null)
  const [inscriptionsInedites, setInscriptionsInedites] = useState<InscriptionInedite[] | null>(null)
  const [fiches, setFiches] = useState<Fiche[] | null>(null)
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
    getMaitrise().then(setMaitrise)
    listMyTentativesInedites().then(setTentativesInedites)
    listMyInscriptionsInedites().then(setInscriptionsInedites)
    listMyFiches().then(setFiches)
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
  const whatsappMessage = `Salut ! Je révise sur ${SITE_NAME} (corrigés BEPC/Probatoire/BAC) - inscris-toi avec mon lien, ça nous donne 7 jours gratuits à tous les deux : ${referralLink}`

  function handleCopyLink() {
    navigator.clipboard.writeText(referralLink)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="mx-auto max-w-2xl animate-fade-up px-4 py-10">
      <h1 className="mb-6 font-display text-3xl font-semibold">Mon compte</h1>

      {/* Épinglé au-dessus des onglets - identité et déconnexion doivent rester
          atteignables en un coup d'œil, jamais cachées derrière un clic. */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          {isEditingProfile ? (
            <form onSubmit={handleSaveProfile} className="flex flex-col gap-4">
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
              {profileError && <p className="text-sm text-destructive">{profileError}</p>}
              <div className="flex gap-2">
                <Button type="submit" disabled={isSavingProfile}>
                  {isSavingProfile ? "Enregistrement..." : "Enregistrer"}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setIsEditingProfile(false)}
                  disabled={isSavingProfile}
                >
                  Annuler
                </Button>
              </div>
            </form>
          ) : (
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">{user.full_name || user.pseudo || user.phone_number}</p>
                <p className="text-sm text-muted-foreground">
                  {user.phone_number}
                  {user.pseudo && ` · @${user.pseudo}`}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon" onClick={startEditingProfile} aria-label="Modifier le profil">
                  <Pencil className="size-4" />
                </Button>
                <Button variant="outline" onClick={handleLogout}>
                  Déconnexion
                </Button>
              </div>
            </div>
          )}
          {!isEditingProfile && whatsappOptedIn !== null && (
            <div className="mt-4 flex items-center justify-between border-t border-border pt-4">
              <span className="flex items-center gap-2 text-sm">
                <MessageCircle className="size-4 shrink-0 text-muted-foreground" />
                Rappels de révision par WhatsApp
              </span>
              <Button size="sm" variant={whatsappOptedIn ? "outline" : "default"} onClick={handleToggleWhatsApp} disabled={whatsappLoading}>
                {whatsappOptedIn ? "Désactiver" : "Activer"}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <ConnexionMethodsCard />

      <Tabs defaultValue="abonnements">
        <TabsList>
          <TabsTrigger value="abonnements">Abonnements</TabsTrigger>
          <TabsTrigger value="activite">Activité</TabsTrigger>
          <TabsTrigger value="progression">Progression</TabsTrigger>
        </TabsList>

        <TabsContent value="abonnements" className="mt-4 flex flex-col gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 font-display text-lg">
                <Gift className="size-4.5 text-primary" />
                Parraine tes amis
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <p className="text-sm text-muted-foreground">
                Ton ami s'inscrit avec ton lien et souscrit un abonnement : vous recevez chacun 7 jours d'accès gratuit.
                {user.filleuls_count > 0 && (
                  <> Tu as déjà parrainé {user.filleuls_count} personne{user.filleuls_count > 1 ? "s" : ""}.</>
                )}
              </p>
              <div className="flex flex-col gap-2 sm:flex-row">
                <Button variant="outline" onClick={handleCopyLink} className="flex-1">
                  <Copy className="size-4" />
                  {copied ? "Lien copié !" : "Copier le lien"}
                </Button>
                <Button asChild className="flex-1">
                  <a
                    href={`https://wa.me/?text=${encodeURIComponent(whatsappMessage)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <MessageCircle className="size-4" />
                    Partager sur WhatsApp
                  </a>
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between font-display text-lg">
                Mes abonnements
                <Link to="/mes-paiements" className="text-xs font-normal text-primary hover:underline">
                  Suivre mes paiements Mobile Money
                </Link>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {subscriptions.length === 0 ? (
                <p className="text-sm text-muted-foreground">Aucun abonnement pour le moment.</p>
              ) : (
                <ul className="flex flex-col gap-3">
                  {subscriptions.map((sub) => (
                    <li
                      key={sub.id}
                      className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-border px-3 py-2.5 transition-colors hover:bg-accent/40"
                    >
                      <span className="flex flex-col">
                        <span className="text-sm">
                          {sub.cursus.examen_display}
                          {sub.cursus.series ? ` - Série ${sub.cursus.series.code}` : ""}
                        </span>
                        {sub.plan_name && (
                          <span className="text-xs text-muted-foreground">{sub.plan_name}</span>
                        )}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground">
                          Expire le {new Date(sub.expires_at).toLocaleDateString("fr-FR")}
                        </span>
                        <Badge variant={sub.is_active ? "success" : "outline"}>
                          {sub.is_active ? "Actif" : "Expiré"}
                        </Badge>
                        {!sub.is_active && (
                          <Button asChild size="sm" variant="outline">
                            <Link to={`/abonnement?cursus=${sub.cursus.id}`}>Se réabonner</Link>
                          </Button>
                        )}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between font-display text-lg">
                <span className="flex items-center gap-2">
                  <Crown className="size-4.5 text-gold" />
                  Épreuves Inédites
                </span>
                <Link
                  to={`${epreuvesListPath(country)}?origine=INEDITE`}
                  className="text-xs font-normal text-primary hover:underline"
                >
                  Voir les épreuves disponibles
                </Link>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {/* L'add-on Épreuves Inédites (InscriptionInedite) est un produit séparé de
                  l'abonnement classique (Subscription) - même un compte abonné peut n'avoir
                  aucun accès ici tant qu'il n'a pas pris l'add-on ou une formule Max qui
                  l'inclut (voir subscriptions.models.ProductType). Rendu explicite ici
                  plutôt que laissé implicite : source de confusion constatée. */}
              {!inscriptionsInedites || inscriptionsInedites.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  Aucun accès Épreuves Inédites pour l'instant - c'est un add-on séparé de l'abonnement classique
                  ci-dessus (inclus dans la formule Max, ou disponible seul).
                </p>
              ) : (
                <ul className="flex flex-col gap-2">
                  {inscriptionsInedites.map((inscription) => (
                    <li
                      key={inscription.id}
                      className="flex items-center justify-between rounded-md border border-border px-3 py-2 text-sm"
                    >
                      <span>
                        {inscription.cursus.examen_display}
                        {inscription.cursus.series ? ` - Série ${inscription.cursus.series.code}` : ""}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground">
                          Expire le {new Date(inscription.expires_at).toLocaleDateString("fr-FR")}
                        </span>
                        <Badge variant={inscription.is_active ? "success" : "outline"}>
                          {inscription.is_active ? "Actif" : "Expiré"}
                        </Badge>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between font-display text-lg">
                <span className="flex items-center gap-2">
                  <FileText className="size-4.5 text-primary" />
                  Fiches (répétiteurs)
                </span>
                <Link to="/fiches" className="text-xs font-normal text-primary hover:underline">
                  Générer une fiche
                </Link>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {/* L'add-on Fiches (InscriptionRepetiteur) est un produit séparé de
                  l'abonnement classique, même patron que l'add-on Épreuves Inédites
                  ci-dessus (voir sa note) - rendu explicite pour la même raison. */}
              {!inscriptionsRepetiteur || inscriptionsRepetiteur.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  Aucun accès Fiches pour l'instant - c'est un add-on séparé de l'abonnement classique ci-dessus,
                  réservé aux répétiteurs.
                </p>
              ) : (
                <ul className="flex flex-col gap-2">
                  {inscriptionsRepetiteur.map((inscription) => (
                    <li
                      key={inscription.id}
                      className="flex items-center justify-between rounded-md border border-border px-3 py-2 text-sm"
                    >
                      <span>
                        {inscription.cursus.examen_display}
                        {inscription.cursus.series ? ` - Série ${inscription.cursus.series.code}` : ""}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground">
                          Expire le {new Date(inscription.expires_at).toLocaleDateString("fr-FR")}
                        </span>
                        <Badge variant={inscription.is_active ? "success" : "outline"}>
                          {inscription.is_active ? "Actif" : "Expiré"}
                        </Badge>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="activite" className="mt-4 flex flex-col gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between font-display text-lg">
                <span className="flex items-center gap-2">
                  <Crown className="size-4.5 text-gold" />
                  Tentatives Épreuves Inédites
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {!tentativesInedites || tentativesInedites.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  Aucune épreuve inédite tentée pour l'instant -{" "}
                  <Link to={`${epreuvesListPath(country)}?origine=INEDITE`} className="text-primary hover:underline">
                    découvre les épreuves inédites
                  </Link>
                  .
                </p>
              ) : (
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
                        className="flex items-center justify-between gap-3 rounded-md border border-border px-3 py-2.5 text-sm transition-colors hover:bg-accent/40"
                      >
                        <span className="flex min-w-0 flex-col">
                          <span className="truncate">{tentative.epreuve_titre}</span>
                          <span className="text-xs text-muted-foreground">
                            {tentative.cursus_display} · {new Date(tentative.started_at).toLocaleDateString("fr-FR")}
                          </span>
                        </span>
                        {tentative.submitted_at ? (
                          <Badge variant={tentative.score_obtenu !== null && tentative.score_obtenu >= 50 ? "success" : "outline"}>
                            {tentative.score_obtenu}%
                          </Badge>
                        ) : (
                          <Badge variant="outline">En cours</Badge>
                        )}
                      </Link>
                    </li>
                  )}
                />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between font-display text-lg">
                <span className="flex items-center gap-2">
                  <FileText className="size-4.5 text-primary" />
                  Fiches générées
                </span>
                <Link to="/fiches" className="text-xs font-normal text-primary hover:underline">
                  Générer une fiche
                </Link>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {!fiches || fiches.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  Aucune fiche générée pour l'instant -{" "}
                  <Link to="/fiches" className="text-primary hover:underline">
                    compose ta première fiche
                  </Link>
                  .
                </p>
              ) : (
                <ExpandableList
                  items={fiches}
                  renderItem={(fiche) => (
                    <li
                      key={fiche.id}
                      className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-border px-3 py-2.5 text-sm"
                    >
                      <span className="flex min-w-0 flex-col">
                        <span className="truncate">{fiche.titre}</span>
                        <span className="text-xs text-muted-foreground">
                          {fiche.cursus_display} · {fiche.subject_label} ·{" "}
                          {new Date(fiche.created_at).toLocaleDateString("fr-FR")}
                        </span>
                      </span>
                      {fiche.statut === "PRETE" ? (
                        <div className="flex items-center gap-2">
                          <Button size="sm" variant="outline" onClick={() => downloadFicheSujetPdf(fiche.id)}>
                            Énoncé
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => downloadFicheCorrigePdf(fiche.id)}>
                            Corrigé
                          </Button>
                        </div>
                      ) : (
                        <Badge variant={fiche.statut === "ECHEC" ? "outline" : "success"}>
                          {fiche.statut === "ECHEC" ? "Échec" : "En cours"}
                        </Badge>
                      )}
                    </li>
                  )}
                />
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="progression" className="mt-4 flex flex-col gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 font-display text-lg">
                <Target className="size-4.5 text-primary" />
                Ma maîtrise
              </CardTitle>
            </CardHeader>
            <CardContent>
              {!maitrise || maitrise.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  Fais ton premier{" "}
                  <Link to="/quiz" className="text-primary hover:underline">
                    quiz
                  </Link>{" "}
                  pour voir apparaître ta maîtrise, thème par thème.
                </p>
              ) : (
                <div className="flex flex-col gap-5">
                  {groupBySubject(maitrise).map((group) => (
                    <div key={group.subject_label}>
                      <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                        {group.subject_label}
                      </p>
                      <ExpandableList
                        items={group.themes}
                        renderItem={(theme) => (
                          <li key={theme.theme_id} className="flex items-center gap-3">
                            <div className="flex min-w-0 flex-1 flex-col gap-1">
                              <div className="flex items-center gap-1.5">
                                <span className="truncate text-sm">{theme.theme}</span>
                                {theme.en_revision && (
                                  <Badge variant="outline" className="shrink-0 text-xs">
                                    À réviser
                                  </Badge>
                                )}
                              </div>
                              <div className="h-1.5 w-full overflow-hidden rounded-full bg-secondary">
                                <div
                                  className={`h-full rounded-full transition-all ${tauxBarClassName(theme.taux)}`}
                                  style={{ width: `${theme.taux}%` }}
                                />
                              </div>
                            </div>
                            <span className="w-10 shrink-0 text-right text-xs text-muted-foreground">{theme.taux}%</span>
                          </li>
                        )}
                      />
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="font-display text-lg">Ma progression</CardTitle>
            </CardHeader>
            <CardContent>
              {!progression || totalRead === 0 ? (
                <p className="text-sm text-muted-foreground">
                  Rien de lu pour l'instant - ouvre une épreuve ou un cours pour commencer.
                </p>
              ) : (
                <div className="flex flex-col gap-4">
                  <p className="text-sm text-muted-foreground">
                    {totalRead} contenu{totalRead > 1 ? "s" : ""} lu{totalRead > 1 ? "s" : ""} au total.
                  </p>

                  {progression.lessons.length > 0 && (
                    <div>
                      <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">Épreuves</p>
                      <ExpandableList
                        items={progression.lessons}
                        renderItem={(epreuve) => (
                          <li key={epreuve.id}>
                            <Link
                              // progression.lessons vient de getMyProgression() (endpoint
                              // access, non modifié) - toujours une Lesson classique.
                              to={epreuveReaderPath(epreuve.subject.country.code.toLowerCase(), epreuve.slug as string)}
                              className="flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm transition-colors hover:bg-accent/40"
                            >
                              <CheckCircle2 className="size-4 shrink-0 text-success" />
                              {epreuve.title}
                            </Link>
                          </li>
                        )}
                      />
                    </div>
                  )}

                  {progression.cours.length > 0 && (
                    <div>
                      <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">Cours</p>
                      <ExpandableList
                        items={progression.cours}
                        renderItem={(cours) => (
                          <li key={cours.id}>
                            <Link
                              to={coursReaderPath(cours.slug)}
                              className="flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm transition-colors hover:bg-accent/40"
                            >
                              <CheckCircle2 className="size-4 shrink-0 text-success" />
                              {cours.titre}
                            </Link>
                          </li>
                        )}
                      />
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
